"""weewx service that subscribes to an MQTT Topic and augments the archive record

Installation:
    Put this file in the bin/user directory.
    Update weewx.conf [MQTTSubscribeService] as needed to configure the service.
    Update weewx.conf [Accumulator] for any custom fields.

Overview:
    This service consists of two threads. One thread waits on the MQTT topic
    and when data is received it is added to the queue.

    The other thread binds to the NEW_ARCHIVE_RECORD event. On this event,
    it processes the queue of MQTT payloads and updates the archive record.

Configuration:
[MQTTSubscribeService] or [MQTTSubscribeDriver]
    # The MQTT server
    host = localhost

    # The port to connect to
    port = 1883

    # Maximum period in seconds allowed between communications with the broker
    keepalive = 60

    # username for broker authentication
    username =

    # password for broker authentication
    password =

    # Units for MQTT payloads without unit value
    unit_system = US  # or 'METRIC' or 'METRICWX'

    # The clientid to connect with
    clientid =

    # The topic to subscribe to
    topic =

    # The format of the MQTT payload. Currently support 'individual' or 'json'
    payload_type = json

    # When True, the full topic (weather/outTemp) is used as the fieldname. When false, the topic
    # furthest to the right is used. Only used when payload is 'individual'.
    full_topic_fieldname = False

    # The delimiter between fieldname and value pairs. (field1=value1, field2=value2)
    keyword_delimiter = ,

    # The separator between fieldname and value pairs. (field1=value1, field2=value2)
    keyword_separator = =

    # Mapping to WeeWX names
    [[label_map]]
        temp1 = extraTemp1

    # The amount to overlap the start time when processing the MQTT queue
    # Only used by the service
    overlap = 0

    # The binding, loop or archive
    # Only used by the service
    binding = loop

    # The amount of time to wait when the queue of MQTT payload is empty
    # Only used by the driver
    wait_before_retry = 2

    # Payload in this topic is processed like an archive record
    # Only used by the driver
    archive_topic =
"""

from __future__ import with_statement
import six
import configobj
import syslog
import paho.mqtt.client as mqtt
import threading
import json
import random
import time
import weeutil.weeutil
from weeutil.weeutil import to_bool, to_float, to_int, to_sorted_string
import weewx
import weewx.drivers
from weewx.engine import StdService
from collections import deque

VERSION='1.1.0rc04'

def logmsg(console, dst, msg):
    syslog.syslog(dst, 'MQTTSS: %s' % msg)
    if console:
        print('MQTTSS: %s' % msg)

def logdbg(console, msg):
    logmsg(console, syslog.LOG_DEBUG, msg)

def loginf(console, msg):
    logmsg(console, syslog.LOG_INFO, msg)

def logerr(console, msg):
    logmsg(console, syslog.LOG_ERR, msg)

class MQTTSubscribe():
    def __init__(self, client, queue, archive_queue, unit_system, service_dict):

        self.client = client
        self.queue = queue
        self.archive_queue = archive_queue
        self.unit_system = unit_system

        self.console = to_bool(service_dict.get('console', False))
        host = service_dict.get('host', 'localhost')
        keepalive = to_int(service_dict.get('keepalive', 60))
        port = to_int(service_dict.get('port', 1883))
        username = service_dict.get('username', None)
        password = service_dict.get('password', None)

        self.topic = service_dict.get('topic', 'weather/loop')
        self.archive_topic = service_dict.get('archive_topic', None)

        self.payload_type = service_dict.get('payload_type', None)
        self.full_topic_fieldname = to_bool(service_dict.get('full_topic_fieldname', False))
        self.keyword_delimiter = service_dict.get('keyword_delimiter', ',')
        self.keyword_separator = service_dict.get('keyword_separator', '=')
        self.label_map = service_dict.get('label_map', {})

        loginf(self.console, "MQTTSubscribe version is %s" % VERSION)
        loginf(self.console, "Host is %s" % host)
        loginf(self.console, "Port is %s" % port)
        loginf(self.console, "Keep alive is %s" % keepalive)
        loginf(self.console, "Username is %s" % username)
        if password is not None:
            loginf(self.console, "Password is set")
        else:
            loginf(self.console, "Password is not set")
        loginf(self.console, "Topic is %s" % self.topic)
        loginf(self.console, "Archive topic is %s" % self.archive_topic)
        loginf(self.console, "Payload type is %s" % self.payload_type)
        loginf(self.console, "Full topic fieldname is %s" % self.full_topic_fieldname)
        loginf(self.console, "Keyword separator is %s" % self.keyword_separator)
        loginf(self.console, "Keyword delimiter is %s" % self.keyword_delimiter)
        loginf(self.console, "Default units is %i" % self.unit_system)
        loginf(self.console, "Label map is %s" % self.label_map)

        if self.payload_type == 'json':
            self.client.on_message = self.on_message_json
        elif self.payload_type =='individual':
            self.client.on_message = self.on_message_individual
        elif self.payload_type =='keyword':
            self.client.on_message = self.on_message_keyword
        else:
            self.client.on_message = self.on_message

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        if username is not None and password is not None:
         self.client.username_pw_set(username, password)

        self.client.connect(host, port, keepalive)

    # sub class overrides this for specific MQTT payload formats
    def on_message(self, client, userdata, msg):
        loginf(self.console, "Method 'on_message' not implemented")

    def on_message_keyword(self, client, userdata, msg):
        logdbg(self.console, "For %s received: %s" %(msg.topic, msg.payload))

        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            fields = msg.payload.split(self.keyword_delimiter)
            data = {}
            for field in fields:
                eq_index = field.find(self.keyword_separator)
                # Ignore all fields that do not have the separator
                if eq_index == -1:
                    logerr(self.console, "on_message_keyword failed to find separator: %s" % self.keyword_separator)
                    logerr(self.console, "**** Ignoring field=%s " % field)
                    continue

                name = field[:eq_index].strip()
                value = field[eq_index + 1:].strip()
                data[self.label_map.get(name, name)] = to_float(value)

            if data:
                if 'dateTime' not in data:
                    data['dateTime'] = time.time()
                if 'usUnits' not in data:
                    data['usUnits'] = self.unit_system

                logdbg(self.console, "Added to queue: %s" % to_sorted_string(data))

                if msg.topic == self.archive_topic:
                    self.archive_queue.append(data,)
                else:
                    self.queue.append(data,)
            else:
                logerr(self.console, "on_message_keyword failed to find data in: topic=%s and payload=%s" % (msg.topic, msg.payload))
        except Exception as exception:
            logerr(self.console, "on_message_json failed with: %s" % exception)
            logerr(self.console, "**** Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))

    def on_message_json(self, client, userdata, msg):
        logdbg(self.console, "For %s received: %s" %(msg.topic, msg.payload))

        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
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
                data['usUnits'] = self.unit_system

            logdbg(self.console, "Added to queue: %s" % to_sorted_string(data))

            if msg.topic == self.archive_topic:
                self.archive_queue.append(data,)
            else:
                self.queue.append(data,)
        except Exception as exception:
            logerr(self.console, "on_message_json failed with: %s" % exception)
            logerr(self.console, "**** Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))


    def on_message_individual(self, client, userdata, msg):
        logdbg(self.console, "For %s received: %s" %(msg.topic, msg.payload))

        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            if self.full_topic_fieldname:
                key = msg.topic.encode('ascii', 'ignore') # ToDo - research
            else:
                tkey = msg.topic.rpartition('/')[2]
                key = tkey.encode('ascii', 'ignore') # ToDo - research

            data = {}
            data['dateTime'] = time.time()
            data['usUnits'] = self.unit_system
            data[self.label_map.get(key,key)] = to_float(msg.payload)

            self.queue.append(data,)
        except Exception as exception:
            logerr(self.console, "on_message_individual failed with: %s" % exception)
            logerr(self.console, "**** Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))

    def on_connect(self, client, userdata, flags, rc):
        logdbg(self.console, "Connected with result code %i" % rc)
        client.subscribe(self.topic)
        if self.archive_topic:
          client.subscribe(self.archive_topic)

    def on_disconnect(self, client, userdata, rc):
        logdbg(self.console, "Disconnected with result code %i" %rc)

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
                data2[self.label_map.get(key2,key2)] = self._byteify(value, ignore_dicts=True)
            return data2
        # if it's anything else, return it in its original form
        return data

class MQTTSubscribeService(StdService):
    def __init__(self, engine, config_dict):
        super(MQTTSubscribeService, self).__init__(engine, config_dict)

        service_dict = config_dict.get('MQTTSubscribeService', {})
        self.console = to_bool(service_dict.get('console', False))
        self.overlap = to_float(service_dict.get('overlap', 0))
        binding = service_dict.get('binding', 'loop')
        unit_system_name = service_dict.get('unit_system', 'US').strip().upper()
        if unit_system_name not in weewx.units.unit_constants:
            raise ValueError("MQTTSubscribeService: Unknown unit system: %s" % unit_system_name)
        unit_system = weewx.units.unit_constants[unit_system_name]
        clientid = service_dict.get('clientid', 'MQTTSubscribeService-' + str(random.randint(1000, 9999)))

        loginf(self.console, "Client id is %s" % clientid)
        loginf(self.console, "Default units is %s %i" %(unit_system_name, unit_system))
        loginf(self.console, "Binding is %s" % binding)
        loginf(self.console, "Overlap is %s" % self.overlap)

        if 'archive_topic' in service_dict:
          raise ValueError("archive_topic, %s, is invalid when running as a service" % service_dict['archive_topic'])

        self.queue = deque()
        self.archive_queue = None

        self.end_ts = 0 # prime for processing loop packet

        self.client = mqtt.Client(client_id=clientid)
        self.thread = MQTTSubscribeServiceThread(self, self.client, self.queue, self.archive_queue, unit_system, service_dict)

        self.thread.start()

        if (binding == 'archive'):
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        elif (binding == 'loop'):
            self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        else:
            raise ValueError("MQTTSubscribeService: Unknown binding: %s" % binding)

    def shutDown(self):
        self.client.disconnect()
        if self.thread:
            self.thread.join()
            self.thread = None

    def _process_data(self, start_ts, end_ts, record):
        logdbg(self.console, "Processing interval: %f %f" %(start_ts, end_ts))
        accumulator = weewx.accum.Accum(weeutil.weeutil.TimeSpan(start_ts, end_ts))

        logdbg(self.console, "Queue size is: %i" % len(self.queue))

        while (len(self.queue) > 0 and self.queue[0]['dateTime'] <= end_ts):
            archive_data = self.queue.popleft()
            logdbg(self.console, "Processing: %s" % to_sorted_string(archive_data))
            try:
                accumulator.addRecord(archive_data)
            except weewx.accum.OutOfSpan:
                loginf(self.console, "Ignoring record outside of interval %f %f %f %s"
                    %(start_ts, end_ts, archive_data['dateTime'], to_sorted_string(archive_data)))

        target_data = {}
        if not accumulator.isEmpty:
            aggregate_data = accumulator.getRecord()
            logdbg(self.console, "Data prior to conversion is: %s" % to_sorted_string(aggregate_data))
            target_data = weewx.units.to_std_system(aggregate_data, record['usUnits'])
            logdbg(self.console, "Data after to conversion is: %s" % to_sorted_string(target_data))
            logdbg(self.console, "Record prior to update is: %s" % to_sorted_string(record))
        else:
            logdbg(self.console, "Queue was empty")

        return target_data

    def new_loop_packet(self, event):
        start_ts = self.end_ts - self.overlap
        self.end_ts = event.packet['dateTime']
        target_data = self._process_data(start_ts, self.end_ts, event.packet)
        event.packet.update(target_data)
        logdbg(self.console, "Packet after update is: %s" % to_sorted_string(event.packet))

    # this works for hardware generation, but software generation does not 'quality control'
    # the archive record, so this data is not 'QC' in this case.
    # If this is important, bind to the loop packet.
    def new_archive_record(self, event):
        end_ts = event.record['dateTime']
        start_ts = end_ts - event.record['interval'] * 60 - self.overlap
        target_data = self._process_data(start_ts, end_ts, event.record)
        event.record.update(target_data)
        logdbg(self.console, "Record after update is: %s" % to_sorted_string(event.record))

class MQTTSubscribeServiceThread(MQTTSubscribe, threading.Thread):
    def __init__(self, service, client, queue, archive_queue, unit_system, service_dict):
        threading.Thread.__init__(self)
        MQTTSubscribe.__init__(self, client, queue, archive_queue, unit_system, service_dict)

    def run(self):
        logdbg(self.console, "Starting loop")
        self.client.loop_forever()

def loader(config_dict, engine):
    config = configobj.ConfigObj(config_dict)
    return MQTTSubscribeDriver(engine, **config['MQTTSubscribeDriver'])

class MQTTSubscribeDriver(MQTTSubscribe, weewx.drivers.AbstractDevice):
    """weewx driver that reads data from MQTT"""

    def __init__(self, engine, **stn_dict):
      self.console = to_bool(stn_dict.get('console', False))
      self.wait_before_retry = float(stn_dict.get('wait_before_retry', 2))
      unit_system_name = stn_dict.get('unit_system', 'US').strip().upper()
      if unit_system_name not in weewx.units.unit_constants:
          raise ValueError("MQTTSubscribeService: Unknown unit system: %s" % unit_system_name)
      unit_system = weewx.units.unit_constants[unit_system_name]
      clientid = stn_dict.get('clientid', 'MQTTSubscribeDriver-' + str(random.randint(1000, 9999)))

      loginf(self.console, "Client id is %s" % clientid)
      loginf(self.console, "Default units is %s %i" %(unit_system_name, unit_system))
      loginf(self.console, "Wait before retry is %i" % self.wait_before_retry)

      queue = deque()
      archive_queue = deque()

      client = mqtt.Client(client_id=clientid)
      MQTTSubscribe.__init__(self, client, queue, archive_queue, unit_system, stn_dict)

      logdbg(self.console, "Starting loop")
      self.client.loop_start()

    def genLoopPackets(self):
      while True:
        logdbg(self.console, "Packet queue is size %i" % len(self.queue))
        while len(self.queue) > 0:
          packet = self.queue.popleft()
          logdbg(self.console, "Packet: %s" % to_sorted_string(packet))
          yield packet
        logdbg(self.console, "Packet queue is empty.")
        time.sleep(self.wait_before_retry)

    def genArchiveRecords(self, lastgood_ts):
        logdbg(self.console, "Archive queue is size %i and date is %f." %(len(self.archive_queue), lastgood_ts))
        while (len(self.archive_queue) > 0 and self.archive_queue[0]['dateTime'] <= lastgood_ts):
            archive_record = self.archive_queue.popleft()
            logdbg(self.console, "Archive record: %s" % to_sorted_string(archive_record))
            yield archive_record

    @property
    def hardware_name(self):
        return "MQTTSubscribeDriver"

# Run from WeeWX home directory
# PYTHONPATH=bin python bin/user/MQTTSubscribe.py
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
               [--units=UNITS]
               [--verbose]
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