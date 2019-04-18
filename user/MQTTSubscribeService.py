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
[MQTTSubscribeService]
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
    unit_system_name = US  # or 'METRIC' or 'METRICWX'

    # The clientid to connect with
    clientid = 

    # The topic to subscribe to
    topic = 

    # The binding, loop or archive
    topic = loop

    # The amount to overlap the start time when processing the MQTT queue
    overlap = 0 

    # Mapping to WeeWX names
    [[label_map]]
        temp1 = extraTemp1
"""

# Proof of concept of a service that subscribes to an MQTT topic 
# and updates the archive record with the data in the MQTT topic

# Version 1.0.0

from __future__ import with_statement
import syslog
import paho.mqtt.client as mqtt
import threading
import json
import random
import time
import weeutil.weeutil
from weeutil.weeutil import to_sorted_string
import weewx
from weewx.engine import StdService
from collections import deque

def logmsg(dst, msg):
    syslog.syslog(dst, 'MQTTSS: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

class MQTTSubscribeService(StdService):
    def __init__(self, engine, config_dict):
        super(MQTTSubscribeService, self).__init__(engine, config_dict)
        
        service_dict = config_dict.get('MQTTSubscribeService', {})
        label_map = service_dict.get('label_map', {})
        binding = service_dict.get('binding', 'loop')
        host = service_dict.get('host', 'localhost')
        keepalive = service_dict.get('keepalive', 60)
        port = service_dict.get('port', 1883)
        topic = service_dict.get('topic', 'weather/loop')
        username = service_dict.get('username', None)
        password = service_dict.get('password', None)
        self.overlap = service_dict.get('overlap', 0)
        unit_system_name = service_dict.get('unit_system', 'US').strip().upper()
        if unit_system_name not in weewx.units.unit_constants:
            raise ValueError("MQTTSubscribeService: Unknown unit system: %s" % unit_system_name)
        unit_system = weewx.units.unit_constants[unit_system_name]
        payload_type = service_dict.get('payload_type', None) # ToDo - add to documentation
        clientid = service_dict.get('clientid', 'MQTTSubscribeService-' + str(random.randint(1000, 9999))) 

        # ToDo - make config option
        host = "weather-data.local"
        payload_type = "json"
        self.overlap = .1 

        loginf("Host is %s" % host)  
        loginf("Port is %s" % port) 
        loginf("Keep alive is %s" % keepalive) 
        loginf("Username is %s" % username) 
        if password is not None:
            loginf("Password is set")   
        else:
            loginf("Password is not set")
        loginf("Client id is %s" % clientid) 
        loginf("Topic is %s" % topic) 
        loginf("Default units is %s %i" %(unit_system_name, unit_system))
        # ToDo - log binding and overlap and payload_type
        loginf("Label map is %s" % label_map) 
        
        self.queue = deque() 

        self.end_ts = 0 # prime for processing loop packet
        
        self.client = mqtt.Client(client_id=clientid)
        if username is not None and password is not None:
            self.client.username_pw_set(username, password)
        
        self.thread = MQTTSubscribeServiceThread(self, self.queue, self.client, label_map, unit_system, payload_type, host, keepalive, port, topic)
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
        logdbg("Processing interval: %f %f" %(start_ts, end_ts))
        accumulator = weewx.accum.Accum(weeutil.weeutil.TimeSpan(start_ts, end_ts))

        logdbg("Queue size is: %i" % len(self.queue))

        while (len(self.queue) > 0 and self.queue[0]['dateTime'] <= end_ts):
            archive_data = self.queue.popleft()
            logdbg("Processing: %s" % to_sorted_string(archive_data))
            try:
                accumulator.addRecord(archive_data)
            except weewx.accum.OutOfSpan:
                loginf("Ignoring record outside of interval %f %f %f %s"
                    %(start_ts, end_ts, archive_data['dateTime'], to_sorted_string(archive_data)))

        target_data = {}
        if not accumulator.isEmpty:
            aggregate_data = accumulator.getRecord()
            logdbg("Data prior to conversion is: %s" % to_sorted_string(aggregate_data))     
            target_data = weewx.units.to_std_system(aggregate_data, record['usUnits'])  
            logdbg("Data after to conversion is: %s" % to_sorted_string(target_data))   
            logdbg("Record prior to update is: %s" % to_sorted_string(record))    
        else:
            logdbg("Queue was empty")

        return target_data

    def new_loop_packet(self, event):
        start_ts = self.end_ts - self.overlap
        self.end_ts = event.packet['dateTime']
        target_data = self._process_data(start_ts, self.end_ts, event.packet)
        event.packet.update(target_data)
        logdbg("Packet after update is: %s" % to_sorted_string(event.packet))  

    # this works for hardware generation, but software generation does not 'quality control'
    # the archive record, so this data is not 'QC' in this case.
    # If this is important, bind to the loop packet.
    def new_archive_record(self, event):
        end_ts = event.record['dateTime']
        start_ts = end_ts - event.record['interval'] * 60 - self.overlap
        target_data = self._process_data(start_ts, end_ts, event.record)
        event.record.update(target_data)
        logdbg("Record after update is: %s" % to_sorted_string(event.record))  

class MQTTSubscribeServiceThread(threading.Thread): 
    def __init__(self, service, queue, client, label_map, unit_system, payload_type, host, keepalive, port, topic):
        threading.Thread.__init__(self)

        self.service = service
        self.queue = queue
        self.client = client
        self.label_map = label_map
        self.unit_system = unit_system
        self.payload_type = payload_type
        self.host = host
        self.keepalive = keepalive
        self.port = port
        self.topic = topic
        
    # sub class overrides this for specific MQTT payload formats
    def on_message(self, client, userdata, msg):
        loginf("Method 'on_message' not implemented")

    def on_json_message(self, client, userdata, msg):
        logdbg("For %s received: %s" %(msg.topic, msg.payload))
        data = self._byteify(
            json.loads(msg.payload, object_hook=self._byteify),
            ignore_dicts=True)

        if 'dateTime' not in data:
            data['dateTime'] = time.time()

        if 'usUnits' not in data:
            data['usUnits'] = self.unit_system          
        
        logdbg("Added to queue: %s" % to_sorted_string(data))
        self.queue.append(data,)

    def on_individual_message(self, client, userdata, msg):
        logdbg("For %s received: %s" %(msg.topic, msg.payload))
        
        tkey = msg.topic.split("/", 1)[1]
        key = tkey.encode('ascii', 'ignore') # ToDo - research
        
        data = {}
        data['dateTime'] = time.time()
        data['usUnits'] = self.unit_system 
        data[self.label_map.get(key,key)] = msg.payload
        
        self.queue.append(data,)

    def on_connect(self, client, userdata, flags, rc):
        logdbg("Connected with result code %i" % rc)
        client.subscribe(self.topic)

    def on_disconnect(self, client, userdata, rc):
        logdbg("Disconnected with result code %i" %rc)

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

    def run(self):
        if self.payload_type == 'json':
            self.client.on_message = self.on_json_message
        elif self.payload_type =='individual':
            self.client.on_message = self.on_individual_message
        else:
            self.client.on_message = self.on_message

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect   
      
        self.client.connect(self.host, self.port, self.keepalive)

        logdbg("Starting loop")
        self.client.loop_forever()

# Run from WeeWX home directory
# PYTHONPATH=bin python bin/user/MQTTSubscribeService.py
if __name__ == '__main__':
    import optparse
    import os
    import configobj
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
        parser.add_option("--verbose", action="store_true", dest="verbose",
                        help="Log extra output (debug=1).")

        (options, args) = parser.parse_args()

        binding = options.binding
        record_count = options.record_count
        interval = options.interval
        archive_delay = options.delay
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

        print("Creating %i %s records" % (record_count, binding))
        print("Interval is %i seconds" % interval)
        print("Archive delay is %i seconds" % archive_delay)

        engine = StdEngine(min_config_dict)

        weewx.accum.initialize(config_dict)

        # override the configured binding with the parameter value
        weeutil.weeutil.merge_config(config_dict,
                                    {'MQTTSubscribeService': {'binding': binding}})
        service = MQTTSubscribeService(engine, config_dict)

        # ToDo - move the if inside the subroutine
        if binding == 'archive':
            simulate_archive(engine, record_count, interval, archive_delay, units)
        elif binding == 'loop':
            simulate_loop(engine, record_count, interval, units)

        service.shutDown()

    def simulate_loop(engine, loop_record_count, loop_interval, units):
        i = 0 
        while i < loop_record_count:
            current_time = int(time.time() + 0.5)
            end_loop_period_ts = (int(current_time / loop_interval) + 1) * loop_interval
            sleep_amount = end_loop_period_ts - current_time

            print("Sleeping %f seconds" % sleep_amount)
            time.sleep(sleep_amount)

            packet = {}
            packet['dateTime'] = time.time()
            packet['usUnits'] = units 

            new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                        packet=packet)
            engine.dispatchEvent(new_loop_packet_event)
            print("Loop packet is: %s" % to_sorted_string(new_loop_packet_event.packet))
            i += 1


    def simulate_archive(engine, archive_record_count, archive_interval, archive_delay, units):
        i = 0 
        while i < archive_record_count:
            current_time = int(time.time() + 0.5)
            end_archive_period_ts = (int(current_time / archive_interval) + 1) * archive_interval
            end_archive_delay_ts  =  end_archive_period_ts + archive_delay
            sleep_amount = end_archive_delay_ts - current_time
            
            print("Sleeping %i seconds" % sleep_amount)
            time.sleep(sleep_amount)

            record = {}
            record['dateTime'] = end_archive_period_ts
            record['interval'] = archive_interval / 60
            record['usUnits'] = units 

            new_archive_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                        record=record,
                                                        origin='hardware')
            engine.dispatchEvent(new_archive_record_event)
            print("Archive record is: %s" % to_sorted_string(new_archive_record_event.record))
            i += 1


    main()