# Proof of concept of a service that subscribes to an MQTT topic 
# and updates the archive record with the data in the MQTT topic
#
# This service consists of two threads. One thread waits on the MQTT
# topic and when data is recieved it is the queue.
#
# The other thread handles the NEW_ARCHIVE_RECORD event. On this
# event, it processes the queue of MQTT payloads and updates the archive record.
# This implementation takes last payload in the queue and uses its data to 
# update the archive record.
#
# ToDos (in not particular order)
# - various ToDos in the code
# - Additional documentation
# - cleanup the code
# - Python 3
# - Tests
#
# Development motivations consist of, but is not limited to, the following:
# - Get a better understanding of WeeWx internals
# - Get a better understanding of MQTT
# - Learn additional Python topics like, threading, Python 3, etc.
#
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
    print('MQTTSS: %s' % msg)
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
        host = service_dict.get('host', 'weather-data.local')
        keepalive = service_dict.get('keepalive', 60)
        port = service_dict.get('port', 1883)
        topic = service_dict.get('topic', 'weather/loop')
        username = service_dict.get('username', None)
        password = service_dict.get('password', None)
        unit_system_name = service_dict.get('unit_system', 'US').strip().upper()
        if unit_system_name not in weewx.units.unit_constants:
            raise ValueError("MQTTSubscribeService: Unknown unit system: %s" % unit_system_name)
        unit_system = weewx.units.unit_constants[unit_system_name]
        clientid = service_dict.get('clientid', 'MQTTSubscribeService-' + str(random.randint(1000, 9999))) 

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
        loginf("Label map is %s" % label_map) 
        
        self.queue = deque() 
        
        self.client = mqtt.Client(client_id=clientid)
        if username is not None and password is not None:
            self.client.username_pw_set(username, password)
        
        self.thread = MQTTSubscribeServiceThread(self, self.queue, self.client, label_map, unit_system, host, keepalive, port, topic)
        self.thread.start()

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)   
        
    def shutDown(self):
        self.client.disconnect() 
        if self.thread:
            self.thread.join()
            self.thread = None

    def new_archive_record(self, event):
        end_ts = event.record['dateTime']
        start_ts = end_ts - event.record['interval'] * 60
        logdbg("Processing interval: %f %f" %(start_ts, end_ts))
        accumulator = weewx.accum.Accum(weeutil.weeutil.TimeSpan(start_ts, end_ts))

        while (len(self.queue) > 0 and self.queue[0]['dateTime'] < end_ts):
            archive_data = self.queue.popleft()
            logdbg("Processing: %s" % to_sorted_string(archive_data))
            try:
                accumulator.addRecord(archive_data)
            except weewx.accum.OutOfSpan:
                loginf("Ignoring record outside of interval %f %f %f %s"
                    %(start_ts, end_ts, archive_data['dateTime'], to_sorted_string(archive_data)))

        if not accumulator.isEmpty:
            aggregate_data = accumulator.getRecord()
            logdbg("Data prior to conversion is: %s" % to_sorted_string(aggregate_data))     
            target_data = weewx.units.to_std_system(aggregate_data, event.record['usUnits'])  
            logdbg("Data after to conversion is: %s" % to_sorted_string(target_data))   
            logdbg("Record prior to update is: %s" % to_sorted_string(event.record))   
            event.record.update(target_data)
            logdbg("Record after update is: %s" % to_sorted_string(event.record))   
        else:
            logdbg("Queue was empty")

class MQTTSubscribeServiceThread(threading.Thread): 
    def __init__(self, service, queue, client, label_map, unit_system, host, keepalive, port, topic):
        threading.Thread.__init__(self)

        self.service = service
        self.queue = queue
        self.client = client
        self.label_map = label_map
        self.unit_system = unit_system
        self.host = host
        self.keepalive = keepalive
        self.port = port
        self.topic = topic
        
    def on_message(self, client, userdata, msg):
        logdbg("For %s received: %s" %(msg.topic, msg.payload))
        data = self.create_archive_data(msg.payload)
        logdbg("Added to queue: %s" % to_sorted_string(data))
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

    # Convert the MQTT payload into a dictionary of archive data usable by WeeWX
    # In theory, a subclass could override to massage different formatted payloads
    def create_archive_data(self, json_text):
        data = self._byteify(
            json.loads(json_text, object_hook=self._byteify),
            ignore_dicts=True)

        if 'dateTime' not in data:
            data['dateTime'] = time.time()

        if 'usUnits' not in data:
            data['usUnits'] = self.unit_system            
    
        return data

    def run(self):
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect   
      
        self.client.connect(self.host, self.port, self.keepalive)

        logdbg("Starting loop")
        self.client.loop_forever()

    # PYTHONPATH=bin python bin/user/MQTTSubscribeService.py

if __name__ == '__main__':
    from weewx.engine import StdEngine

    config_dict = {
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

    engine = StdEngine(config_dict)

    service = MQTTSubscribeService(engine, config_dict)

    time.sleep(5)

    record = {}
    record['dateTime'] = time.time()
    record['interval'] = 5
    record['usUnits'] = 1  
    new_archive_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                record=record,
                                                origin='hardware')

    engine.dispatchEvent(new_archive_record_event)

    service.shutDown()