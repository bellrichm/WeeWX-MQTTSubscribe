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

    # The clientid to connect with.
    # Service default is: MQTTSubscribeService-xxxx
    # Driver default is: MQTTSubscribeDriver-xxxx
    #    where xxxx is a random number between 1000 and 9999
    clientid =

    # The topic to subscribe to.
    # DEPRECATED - use [[topics]]
    topic =

    # Turn the service on and off.
    # Default is: true
    # Only used by the service.
    enable = false

    # The amount of time in seconds to overlap the start time when processing the MQTT queue.
    # When the time of the MQTT payload is less than the end time of the previous packet/record,
    # the MQTT payload is ignored. When overlap is set, MQTT payloads within this number of seconds
    # of the previous end time will be processed.
    # Default is: 0
    # Only used by the service.
    # DEPRECATED  - use adjust_start_time
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

    # Configuration for the message callback.
    [[message_callback]]
        # The format of the MQTT payload.
        # Currently support: individual, json, keyword
        # Must be specified.
        type = REPLACE_ME

        # When True, the full topic (weather/outTemp) is used as the fieldname.
        # When false, the topic furthest to the right is used.
        # Valid values: True, False
        # Default is: False
        # Only used when type is 'individual'.

        # When the json is nested, the delimiter between the hierarchies.
        # Default is: _
        flatten_delimiter = _

        # The delimiter between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is: ,
        keyword_delimiter = ,

        # The separator between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is: =
        keyword_separator = =

        # List of fields that are cumulative values
        # Default is: [] (empty list)
        contains_total =

        # Mapping to WeeWX names.
        [[[label_map]]]
            temp1 = extraTemp1

    # The topics to subscribe to.
    [[topics]
        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX
        # Default is: US
        unit_system = US

        # Even if the payload has a datetime, ignore it and use the server datetime
        # Default is False
        use_server_datetime = False

        # When True, the MQTT datetime will be not be checked that is greater than the last packet processed.
        # Default is False
        # Only used by the service.
        ignore_start_time = False

        # When the True, the MQTT data will continue to be processed even if its datetime is greater than the packet's datetime.
        # Default is False
        # Only used by the service.
        ignore_end_time = False

        # Allow MQTT data with a datetime this many seconds prior to the previous packet's datetime
        # to be added to the current packet.
        # Default is 0
        # Only used by the service.
        adjust_start_time = 0

        # Allow MQTT data with a datetime this many seconds after the current packet's datetime
        # to be added to the current packet.
        # Default is 0
        # Only used by the service.
        adjust_end_time = 0

        # The maximum queue size.
        # When the queue is larger than this value, the oldest element is removed.
        # In general the queue should not grow large, but it might if the time
        # between the driver creating packets is large and the MQTT broker publishes frequently.
        # Or if subscribing to 'individual' payloads with wildcards. This results in many topic
        # in a single queue.
        # Default is: sys.maxsize for python 3 and sys.maxint for python 2
        max_queue = MAXSIZE

        [[[first/topic]]]
        [[[second/one]]]
"""

from __future__ import with_statement
from __future__ import print_function
import datetime
import json
import locale
import platform
import random
import re
import sys
import time
from collections import deque

import configobj
import paho.mqtt.client as mqtt

import weewx
import weewx.drivers
from weewx.engine import StdService
import weeutil
from weeutil.weeutil import option_as_list, to_bool, to_float, to_int, to_sorted_string

# Stole from six module. Added to eliminate dependency on six when running under WeeWX 3.x
PY2 = sys.version_info[0] == 2
if PY2:
    MAXSIZE = sys.maxint # (only a python 3 error) pylint: disable=no-member
else:
    MAXSIZE = sys.maxsize

try:
    import weeutil.logger
    import logging
    def setup_logging(logging_level):
        if logging_level:
            weewx.debug = logging_level

        weeutil.logger.setup('wee_MQTTSS', {})

        log = logging.getLogger(__name__)

        log.info("Initializing weewx version %s", weewx.__version__)
        log.info("Using Python %s", sys.version)
        log.info("Platform %s", platform.platform())
        log.info("Locale is '%s'", locale.setlocale(locale.LC_ALL))

    class Logger(object):
        """ The logging class. """
        def __init__(self, console=None):
            self.console = console
            self._logmsg = logging.getLogger(__name__)

        def debug(self, msg):
            """ Log debug messages. """
            self._logmsg.debug(msg)

        def info(self, msg):
            """ Log informational messages. """
            self._logmsg.info(msg)

        def error(self, msg):
            """ Log error messages. """
            self._logmsg.error(msg)
except ImportError:
    import syslog
    def setup_logging(logging_level):
        syslog.openlog('wee_MQTTSS', syslog.LOG_PID | syslog.LOG_CONS)
        if logging_level:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
        else:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

        syslog.syslog(syslog.LOG_INFO, "wee_MQTTSS: Initializing weewx version %s" % weewx.__version__)
        syslog.syslog(syslog.LOG_INFO, "wee_MQTTSS: Using Python %s" % sys.version)
        syslog.syslog(syslog.LOG_INFO, "wee_MQTTSS: Platform %s" % platform.platform())
        syslog.syslog(syslog.LOG_INFO, "wee_MQTTSS: Locale is '%s'" % locale.setlocale(locale.LC_ALL))

    class Logger(object):
        """ The logging class. """
        def __init__(self, console=None):
            self.console = console

        def debug(self, msg):
            """ Log debug messages. """
            self._logmsg(syslog.LOG_DEBUG, msg)

        def info(self, msg):
            """ Log informational messages. """
            self._logmsg(syslog.LOG_INFO, msg)

        def error(self, msg):
            """ Log error messages. """
            self._logmsg(syslog.LOG_ERR, msg)

        def _logmsg(self, dst, msg):
            syslog.syslog(dst, '%s: %s' % (__name__, msg))
            if self.console:
                print('%s: %s' % (__name__, msg))

VERSION = '1.4.1-rc01'
DRIVER_NAME = 'MQTTSubscribeDriver'
DRIVER_VERSION = VERSION

# pylint: disable=fixme

class CollectData(object):
    """ Manage fields that are 'grouped together', like wind data. """
    def __init__(self, fields):
        self.fields = fields
        self.data = {}

    def add_data(self, in_data):
        """ Add data to the collection and return old collection if this field is already in the collection. """
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
        """ Return the collection. """
        return self.data

class TopicManager(object):
    """ Manage the MQTT topic subscriptions. """
    def __init__(self, config, logger):
        self.logger = logger

        if not config.sections:
            raise ValueError("At least one topic must be configured.")

        self.logger.info("TopicManager config is %s" % config)

        default_qos = to_int(config.get('qos', 0))
        default_use_server_datetime = to_bool(config.get('use_server_datetime', False))
        default_ignore_start_time = to_bool(config.get('ignore_start_time', False))
        default_ignore_end_time = to_bool(config.get('ignore_end_time', False))
        overlap = to_float(config.get('overlap', 0)) # Backwards compatibility
        default_adjust_start_time = to_float(config.get('adjust_start_time', overlap))
        default_adjust_end_time = to_float(config.get('adjust_end_time', 0))
        default_datetime_format = config.get('datetime_format', None)
        default_offset_format = config.get('offset_format', None)

        default_unit_system_name = config.get('unit_system', 'US').strip().upper()
        if default_unit_system_name not in weewx.units.unit_constants:
            raise ValueError("MQTTSubscribe: Unknown unit system: %s" % default_unit_system_name)
        unit_system = weewx.units.unit_constants[default_unit_system_name]

        max_queue = config.get('max_queue', MAXSIZE)

        self.wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

        self.topics = {}
        self.subscribed_topics = {}

        for topic in config.sections:
            topic_dict = config.get(topic, {})

            qos = to_int(topic_dict.get('qos', default_qos))
            use_server_datetime = to_bool(topic_dict.get('use_server_datetime',
                                                         default_use_server_datetime))
            ignore_start_time = to_bool(topic_dict.get('ignore_start_time', default_ignore_start_time))
            ignore_end_time = to_bool(topic_dict.get('ignore_end_time', default_ignore_end_time))
            adjust_start_time = to_float(topic_dict.get('adjust_start_time', default_adjust_start_time))
            adjust_end_time = to_float(topic_dict.get('adjust_end_time', default_adjust_end_time))
            datetime_format = topic_dict.get('datetime_format', default_datetime_format)
            offset_format = topic_dict.get('offset_format', default_offset_format)

            unit_system_name = topic_dict.get('unit_system', default_unit_system_name).strip().upper()
            if unit_system_name not in weewx.units.unit_constants:
                raise ValueError("MQTTSubscribe: Unknown unit system: %s" % unit_system_name)
            unit_system = weewx.units.unit_constants[unit_system_name]

            self.subscribed_topics[topic] = {}
            self.subscribed_topics[topic]['unit_system'] = unit_system
            self.subscribed_topics[topic]['qos'] = qos
            self.subscribed_topics[topic]['use_server_datetime'] = use_server_datetime
            self.subscribed_topics[topic]['ignore_start_time'] = ignore_start_time
            self.subscribed_topics[topic]['ignore_end_time'] = ignore_end_time
            self.subscribed_topics[topic]['adjust_start_time'] = adjust_start_time
            self.subscribed_topics[topic]['adjust_end_time'] = adjust_end_time
            self.subscribed_topics[topic]['datetime_format'] = datetime_format
            self.subscribed_topics[topic]['offset_format'] = offset_format
            self.subscribed_topics[topic]['max_queue'] = topic_dict.get('max_queue', max_queue)
            self.subscribed_topics[topic]['queue'] = deque()
            self.subscribed_topics[topic]['queue_wind'] = deque()

    def append_data(self, topic, in_data, fieldname=None):
        """ Add the MQTT data to the queue. """
        data = dict(in_data)
        payload = {}
        payload['wind_data'] = False
        if fieldname in self.wind_fields:
            payload['wind_data'] = True

        queue = self._get_queue(topic)
        use_server_datetime = self._get_value('use_server_datetime', topic)

        self._queue_size_check(queue, self._get_max_queue(topic))

        if 'dateTime' not in data or use_server_datetime:
            data['dateTime'] = time.time()
        if 'usUnits' not in data:
            data['usUnits'] = self._get_unit_system(topic)

        datetime_format = self._get_value('datetime_format', topic)
        if datetime_format and 'dateTime' in data:
            data['dateTime'] = self._to_epoch(data['dateTime'], datetime_format, self._get_value('offset_format', topic))

        self.logger.debug("TopicManager Added to queue %s %s %s: %s"
                          %(topic, self._lookup_topic(topic),
                            weeutil.weeutil.timestamp_to_string(data['dateTime']), to_sorted_string(data)))
        payload['data'] = data
        queue.append(payload,)

    def peek_datetime(self, topic):
        """ Return the date/time of the first element in the queue. """
        queue = self._get_queue(topic)
        self.logger.debug("TopicManager queue size is: %i" % len(queue))
        datetime_value = None
        if queue:
            datetime_value = queue[0]['data']['dateTime']

        return datetime_value

    def peek_last_datetime(self, topic):
        """ Return the date/time of the last element in the queue. """
        queue = self._get_queue(topic)
        self.logger.debug("TopicManager queue size is: %i" % len(queue))
        datetime_value = 0
        if queue:
            datetime_value = queue[-1]['data']['dateTime']

        return datetime_value

    def get_data(self, topic, end_ts=MAXSIZE):
        """ Get data off the queue of MQTT data. """
        queue = self._get_queue(topic)
        self.logger.debug("TopicManager starting queue %s size is: %i" %(topic, len(queue)))
        collector = CollectData(self.wind_fields)
        while queue:
            if queue[0]['data']['dateTime'] > end_ts:
                self.logger.debug("TopicManager leaving queue: %s size: %i content: %s" %(topic, len(queue), queue[0]))
                break
            payload = queue.popleft()
            wind_data = payload['wind_data']
            if wind_data:
                self.logger.debug("TopicManager processing wind data.")
                temp_data = payload['data']
                data = collector.add_data(temp_data)
            else:
                data = payload['data']
            if data:
                self.logger.debug("TopicManager retrieved queue %s %s: %s"
                                  %(topic, weeutil.weeutil.timestamp_to_string(data['dateTime']), to_sorted_string(data)))
                yield data

        data = collector.get_data()
        if data:
            self.logger.debug("TopicManager retrieved wind queue final %s %s: %s"
                              %(topic, weeutil.weeutil.timestamp_to_string(data['dateTime']), to_sorted_string(data)))
            yield data

    def get_accumulated_data(self, topic, start_time, end_time, units):
        """ Get the MQTT data after being accumulated. """
        ignore_start_time = self._get_value('ignore_start_time', topic)
        ignore_end_time = self._get_value('ignore_end_time', topic)
        adjust_start_time = self._get_value('adjust_start_time', topic)
        adjust_end_time = self._get_value('adjust_end_time', topic)

        if ignore_start_time:
            self.logger.debug("Service ignoring start time.")
            start_ts = self.peek_datetime(topic) - adjust_start_time
        else:
            start_ts = start_time - adjust_start_time

        if ignore_end_time:
            self.logger.debug("Service ignoring end time.")
            end_ts = self.peek_last_datetime(topic) + adjust_end_time
        else:
            end_ts = end_time + adjust_end_time

        self.logger.debug("Service processing interval: %f %f" %(start_ts, end_ts))
        accumulator = weewx.accum.Accum(weeutil.weeutil.TimeSpan(start_ts, end_ts))

        for data in self.get_data(topic, end_ts):
            if data:
                try:
                    self.logger.debug("Service data to accumulate: %s %s"
                                      % (weeutil.weeutil.timestamp_to_string(data['dateTime']), to_sorted_string(data)))
                    accumulator.addRecord(data)
                except weewx.accum.OutOfSpan:
                    self.logger.info("Service ignoring record outside of interval %f %f %f %s"
                                     %(start_ts, end_ts, data['dateTime'], (to_sorted_string(data))))
            else:
                break

        target_data = {}
        if not accumulator.isEmpty:
            aggregate_data = accumulator.getRecord()
            self.logger.debug("Service data prior to conversion is: %s %s"
                              % (weeutil.weeutil.timestamp_to_string(aggregate_data['dateTime']), to_sorted_string(aggregate_data)))
            target_data = weewx.units.to_std_system(aggregate_data, units)
            self.logger.debug("Service data after to conversion is: %s %s"
                              % (weeutil.weeutil.timestamp_to_string(target_data['dateTime']), to_sorted_string(target_data)))
        else:
            self.logger.debug("Dervice queue was empty")

        # Force dateTime to packet's datetime so that the packet datetime is not updated to the MQTT datetime
        if ignore_end_time:
            target_data['dateTime'] = end_time

        return target_data

    def _queue_size_check(self, queue, max_queue):
        while len(queue) >= max_queue:
            element = queue.popleft()
            self.logger.error("TopicManager queue limit %i reached. Removing: %s" %(max_queue, element))

    def get_qos(self, topic):
        """ Get the QOS. """
        return self._get_value('qos', topic)

    def _get_unit_system(self, topic):
        return self._get_value('unit_system', topic)

    def _get_max_queue(self, topic):
        return self._get_value('max_queue', topic)

    def _get_queue(self, topic):
        return self._get_value('queue', topic)

    def _get_wind_queue(self, topic):
        return self._get_value('queue_wind', topic)

    def _get_value(self, value, topic):
        subscribed_topic = self._lookup_topic(topic)
        return self.subscribed_topics[subscribed_topic][value]

    def _lookup_topic(self, topic):
        if topic in self.topics:
            return self.topics[topic]

        for subscribed_topic in self.subscribed_topics:
            if mqtt.topic_matches_sub(subscribed_topic, topic):
                self.topics[topic] = subscribed_topic
                return subscribed_topic

    def _to_epoch(self, datetime_input, datetime_format, offset_format=None):
        self.logger.debug("TopicManager datetime conversion datetime_input:%s datetime_format:%s offset_format:%s"
                          %(datetime_input, datetime_format, offset_format))
        if offset_format:
            offset_start = len(datetime_input)-len(offset_format)
            offset = re.sub(r"\D", "", datetime_input[offset_start:]) #remove everything but the numbers from the UTC offset
            sign = datetime_input[offset_start-1:offset_start] # offset plus or minus
            offset_delta = datetime.timedelta(hours=int(offset[:2]), minutes=int(offset[2:]))
            if sign == '-':
                offset_delta = -offset_delta

            datetime_string = datetime_input[:offset_start-1].strip()

            self.logger.debug("TopicManager datetime conversion offset:%s sign:%s" %(offset, sign))

        else:
            datetime_string = datetime_input
            offset_delta = datetime.timedelta(hours=0, minutes=0)

        epoch = time.mktime((datetime.datetime.strptime(datetime_string, datetime_format) + offset_delta).timetuple())
        self.logger.debug("TopicManager datetime conversion datetime_string:%s epoch:%s" %(datetime_string, epoch))

        return epoch

class MessageCallbackProvider(object):
    """ Provide the MQTT callback. """
    def __init__(self, config, logger, topic_manager):
        self.logger = logger
        self.topic_manager = topic_manager
        self._setup_callbacks()
        self.type = config.get('type', None)
        self.flatten_delimiter = config.get('flatten_delimiter', '_')
        self.keyword_delimiter = config.get('keyword_delimiter', ',')
        self.keyword_separator = config.get('keyword_separator', '=')
        contains_total = option_as_list(config.get('contains_total', []))
        label_map = config.get('label_map', {})
        self.full_topic_fieldname = to_bool(config.get('full_topic_fieldname', False))

        self.inputs = config.get('inputs', {})
        orig_inputs = config.get('inputs', {})
        # backwards compatible, add the label map
        for key in label_map:
            if not key in orig_inputs:
                value = {}
                value['name'] = label_map[key]
                self.inputs[key] = value

        # backwards compatible, add the cumulative fields
        for field in contains_total:
            if not field in orig_inputs:
                value = {}
                value['contains_total'] = True
                self.inputs[field] = value

        for key in self.inputs:
            if  'contains_total' in self.inputs[key]:
                self.inputs[key]['contains_total'] = to_bool(self.inputs[key]['contains_total'])

        if self.type not in self.callbacks:
            raise ValueError("Invalid type configured: %s" % self.type)

        self.previous_values = {}

    def get_callback(self):
        """ Get the MQTT callback. """
        return self.callbacks[self.type]

    def _setup_callbacks(self):
        self.callbacks = {}
        self.callbacks['individual'] = self._on_message_individual
        self.callbacks['json'] = self._on_message_json
        self.callbacks['keyword'] = self._on_message_keyword

    def _byteify(self, data, ignore_dicts=False):
        if PY2:
            # if this is a unicode string, return its string representation
            if isinstance(data, unicode): # (never called under python 3) pylint: disable=undefined-variable
                return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [self._byteify(item, ignore_dicts=True) for item in data]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            data2 = {}
            for key, value in data.items():
                key2 = self._byteify(key, ignore_dicts=True)
                value2 = self._byteify(value, ignore_dicts=True)
                if self.inputs.get(key2, {}).get('contains_total', False):
                    current_value = value2
                    value2 = self._calc_increment(key2, current_value, self.previous_values.get(key2))
                    self.previous_values[key2] = current_value

                data2[self.inputs.get(key2, {}).get('name', key2)] = value2
            return data2
        # if it's anything else, return it in its original form
        return data

    def _flatten_dict(self, dictionary, separator):
        def _items():
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    for subkey, subvalue in self._flatten_dict(value, separator).items():
                        yield key + separator + subkey, subvalue
                else:
                    yield key, value

        return dict(_items())

    def _calc_increment(self, observation, current_total, previous_total):
        self.logger.info("MessageCallbackProvider _calc_increment calculating increment " \
                         "for %s with current: %f and previous %s values."
                         % (observation, current_total, (previous_total is None and 'None' or str(previous_total))))

        if current_total is not None and previous_total is not None:
            if current_total >= previous_total:
                return current_total - previous_total
            else:
                self.logger.info("MessageCallbackProvider _calc_increment skipping calculating increment " \
                                 "for %s with current: %f and previous %f values."
                                 % (observation, current_total, previous_total))
                return None

    def _log_message(self, msg):
        self.logger.debug("MessageCallbackProvider For %s has QOS of %i and retain of %s received: %s"
                          %(msg.topic, msg.qos, msg.retain, msg.payload))

    def _log_exception(self, method, exception, msg):
        self.logger.error("MessageCallbackProvider %s failed with: %s" %(method, exception))
        self.logger.error("**** MessageCallbackProvider Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))

    def _on_message_keyword(self, client, userdata, msg): # (match callback signature) pylint: disable=unused-argument
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self._log_message(msg)

            if PY2:
                payload_str = msg.payload
            else:
                payload_str = msg.payload.decode('utf-8')

            fields = payload_str.split(self.keyword_delimiter)
            data = {}
            for field in fields:
                eq_index = field.find(self.keyword_separator)
                # Ignore all fields that do not have the separator
                if eq_index == -1:
                    self.logger.error("MessageCallbackProvider on_message_keyword failed to find separator: %s"
                                      % self.keyword_separator)
                    self.logger.error("**** MessageCallbackProvider Ignoring field=%s " % field)
                    continue

                name = field[:eq_index].strip()
                value = to_float(field[eq_index + 1:].strip()) # ToDo - a bit lazy and dangerous, assuming all incoming is a float

                if self.inputs.get(name, {}).get('contains_total', False):
                    current_value = value
                    value = self._calc_increment(name, current_value, self.previous_values.get(name))
                    self.previous_values[name] = current_value

                data[self.inputs.get(name, {}).get('name', name)] = value

            if data:
                self.topic_manager.append_data(msg.topic, data)
            else:
                self.logger.error("MessageCallbackProvider on_message_keyword failed to find data in: topic=%s and payload=%s"
                                  % (msg.topic, msg.payload))

        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_keyword', exception, msg)

    def _on_message_json(self, client, userdata, msg): # (match callback signature) pylint: disable=unused-argument
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self._log_message(msg)

            data = self._byteify(json.loads(msg.payload, object_hook=self._byteify), ignore_dicts=True)
            self.topic_manager.append_data(msg.topic, self._flatten_dict(data, self.flatten_delimiter))

        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_json', exception, msg)

    def _on_message_individual(self, client, userdata, msg): # (match callback signature) pylint: disable=unused-argument

        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self._log_message(msg)

            if self.full_topic_fieldname:
                key = msg.topic
            else:
                key = msg.topic.rpartition('/')[2]

            if PY2:
                key = key.encode('utf-8')

            value = to_float(msg.payload) # ToDo - a bit lazy and dangerous, assuming all incoming is a float

            if self.inputs.get(key, {}).get('contains_total', False):
                current_value = value
                value = self._calc_increment(key, current_value, self.previous_values.get(key))
                self.previous_values[key] = current_value

            fieldname = self.inputs.get(key, {}).get('name', key)

            data = {}
            data[fieldname] = value
            self.topic_manager.append_data(msg.topic, data)
        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_individual', exception, msg)

class MQTTSubscribe(object):
    """ Manage MQTT sunscriptions. """
    def __init__(self, service_dict, logger):
        self.logger = logger

        message_callback_config = service_dict.get('message_callback', None)
        if message_callback_config is None:
            raise ValueError("[[message_callback]] is required.")

        # For backwards compatibility
        overlap = to_float(service_dict.get('overlap', 0))
        self.logger.info("Overlap is %s" % overlap)
        topics_dict = service_dict.get('topics', {})
        topics_dict['overlap'] = overlap

        message_callback_provider_name = service_dict.get('message_callback_provider',
                                                          'user.MQTTSubscribe.MessageCallbackProvider')
        self.manager = TopicManager(topics_dict, self.logger)

        clientid = service_dict.get('clientid',
                                    'MQTTSubscribe-' + str(random.randint(1000, 9999)))
        clean_session = to_bool(service_dict.get('clean_session', True))

        host = service_dict.get('host', 'localhost')
        keepalive = to_int(service_dict.get('keepalive', 60))
        port = to_int(service_dict.get('port', 1883))
        username = service_dict.get('username', None)
        password = service_dict.get('password', None)
        log_mqtt = to_bool(service_dict.get('log', False))

        self.archive_topic = service_dict.get('archive_topic', None)

        if self.archive_topic and self.archive_topic not in service_dict['topics']:
            raise ValueError("Archive topic %s must be in [[topics]]" % self.archive_topic)

        self.logger.info("Message callback config is %s" % message_callback_config)
        self.logger.info("Message callback provider is %s" % message_callback_provider_name)
        self.logger.info("Client id is %s" % clientid)
        self.logger.info("Clean session is %s" % clean_session)
        self.logger.info("MQTTSubscribe version is %s" % VERSION)
        self.logger.info("Host is %s" % host)
        self.logger.info("Port is %s" % port)
        self.logger.info("Keep alive is %s" % keepalive)
        self.logger.info("Username is %s" % username)
        if password is not None:
            self.logger.info("Password is set")
        else:
            self.logger.info("Password is not set")
        self.logger.info("Archive topic is %s" % self.archive_topic)

        self.mqtt_logger = {
            mqtt.MQTT_LOG_INFO: self.logger.info,
            mqtt.MQTT_LOG_NOTICE: self.logger.info,
            mqtt.MQTT_LOG_WARNING: self.logger.info,
            mqtt.MQTT_LOG_ERR: self.logger.debug,
            mqtt.MQTT_LOG_DEBUG: self.logger.debug
        }

        self.client = mqtt.Client(client_id=clientid, clean_session=clean_session)

        if log_mqtt:
            self.client.on_log = self._on_log

        message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
        message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                    self.logger,
                                                                    self.manager)

        self.client.on_message = message_callback_provider.get_callback()

        self.client.on_subscribe = self._on_subscribe

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        if username is not None and password is not None:
            self.client.username_pw_set(username, password)

        self.client.connect(host, port, keepalive)

    @property
    def subscribed_topics(self):
        """ The topics subscribed to. """
        return self.manager.subscribed_topics

    def get_data(self, topic, end_ts=MAXSIZE):
        """ Get data off the queue of MQTT data. """
        return self.manager.get_data(topic, end_ts)

    def get_accumulated_data(self, topic, start_ts, end_ts, units):
        """ Get the MQTT data after being accumulated. """
        return self.manager.get_accumulated_data(topic, start_ts, end_ts, units)

    def start(self):
        """ start subscribing to the topics """
        self.logger.debug("Starting loop")
        self.client.loop_start()

    def disconnect(self):
        """ shut it down """
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, rc): # (match callback signature) pylint: disable=unused-argument
        # https://pypi.org/project/paho-mqtt/#on-connect
        # rc:
        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorised
        # 6-255: Currently unused.
        self.logger.debug("Connected with result code %i" % rc)
        self.logger.debug("Connected flags %s" % str(flags))
        for topic in self.manager.subscribed_topics:
            (result, mid) = client.subscribe(topic, self.manager.get_qos(topic))
            self.logger.debug("Subscribe to %s has a mid %i and rc %i" %(topic, mid, result))

    def _on_disconnect(self, client, userdata, rc): # (match callback signature) pylint: disable=unused-argument
        self.logger.debug("Disconnected with result code %i" %rc)

    def _on_subscribe(self, client, userdata, mid, granted_qos): # (match callback signature) pylint: disable=unused-argument
        self.logger.debug("Subscribed to topic mid: %i is size %i has a QOS of %i"
                          %(mid, len(granted_qos), granted_qos[0]))

    def _on_log(self, client, userdata, level, msg): # (match callback signature) pylint: disable=unused-argument
        self.mqtt_logger[level]("MQTTSubscribe/MQTT", msg)

class MQTTSubscribeService(StdService):
    """ The MQTT subscribe service. """
    def __init__(self, engine, config_dict):
        super(MQTTSubscribeService, self).__init__(engine, config_dict)

        service_dict = config_dict.get('MQTTSubscribeService', {})
        console = to_bool(service_dict.get('console', False))
        self.logger = Logger(console)

        self.enable = to_bool(service_dict.get('enable', True))
        if not self.enable:
            self.logger.info("Service is not enabled, exiting.")
            return

        binding = service_dict.get('binding', 'loop')

        self.logger.info("Service binding is %s" % binding)

        if 'archive_topic' in service_dict:
            raise ValueError("archive_topic, %s, is invalid when running as a service" % service_dict['archive_topic'])

        self.end_ts = 0 # prime for processing loop packet
        self.wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

        self.subscriber = MQTTSubscribe(service_dict, self.logger)
        self.subscriber.start()

        if binding == 'archive':
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        elif binding == 'loop':
            self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        else:
            raise ValueError("MQTTSubscribeService: Unknown binding: %s" % binding)

    def shutDown(self):
        self.subscriber.disconnect()

    def new_loop_packet(self, event):
        """ Handle the new loop packet event. """
        # packet has traveled back in time
        if self.end_ts > event.packet['dateTime']:
            self.logger.error("Service ignoring packet has dateTime of %f which is prior to previous packet %f"
                              %(event.packet['dateTime'], self.end_ts))
        else:
            start_ts = self.end_ts
            self.end_ts = event.packet['dateTime']

            for topic in self.subscriber.subscribed_topics: # topics might not be cached.. therefore use subscribed?
                self.logger.debug("Service packet prior to update is: %s %s"
                                  % (weeutil.weeutil.timestamp_to_string(event.packet['dateTime']),
                                     to_sorted_string(event.packet)))
                target_data = self.subscriber.get_accumulated_data(topic,
                                                                   start_ts, self.end_ts, event.packet['usUnits'])
                event.packet.update(target_data)
                self.logger.debug("Service packet after update is: %s %s"
                                  % (weeutil.weeutil.timestamp_to_string(event.packet['dateTime']),
                                     to_sorted_string(event.packet)))

    # this works for hardware generation, but software generation does not 'quality control'
    # the archive record, so this data is not 'QC' in this case.
    # If this is important, bind to the loop packet.
    def new_archive_record(self, event):
        """ Handle the new archive record event. """
        end_ts = event.record['dateTime']
        start_ts = end_ts - event.record['interval'] * 60

        for topic in self.subscriber.subscribed_topics: # topics might not be cached.. therefore use subscribed?
            self.logger.debug("Service record prior to update is: %s %s"
                              % (weeutil.weeutil.timestamp_to_string(event.record['dateTime']),
                                 to_sorted_string(event.record)))
            target_data = self.subscriber.get_accumulated_data(topic, start_ts, end_ts, event.record['usUnits'])
            event.record.update(target_data)
            self.logger.debug("Service record after update is: %s %s"
                              % (weeutil.weeutil.timestamp_to_string(event.record['dateTime']),
                                 to_sorted_string(event.record)))

def loader(config_dict, engine): # (Need to match function signature) pylint: disable=unused-argument
    """ Load and return the driver. """
    config = configobj.ConfigObj(config_dict)
    return MQTTSubscribeDriver(**config[DRIVER_NAME])

def confeditor_loader():
    """ Load and return the configuration editor. """
    return MQTTSubscribeDriverConfEditor()

class MQTTSubscribeDriver(weewx.drivers.AbstractDevice): # (methods not used) pylint: disable=abstract-method
    """weewx driver that reads data from MQTT"""

    def __init__(self, **stn_dict):
        console = to_bool(stn_dict.get('console', False))
        self.logger = Logger(console)

        self.wait_before_retry = float(stn_dict.get('wait_before_retry', 2))
        self._archive_interval = to_int(stn_dict.get('archive_interval', 300))
        self.archive_topic = stn_dict.get('archive_topic', None)

        self.logger.info("Driver wait before retry is %i" % self.wait_before_retry)

        self.wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

        self.subscriber = MQTTSubscribe(stn_dict, self.logger)
        self.subscriber.start()

    @property
    def hardware_name(self):
        return "MQTTSubscribeDriver"

    @property
    def archive_interval(self):
        return self._archive_interval

    def closePort(self):
        self.subscriber.disconnect()

    def genLoopPackets(self):
        while True:
            for topic in self.subscriber.subscribed_topics: # topics might not be cached.. therefore use subscribed?
                if topic == self.archive_topic:
                    continue

                for data in self.subscriber.get_data(topic):
                    if data:
                        yield data
                    else:
                        break

            self.logger.debug("Driver queues are empty.")

            time.sleep(self.wait_before_retry)

    def genArchiveRecords(self, lastgood_ts):
        if not self.archive_topic:
            self.logger.debug("Driver no archive topic configured.")
            raise NotImplementedError
        else:
            for data in self.subscriber.get_data(self.archive_topic, lastgood_ts):
                if data:
                    yield data
                else:
                    break

class MQTTSubscribeDriverConfEditor(weewx.drivers.AbstractConfEditor): # pragma: no cover
    """ Methods for producing and updating configuration stanzas for use in configuration file. """
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

    # Configuration for the message callback.
    [[message_callback]]
        # The format of the MQTT payload.
        # Currently support: individual, json, keyword
        # Must be specified.
        type = REPLACE_ME

    # The topics to subscribe to.
    [[topics]]

        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX
        # Default is: US
        unit_system = US

        [[[FIRST/REPLACE_ME]]]
        [[[SECOND/REPLACE_ME]]]
"""
    def prompt_for_settings(self):
        settings = {}
        settings['message_callback'] = {}
        settings['topics'] = {}

        print("Enter the host.")
        settings['host'] = self._prompt('host', 'localhost')

        print("Enter the port on the host.")
        settings['port'] = self._prompt('port', '1883')

        print("Enter the maximum period in seconds allowed between communications with the broker.")
        settings['keepalive'] = self._prompt('keepalive', '60')

        print("Enter the units for MQTT payloads without unit value: US|METRIC|METRICWX")
        settings['topics']['unit_system'] = self._prompt('unit_system', 'US', ['US', 'METRIC', 'METRICWX'])

        print("Enter a topic to subscribe to. ")
        topic = self._prompt('topic')
        while topic:
            settings['topics'][topic] = {}
            print("Enter a topic to subscribe to. Leave blank when done.")
            topic = self._prompt('topic')

        print("Enter the MQTT paylod type: individual|json|keyword")
        settings['message_callback']['type'] = self._prompt('type', 'json', ['individual', 'json', 'keyword'])

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
    from weewx.engine import StdEngine # pylint: disable=ungrouped-imports

    USAGE = """MQTTSubscribeService --help
               CONFIG_FILE
               [--records=RECORD_COUNT]
               [--interval=INTERVAL]
               [--delay=DELAY]
               [--units=US|METRIC|METRICWX]
               [--binding=archive|loop]
               [--type=driver|service]
               [--verbose]
               [--console]

    CONFIG_FILE = The WeeWX configuration file, typically weewx.conf.
    """

    def main():
        """ Prepare and run MQTTSubscribe in simulation mode. """
        parser = optparse.OptionParser(usage=USAGE)
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
        parser.add_option("--host",
                          help="The MQTT server.")
        parser.add_option("--topics",
                          help="Comma separated list of topics to subscribe to.")
        parser.add_option("--callback",
                          help="The callback type.")

        (options, args) = parser.parse_args()

        simulation_type = options.type
        binding = options.binding
        record_count = options.record_count
        interval = options.interval
        delay = options.delay
        units = weewx.units.unit_constants[options.units]

        setup_logging(options.verbose)

        config_path = os.path.abspath(args[0])

        config_dict = configobj.ConfigObj(config_path, file_error=True)

        if options.topics:
            topics = options.topics.split(',')
            if 'MQTTSubscribeService' in config_dict and 'topics' in config_dict['MQTTSubscribeService']:
                config_dict['MQTTSubscribeService']['topics'] = {}
            if 'MQTTSubscribeDriver' in config_dict and 'topics' in config_dict['MQTTSubscribeDriver']:
                config_dict['MQTTSubscribeDriver']['topics'] = {}
            for topic in topics:
                weeutil.config.merge_config(config_dict,
                                            {'MQTTSubscribeService': {'topics': {topic:{}}}})
                weeutil.config.merge_config(config_dict,
                                            {'MQTTSubscribeDriver': {'topics': {topic:{}}}})

        if options.host:
            weeutil.config.merge_config(config_dict,
                                        {'MQTTSubscribeService': {'host': options.host}})
            weeutil.config.merge_config(config_dict,
                                        {'MQTTSubscribeDriver': {'host': options.host}})

        if options.callback:
            weeutil.config.merge_config(config_dict,
                                        {'MQTTSubscribeService': {'message_callback': {'type': options.callback}}})
            weeutil.config.merge_config(config_dict,
                                        {'MQTTSubscribeDriver': {'message_callback': {'type': options.callback}}})

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
        weeutil.config.merge_config(config_dict,
                                    {'MQTTSubscribeService': {'binding': binding}})

        # if specified, override the console logging
        if options.console:
            weeutil.config.merge_config(config_dict,
                                        {'MQTTSubscribeService': {'console': True}})
            weeutil.config.merge_config(config_dict,
                                        {'MQTTSubscribeDriver': {'console': True}})

        if simulation_type == "service":
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
        """ Simulate running MQTTSubscribe as a driver that generates archive records. """
        i = 0
        while i < record_count:
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval
            end_delay_ts = end_period_ts + delay
            sleep_amount = end_delay_ts - current_time
            print("Sleeping %i seconds" % sleep_amount)
            time.sleep(sleep_amount)

            for record in driver.genArchiveRecords(end_period_ts):
                print("Record is: %s %s"
                      % (weeutil.weeutil.timestamp_to_string(record['dateTime']), to_sorted_string(record)))

            i += 1

    def simulate_driver_packet(driver, record_count):
        """ Simulate running MQTTSubscribe as a driver that generates loop packets. """
        i = 0
        for packet in driver.genLoopPackets():
            print("Packet is: %s %s"
                  % (weeutil.weeutil.timestamp_to_string(packet['dateTime']),
                     to_sorted_string(packet)))
            i += 1
            if i >= record_count:
                break

    def simulate_service(engine, config_dict, binding, record_count, interval, delay, units):
        """ Simulate running MQTTSubscribe as a service. """
        service = MQTTSubscribeService(engine, config_dict)
        i = 0
        while i < record_count:
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval
            end_delay_ts = end_period_ts + delay
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
                print("Archive Record is: %s %s"
                      % (weeutil.weeutil.timestamp_to_string(new_archive_record_event.record['dateTime']),
                         to_sorted_string(new_archive_record_event.record)))
            elif binding == 'loop':
                new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=data)
                engine.dispatchEvent(new_loop_packet_event)
                print("Loop packet is: %s %s"
                      % (weeutil.weeutil.timestamp_to_string(new_loop_packet_event.packet['dateTime']),
                         to_sorted_string(new_loop_packet_event.packet)))
            else:
                pass

            i += 1

        service.shutDown()

    main()
    