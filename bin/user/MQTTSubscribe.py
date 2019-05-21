"""
WeeWX driver and service that subscribes to MQTT topics and
creates/updates loop packets/archive records.

Installation:
    Put this file in the bin/user directory.
    Update weewx.conf [MQTTSubscribeService] as needed to configure the service.
    Update weewx.conf [MQTTSubscribeDriver] as needed to configure the driver.
    Update weewx.conf [Accumulator] for any custom fields.

Overview:
    The MQTT loop_start is used to run a separate thread to manage the MQTT subscriptions.
    The payloads are put on a queue to be processed by the driver or service.

    The service binds to either the NEW_LOOP_PACKET or NEW_ARCHIVE_RECORD event. 
    On this event, it processes the queue of MQTT payloads and updates the packet or record

    The driver processes the queue and generates a packet for each element currently in the queue.
    A topic can be desinated as an 'archive topic'. Data in this topic is returned as an archive record.

Configuration:
[MQTTSubscribeService] or [MQTTSubscribeDriver]
    # The MQTT server.
    # Default is: localhost
    host = localhost

    # The port to connect to.
    # Default is: 1883
    port = 1883

    # Maximum period in seconds allowed between communications with the broker.
    # Default is: 60
    keepalive = 60

    # username for broker authentication.
    # Default is: None
    username =

    # password for broker authentication.
    # Default is: None
    password =

    # Controls the MQTT logging.
    # Default is: false
    log = false

    # Units for MQTT payloads without unit value. 
    # Valid values: US, METRIC, METRICWX
    # Default is: US
    unit_system = US

    # The clientid to connect with.
    # Service default is: MQTTSubscribeService-xxxx
    # Driver default is: MQTTSubscribeDriver-xxxx
    #    where xxxx is a random number between 1000 and 9999
    clientid =

    # The topic to subscribe to.
    # DEPRECATED - use [[topics]]
    topic =

    # Todo - think about default size
    # The maximum queue size.
    # When the queue is larger than this value, the oldest element is removed.
    # In general the queue should not grow large, but it might if the time 
    # between the driver creating packets is large and the MQTT broker publishes frequently.
    # Or if subscribing to 'individual' payloads with wildcards. This results in many topic
    # in a single queue.
    # Default is: six.MAXSIZE
    max_queue = six.MAXSIZE

    # Turn the service on and off.
    # Default is: true
    # Only used by the service.
    enable = false

    # The amount of time in seconds to overlap the start time when processing the MQTT queue.
    # When the time of the MQTT payload is less than the end time of the previous packet/record, 
    # the MQTT payload is ignored. When overlap is set, MQTT payloads within this number of seconds 
    # of the previous end time will be processed.
    # It is best to keep this 0 and only set it if 'Ignoring record outside of interval' messages are seen.
    # This option maybe removed in the future.
    # Default is: 0
    # Only used by the service.
    overlap = 0

    # The binding, loop or archive.
    # Default is: loop
    # Only used by the service.
    binding = loop

    # When the MQTT queue has no data, the amount of time in seconds to wait
    # before checking again.
    # Default is: 2
    # Only used by the driver
    wait_before_retry = 2

    # Payload in this topic is processed like an archive record.
    # Default is: None
    # Only used by the driver.
    archive_topic =

    # The message handler to use
    [[message_handler]]
        # The format of the MQTT payload.
        # Currently support: individual, json, keyword
        # Must be specified.
        type = REPLACE_ME

        # When True, the full topic (weather/outTemp) is used as the fieldname.
        # When false, the topic furthest to the right is used.
        # Valid values: True, False
        # Default is: False
        # Only used when type is 'individual'.

        # The delimiter between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is: ,
        keyword_delimiter = ,

        # The separator between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is: =
        keyword_separator = =

        # Mapping to WeeWX names.
        [[[label_map]]]
            temp1 = extraTemp1

    # The topics to subscribe to.
    [[topics]
        [[[first/topic]]]
        [[[second/one]]]
"""

from __future__ import with_statement
import six
import configobj
import syslog
import paho.mqtt.client as mqtt
import json
import random
import time
#import weeutil.weeutil
import weeutil
from weeutil.weeutil import to_bool, to_float, to_int, to_sorted_string
import weewx
import weewx.drivers
from weewx.engine import StdService
from collections import deque

VERSION='1.1.0rc26'
DRIVER_NAME = 'MQTTSubscribeDriver'
DRIVER_VERSION = VERSION

def logmsg(console, dst, prefix, msg):
    syslog.syslog(dst, '%s: %s' % (prefix, msg))
    if console:
        print('%s: %s' % (prefix, msg))

def logdbg(console, prefix, msg):
    logmsg(console, syslog.LOG_DEBUG, prefix, msg)

def loginf(console, prefix, msg):
    logmsg(console, syslog.LOG_INFO, prefix, msg)

def logerr(console, prefix, msg):
    logmsg(console, syslog.LOG_ERR, prefix, msg)

class CollectData:
    def __init__(self, fields):
        self.fields = fields
        self.data = {}

    def add_data(self, in_data):
        old_data = {}
        for field in self.fields:
            # ToDo - might be a better way to determine the fieldname
            if field in in_data:
                if field in self.data:
                    old_data = dict(self.data)
                    self.data = {}

                self.data[field] = in_data[field]
                self.data['usUnits'] = in_data['usUnits']
                self.data['dateTime'] = in_data['dateTime']
                return old_data

    def get_data(self):
        return self.data

class MessageCallbackFactory:
    def __init__(self, config, console=False):
        self.console = console
        self._setup_callbacks()
        self.type = config.get('type', None)
        self.keyword_delimiter = config.get('keyword_delimiter', ',')
        self.keyword_separator = config.get('keyword_separator', '=')
        self.label_map = config.get('label_map', {})
        self.full_topic_fieldname = to_bool(config.get('full_topic_fieldname', False))

        if self.type not in self.callbacks:
            raise ValueError("Invalid type configured: %s" % self.type)

    def get_callback(self):
        return self.callbacks[self.type]

    def _setup_callbacks(self):
        self.callbacks = {}
        self.callbacks['individual'] = self._on_message_individual
        self.callbacks['json'] = self._on_message_json
        self.callbacks['keyword'] = self._on_message_keyword

    def _byteify(self, data, ignore_dicts = False):
        # if this is a unicode string, return its string representation
        if isinstance(data, unicode):
            return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [ self._byteify(item, ignore_dicts=True) for item in data ]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            data2 = {}
            for key, value in data.items():
                key2 = self._byteify(key, ignore_dicts=True)
                # ToDo - better way to do mapping
                data2[self.label_map.get(key2,key2)] = self._byteify(value, ignore_dicts=True)
            return data2
        # if it's anything else, return it in its original form
        return data

    def _lookup_topic(self, topics, msg_topic):
        for topic in topics:
            if mqtt.topic_matches_sub(topic, msg_topic):
                return topic

    def _queue_size_check(self, queue, max_queue):
        while len(queue) >= max_queue:
            element = queue.popleft()
            logerr(self.console, "MQTTSubscribe", "Queue limit %i reached. Removing: %s" %(max_queue, element))        

    def _on_message_keyword(self, client, userdata, msg):
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            topics = userdata['topics']
            topic =self. _lookup_topic(topics, msg.topic)
            logdbg(self.console, "MQTTSubscribe", "For %s received: %s assigned to: %s" %(msg.topic, msg.payload, topic))            

            self._queue_size_check(topics[topic]['queue'], topics[topic]['max_queue'])

            fields = msg.payload.split(self.keyword_delimiter)
            data = {}
            for field in fields:
                eq_index = field.find(self.keyword_separator)
                # Ignore all fields that do not have the separator
                if eq_index == -1:
                    logerr(self.console, "MQTTSubscribe", "on_message_keyword failed to find separator: %s" % self.keyword_separator)
                    logerr(self.console, "MQTTSubscribe", "**** Ignoring field=%s " % field)
                    continue

                name = field[:eq_index].strip()
                value = field[eq_index + 1:].strip()
                data[self.label_map.get(name, name)] = to_float(value)

            if data:
                if 'dateTime' not in data:
                    data['dateTime'] = time.time()
                if 'usUnits' not in data:
                    data['usUnits'] = topics[topic]['unit_system']

                topics[topic]['queue'].append(data,)

                logdbg(self.console, "MQTTSubscribe", "Added to queue: %s" % to_sorted_string(data))
            else:
                logerr(self.console, "MQTTSubscribe", "on_message_keyword failed to find data in: topic=%s and payload=%s" % (msg.topic, msg.payload))
        except Exception as exception:
            logerr(self.console, "MQTTSubscribe", "on_message_keyword failed with: %s" % exception)
            logerr(self.console, "MQTTSubscribe", "**** Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))

    def _on_message_json(self, client, userdata, msg):
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            topics = userdata['topics']
            topic =self. _lookup_topic(topics, msg.topic)
            logdbg(self.console, "MQTTSubscribe", "For %s received: %s assigned to: %s" %(msg.topic, msg.payload, topic))            

            self._queue_size_check(topics[topic]['queue'], topics[topic]['max_queue'])

            # ToDo - better way?
            if six.PY2:
                data = self._byteify(
                    json.loads(msg.payload, object_hook=self._byteify),
                    ignore_dicts=True)
            else:
                data = json.loads(msg.payload.decode("utf-8"))

            if 'dateTime' not in data:
                data['dateTime'] = time.time()
            if 'usUnits' not in data:
                data['usUnits'] = topics[topic]['unit_system']

            topics[topic]['queue'].append(data,)

            logdbg(self.console, "MQTTSubscribe", "Added to queue: %s" % to_sorted_string(data))
        except Exception as exception:
            logerr(self.console, "MQTTSubscribe", "on_message_json failed with: %s" % exception)
            logerr(self.console, "MQTTSubscribe", "**** Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))

    def _on_message_individual(self, client, userdata, msg):
        wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            topics = userdata['topics']
            topic =self. _lookup_topic(topics, msg.topic)
            logdbg(self.console, "MQTTSubscribe", "For %s received: %s assigned to: %s" %(msg.topic, msg.payload, topic))

            self._queue_size_check(topics[topic]['queue'], topics[topic]['max_queue'])

            if self.full_topic_fieldname:
                key = msg.topic.encode('ascii', 'ignore') # ToDo - research
            else:
                tkey = msg.topic.rpartition('/')[2]
                key = tkey.encode('ascii', 'ignore') # ToDo - research

            fieldname = self.label_map.get(key,key)

            data = {}
            data['dateTime'] = time.time()
            data['usUnits'] = topics[topic]['unit_system']
            data[fieldname] = to_float(msg.payload)

            if fieldname in wind_fields:
                topics[topic]['queue_wind'].append(data,)
            else:
                topics[topic]['queue'].append(data,)
        except Exception as exception:
            logerr(self.console, "MQTTSubscribe", "on_message_individual failed with: %s" % exception)
            logerr(self.console, "MQTTSubscribe", "**** Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))

# Class to manage MQTT subscriptions
# If payload format that is not supported, subclass and implement on_message methos
class MQTTSubscribe():
    def __init__(self, service_dict):
        self.console = to_bool(service_dict.get('console', False))
        message_handler_config = service_dict.get('message_handler', None)
        if message_handler_config is None:
            raise ValueError("[[message_handler]] is required.")

        message_callback_factory = service_dict.get('message_callback_factory', 'user.MQTTSubscribe.MessageCallbackFactory')
        self.topics = self._create_topics(service_dict)
        clientid = service_dict.get('clientid',
                                'MQTTSubscribe-' + str(random.randint(1000, 9999)))

        host = service_dict.get('host', 'localhost')
        keepalive = to_int(service_dict.get('keepalive', 60))
        port = to_int(service_dict.get('port', 1883))
        username = service_dict.get('username', None)
        password = service_dict.get('password', None)
        log = to_bool(service_dict.get('log', False))

        self.archive_topic = service_dict.get('archive_topic', None)

        if self.archive_topic and self.archive_topic not in service_dict['topics']:
            raise ValueError("Archive topic %s must be in [[topics]]" % self.archive_topic)

        loginf(self.console, "MQTTSubscribe", "Console is %s" % self.console)
        loginf(self.console, "MQTTSubscribe", "Message handler config is %s" % message_handler_config)
        loginf(self.console, "MQTTSubscribe", "Message callback factory is %s" % message_callback_factory)
        loginf(self.console, "MQTTSubscribe", "Client id is %s" % clientid)
        loginf(self.console, "MQTTSubscribe", "MQTTSubscribe version is %s" % VERSION)
        loginf(self.console, "MQTTSubscribe", "Host is %s" % host)
        loginf(self.console, "MQTTSubscribe", "Port is %s" % port)
        loginf(self.console, "MQTTSubscribe", "Keep alive is %s" % keepalive)
        loginf(self.console, "MQTTSubscribe", "Username is %s" % username)
        if password is not None:
            loginf(self.console, "MQTTSubscribe", "Password is set")
        else:
            loginf(self.console, "MQTTSubscribe", "Password is not set")
        loginf(self.console, "MQTTSubscribe", "Archive topic is %s" % self.archive_topic)
        loginf(self.console, "MQTTSubscribe", "Topics are %s" % self.topics)

        self.logger = {
            mqtt.MQTT_LOG_INFO: loginf,
            mqtt.MQTT_LOG_NOTICE: loginf,
            mqtt.MQTT_LOG_WARNING: loginf,
            mqtt.MQTT_LOG_ERR: logerr,
            mqtt.MQTT_LOG_DEBUG: logdbg
        }

        userdata = {}
        userdata['topics'] = self.topics
        self.client = mqtt.Client(client_id=clientid, userdata=userdata)

        if log:
            self.client.on_log = self._on_log

        MessageCallbackFactory_class = weeutil.weeutil._get_object(message_callback_factory)
        messageCallBackFactory = MessageCallbackFactory_class(message_handler_config, self.console)

        self.client.on_message = messageCallBackFactory.get_callback()

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        if username is not None and password is not None:
            self.client.username_pw_set(username, password)

        self.client.connect(host, port, keepalive)

    @property
    def Topics(self):
      return self.topics

    # start subscribing to the topics
    def start(self):
        logdbg(self.console, "MQTTSubscribe", "Starting loop")
        self.client.loop_start()

    # shut it down
    def shutDown(self):
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        logdbg(self.console, "MQTTSubscribe", "Connected with result code %i" % rc)
        for topic in self.topics:
            client.subscribe(topic)

    def _on_disconnect(self, client, userdata, rc):
        logdbg(self.console, "MQTTSubscribe", "Disconnected with result code %i" %rc)

    def _on_log(self, client, userdata, level, msg):
        self.logger[level](self.console, "MQTTSubscribe/MQTT", msg)

    def _create_topics(self, config_dict):
        if 'topic' in config_dict and 'topics' in config_dict:
            raise ValueError("Cannot have both 'topic' and 'topics'. Please remove 'topic'.")

        unit_system_name = config_dict.get('unit_system', 'US').strip().upper()
        if unit_system_name not in weewx.units.unit_constants:
            raise ValueError("MQTTSubscribe: Unknown unit system: %s" % unit_system_name)
        unit_system = weewx.units.unit_constants[unit_system_name]

        if 'topic' in config_dict:
            topics = {}
            topics[config_dict['topic']] = {}
        else:
            topics = dict(config_dict['topics'])

        if not topics:
            raise ValueError("At least one [[topics]] must be specified.")

        for topic in topics:
            if 'topics' in config_dict and topic in config_dict['topics']:
                topic_dict = config_dict['topics'][topic]
            else:
                topic_dict = {}
            topics[topic]['queue'] = deque()
            topics[topic]['max_queue'] = topic_dict.get('max_queue',
                                                        config_dict.get('max_queue', six.MAXSIZE))
            topics[topic]['queue_wind'] = deque()
            topics[topic]['unit_system'] = unit_system

        return topics

class MQTTSubscribeService(StdService):
    def __init__(self, engine, config_dict):
        super(MQTTSubscribeService, self).__init__(engine, config_dict)

        service_dict = config_dict.get('MQTTSubscribeService', {})
        self.console = to_bool(service_dict.get('console', False))
        self.enable =  to_bool(service_dict.get('enable', True))
        if not self.enable:
            loginf(self.console, "MQTTSubscribeService", "Service is not enabled, exiting.")
            return

        self.overlap = to_float(service_dict.get('overlap', 0))
        binding = service_dict.get('binding', 'loop')

        loginf(self.console, "MQTTSubscribeService", "Binding is %s" % binding)
        loginf(self.console, "MQTTSubscribeService", "Overlap is %s" % self.overlap)

        if 'archive_topic' in service_dict:
          raise ValueError("archive_topic, %s, is invalid when running as a service" % service_dict['archive_topic'])

        self.end_ts = 0 # prime for processing loop packet
        self.wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

        self.manager = MQTTSubscribe(service_dict)
        self.manager.start()

        if (binding == 'archive'):
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        elif (binding == 'loop'):
            self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        else:
            raise ValueError("MQTTSubscribeService: Unknown binding: %s" % binding)

    def shutDown(self):
        self.manager.shutDown()

    def _process_data(self, topic, start_ts, end_ts, record):
        queue = topic['queue']
        queue_wind = topic['queue_wind']
        logdbg(self.console, "MQTTSubscribeService", "Processing interval: %f %f" %(start_ts, end_ts))
        accumulator = weewx.accum.Accum(weeutil.weeutil.TimeSpan(start_ts, end_ts))

        logdbg(self.console, "MQTTSubscribeService", "Queue size is: %i" % len(queue))
        while (len(queue) > 0 and queue[0]['dateTime'] <= end_ts):
            archive_data = queue.popleft()
            logdbg(self.console, "MQTTSubscribeService", "Processing: %s" % to_sorted_string(archive_data))
            try:
                logdbg(self.console, "MQTTSubscribeService", "Data to accumulate: %s" % to_sorted_string(archive_data))
                accumulator.addRecord(archive_data)
            except weewx.accum.OutOfSpan:
                loginf(self.console, "MQTTSubscribeService", "Ignoring record outside of interval %f %f %f %s"
                    %(start_ts, end_ts, archive_data['dateTime'], to_sorted_string(archive_data)))

        collector = CollectData(self.wind_fields)
        logdbg(self.console, "MQTTSubscribeService", "Wind queue size is: %i" % len(queue_wind))
        while (len(queue_wind) > 0 and queue_wind[0]['dateTime'] <= end_ts):
            archive_data = queue_wind.popleft()
            logdbg(self.console, "MQTTSubscribeService", "Processing: %s" % to_sorted_string(archive_data))            
            try:
                data = collector.add_data(archive_data)
                if data:
                    logdbg(self.console, "MQTTSubscribeService", "Data to accumulate: %s" % to_sorted_string(data))
                    accumulator.addRecord(data)
            except weewx.accum.OutOfSpan:
                loginf(self.console, "MQTTSubscribeService", "Ignoring record outside of interval %f %f %f %s"
                    %(start_ts, end_ts, archive_data['dateTime'], to_sorted_string(archive_data)))            

        wind_data = collector.get_data()
        if wind_data:
            logdbg(self.console, "MQTTSubscribeService", "Data to accumulate post loop: %s" % to_sorted_string(wind_data))
            try:
                accumulator.addRecord(wind_data)
            except weewx.accum.OutOfSpan:
                loginf(self.console, "MQTTSubscribeService", "Ignoring record outside of interval %f %f %f %s"
                    %(start_ts, end_ts, archive_data['dateTime'], to_sorted_string(archive_data)))

        target_data = {}
        if not accumulator.isEmpty:
            aggregate_data = accumulator.getRecord()
            logdbg(self.console, "MQTTSubscribeService", "Data prior to conversion is: %s" % to_sorted_string(aggregate_data))
            target_data = weewx.units.to_std_system(aggregate_data, record['usUnits'])
            logdbg(self.console, "MQTTSubscribeService", "Data after to conversion is: %s" % to_sorted_string(target_data))
            logdbg(self.console, "MQTTSubscribeService", "Record prior to update is: %s" % to_sorted_string(record))
        else:
            logdbg(self.console, "MQTTSubscribeService", "Queue was empty")

        return target_data

    def new_loop_packet(self, event):
        start_ts = self.end_ts - self.overlap
        self.end_ts = event.packet['dateTime']
        for tp in self.manager.Topics:
            topic = self.manager.Topics[tp]
            target_data = self._process_data(topic, start_ts, self.end_ts, event.packet)
            event.packet.update(target_data)
            logdbg(self.console, "MQTTSubscribeService", "Packet after update is: %s" % to_sorted_string(event.packet))

    # this works for hardware generation, but software generation does not 'quality control'
    # the archive record, so this data is not 'QC' in this case.
    # If this is important, bind to the loop packet.
    def new_archive_record(self, event):
        end_ts = event.record['dateTime']
        start_ts = end_ts - event.record['interval'] * 60 - self.overlap
        for tp in self.manager.Topics:
            topic = self.manager.Topics[tp]
            target_data = self._process_data(topic, start_ts, end_ts, event.record)
            event.record.update(target_data)
            logdbg(self.console, "MQTTSubscribeService", "Record after update is: %s" % to_sorted_string(event.record))

def loader(config_dict, engine):
    return MQTTSubscribeDriver(**config_dict[DRIVER_NAME])

def confeditor_loader():
    return MQTTSubscribeDriverConfEditor()

class MQTTSubscribeDriver(weewx.drivers.AbstractDevice):
    """weewx driver that reads data from MQTT"""

    def __init__(self, **stn_dict):
      self.console = to_bool(stn_dict.get('console', False))
      self.wait_before_retry = float(stn_dict.get('wait_before_retry', 2))
      self.archive_topic = stn_dict.get('archive_topic', None)

      loginf(self.console, "MQTTSubscribeDriver", "Wait before retry is %i" % self.wait_before_retry)

      self.wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

      self.manager = MQTTSubscribe(stn_dict)
      self.manager.start()

    @property
    def hardware_name(self):
        return "MQTTSubscribeDriver"

    def genLoopPackets(self):
      while True:
        for topic in self.manager.Topics:
            if topic == self.archive_topic:
                continue
                
            queue = self.manager.Topics[topic]['queue']
            logdbg(self.console, "MQTTSubscribeDriver", "Queue is size %i" % len(queue))
            while len(queue) > 0:
                packet = queue.popleft()
                logdbg(self.console, "MQTTSubscribeDriver", "Packet: %s" % to_sorted_string(packet))
                yield packet
 
            queue_wind = self.manager.Topics[topic]['queue_wind']
            logdbg(self.console, "MQTTSubscribeDriver", "Wind queue is size %i" % len(queue_wind))

            collector = CollectData(self.wind_fields)
            while len(queue_wind) > 0:
                packet = queue_wind.popleft()
                data = collector.add_data(packet)
                if data:
                    logdbg(self.console, "MQTTSubscribeDriver", "Packet: %s" % to_sorted_string(data))
                    yield data
                    
            wind_data = collector.get_data()
            if wind_data:
                logdbg(self.console, "MQTTSubscribeDriver", "Packet post loop: %s" % to_sorted_string(wind_data))
                yield wind_data
            logdbg(self.console, "MQTTSubscribeDriver", "Queues are empty.")
        time.sleep(self.wait_before_retry)

    def genArchiveRecords(self, lastgood_ts):
        if not self.archive_topic:
            logdbg(self.console, "MQTTSubscribeDriver", "No archive topic configured.")
            raise NotImplementedError
        else:
            queue = self.manager.Topics[self.archive_topic]['queue']
            logdbg(self.console, "MQTTSubscribeDriver", "Archive queue is size %i and date is %f." %(len(queue), lastgood_ts))
            while (len(queue) > 0 and queue[0]['dateTime'] <= lastgood_ts):
                archive_record = queue.popleft()
                logdbg(self.console, "MQTTSubscribeDriver", "Archive record: %s" % to_sorted_string(archive_record))
                yield archive_record

class MQTTSubscribeDriverConfEditor(weewx.drivers.AbstractConfEditor): # pragma: no cover
    @property
    def default_stanza(self):
        return """
[MQTTSubscribeDriver]
    # This section is for the MQTTSubscribe driver.

    # The driver to use:
    driver = user.MQTTSubscribe

    # The MQTT server.
    # Default is: localhost
    host = localhost

    # The port to connect to.
    # Default is: 1883
    port = 1883

    # Maximum period in seconds allowed between communications with the broker.
    # Default is: 60
    keepalive = 60

    # Units for MQTT payloads without unit value.
    # Valid values: US, METRIC, METRICWX
    # Default is: US
    unit_system = US

    # The message handler to use
    [[message_handler]]
        # The format of the MQTT payload.
        # Currently support: individual, json, keyword
        # Must be specified.
        type = REPLACE_ME

    # The topics to subscribe to.
    [[topics]]
        [[[FIRST/REPLACE_ME]]]
        [[[SECOND/REPLACE_ME]]]
"""
    def prompt_for_settings(self):
        settings = {}
        settings['message_handler'] = {}

        print("Enter the host.")
        settings['host'] = self._prompt('host', 'localhost')

        print("Enter the port on the host.")
        settings['port'] = self._prompt('port', '1883')

        print("Enter the maximum period in seconds allowed between communications with the broker.")
        settings['keepalive'] = self._prompt('keepalive', '60')

        print("Enter the units for MQTT payloads without unit value: US|METRIC|METRICWX")
        settings['unit_system'] = self._prompt('unit_system', 'US', ['US', 'METRIC', 'METRICWX'])

        print("Enter the MQTT paylod type: individual|json|keyword")
        settings['message_handler']['type'] = self._prompt('type', 'json', ['individual', 'json', 'keyword'])

        return settings

# To Run
# setup.py install:
# PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/MQTTSubscribe.py
#
# rpm or deb package install:
# PYTHONPATH=/usr/share/weewx python /usr/share/weewx/user/MQTTSubscribe.py
if __name__ == '__main__': # pragma: no cover
    import optparse
    import os
    import sys
    from weewx.engine import StdEngine

    usage = """MQTTSubscribeService --help
           wee_config CONFIG_FILE
               [--records=RECORD_COUNT]
               [--interval=INTERVAL]
               [--delay=DELAY]
               [--units=US|METRIC|METRICWX]
               [--binding=archive|loop]
               [--type=driver|service]
               [--verbose]
               [--console]
    """

    def main():
        parser = optparse.OptionParser(usage=usage)
        parser.add_option('--records', dest='record_count', type=int,
                        help='The number of archive records to create.',
                        default=2)
        parser.add_option('--interval', dest='interval', type=int,
                        help='The archive interval in seconds.',
                        default=300)
        parser.add_option('--delay', dest='delay', type=int,
                        help='The archive delay in seconds.',
                        default=15)
        parser.add_option("--units", choices=["US", "METRIC", "METRICWX"],
                        help="The default units if not in MQTT payload.",
                        default="US")
        parser.add_option("--binding", choices=["archive", "loop"],
                        help="The type of binding.",
                        default="archive")
        parser.add_option("--type", choices=["driver", "service"],
                        help="The simulation type.",
                        default="driver")
        parser.add_option("--verbose", action="store_true", dest="verbose",
                        help="Log extra output (debug=1).")
        parser.add_option("--console", action="store_true", dest="console",
                        help="Log to console in addition to syslog.")

        (options, args) = parser.parse_args()

        simulation_type = options.type
        binding = options.binding
        record_count = options.record_count
        interval = options.interval
        delay = options.delay
        units= weewx.units.unit_constants[options.units]

        syslog.openlog('wee_MQTTSS', syslog.LOG_PID | syslog.LOG_CONS)
        if options.verbose:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
        else:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

        config_path = os.path.abspath(args[0])

        config_dict = configobj.ConfigObj(config_path, file_error=True)

        min_config_dict = {
            'Station': {
                'altitude': [0, 'foot'],
                'latitude': 0,
                'station_type': 'Simulator',
                'longitude': 0
            },
            'Simulator': {
                'driver': 'weewx.drivers.simulator',
            },
            'Engine': {
                'Services': {}
            }
        }

        print("Simulation is %s" % simulation_type)
        print("Creating %i %s records" % (record_count, binding))
        print("Interval is %i seconds" % interval)
        print("Delay is %i seconds" % delay)

        engine = StdEngine(min_config_dict)

        weewx.accum.initialize(config_dict)

        # override the configured binding with the parameter value
        weeutil.weeutil.merge_config(config_dict,
                                    {'MQTTSubscribeService': {'binding': binding}})

        # if specified, override the console logging
        if options.console:
            weeutil.weeutil.merge_config(config_dict,
                                     {'MQTTSubscribeService': {'console': True}})
            weeutil.weeutil.merge_config(config_dict,
                                     {'MQTTSubscribeDriver': {'console': True}})

        if simulation_type =="service":
            simulate_service(engine, config_dict, binding, record_count, interval, delay, units)
        elif simulation_type == "driver":
            driver = "user.MQTTSubscribe"
            __import__(driver)
            # This is a bit of Python wizardry. First, find the driver module
            # in sys.modules.
            driver_module = sys.modules[driver]
            # Find the function 'loader' within the module:
            loader_function = getattr(driver_module, 'loader')
            driver = loader_function(config_dict, engine)

            if binding == "archive":
                simulate_driver_archive(driver, record_count, interval, delay)
            elif binding == "loop":
                simulate_driver_packet(driver, record_count)

    def simulate_driver_archive(driver, record_count, interval, delay):
        i = 0
        while i < record_count:
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval
            end_delay_ts  =  end_period_ts + delay
            sleep_amount = end_delay_ts - current_time
            print("Sleeping %i seconds" % sleep_amount)
            time.sleep(sleep_amount)

            for record in driver.genArchiveRecords(end_period_ts):
                print("Record is: %s" % to_sorted_string(record))

            i += 1

    def simulate_driver_packet(driver, record_count):
        i = 0
        for packet in driver.genLoopPackets():
            print("Packet is: %s" % to_sorted_string(packet))
            i += 1
            if i >= record_count:
                break

    def simulate_service(engine, config_dict, binding, record_count, interval, delay, units):
        service = MQTTSubscribeService(engine, config_dict)
        i = 0
        while i < record_count:
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval
            end_delay_ts  =  end_period_ts + delay
            sleep_amount = end_delay_ts - current_time

            print("Sleeping %i seconds" % sleep_amount)
            time.sleep(sleep_amount)

            data = {}
            data['dateTime'] = end_period_ts
            data['usUnits'] = units

            if binding == 'archive':
                data['interval'] = interval / 60
                new_archive_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                            record=data,
                                                            origin='hardware')
                engine.dispatchEvent(new_archive_record_event)
                print("Archive Record is: %s" % to_sorted_string(new_archive_record_event.record))
            elif binding == 'loop':
                new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                        packet=data)
                engine.dispatchEvent(new_loop_packet_event)
                print("Loop packet is: %s" % to_sorted_string(new_loop_packet_event.packet))
            else:
                pass

            i += 1

        service.shutDown()

    main()
