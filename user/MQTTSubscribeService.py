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
# - Fully support overriding of names in the MQTT payload via the label_map
# - Handle units and any necessary conversion of the MQTT payload
# - Handle aggregation of the MQTT payload - or at least ability to customize by overriding
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
import time
import weeutil.weeutil
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
        
        label_map = {}

        service_dict = config_dict.get('MQTTSubscribeService', {})
        host = service_dict.get('host', 'weather-data.local')
        keepalive = service_dict.get('keepalive', 60)
        port = service_dict.get('port', 1883)
        topic = service_dict.get('topic', 'weather/loop')
        username = service_dict.get('username', None)
        password = service_dict.get('password', None)
        # ToDo randomize this
        clientid = service_dict.get('clientid', 'MQTTSubscribeService') 

        #ToDo log config options
        loginf("host is %s" % host)      
        
        self.queue = deque() 
        
        self.client = mqtt.Client(client_id=clientid)
        if username is not None and password is not None:
            self.client.username_pw_set(username, password)
        
        self.thread = MQTTSubscribeServiceThread(self, self.queue, self.client, label_map, host, keepalive, port, topic)
        self.thread.start()

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)   
        
    def shutDown(self):
        # when the service shuts down, 
        self.client.disconnect() 
        if self.thread:
            self.thread.join()
            self.thread = None

    # put appropriate logic here to process queue and update archive_record
    # queue could have zero or more elements
    def new_archive_record(self, event):
        aggregate_data = None
        end_ts = event.record['dateTime']
        start_ts = end_ts - 300 # ToDo - get archive period
        accumulator = weewx.accum.Accum(weeutil.weeutil.TimeSpan(start_ts, end_ts))
        logdbg(len(self.queue))
        i = 0
        while (len(self.queue) > 0 and self.queue[0]['dateTime'] < end_ts):
            i = i+1
            # logdbg(i)          

            archive_data = self.queue.popleft()
            #logdbg(archive_data)
            #logdbg(str(i) + " " + str(start_ts) + " " + str(end_ts) + " " + str(archive_data['dateTime']))
            
            if archive_data['dateTime'] > start_ts:
                try:
                    accumulator.addRecord(archive_data)
                except weewx.accum.OutOfSpan:
                    # ToDo - This should never be executed - so log appropriately
                    logdbg(str(start_ts) + " " + str(end_ts) + " " + str(archive_data['dateTime']))
                    #logdbg(archive_data)


        # ToDo - handle empty queue
        aggregate_data = accumulator.getRecord()
        #logdbg(aggregate_data)        
        event.record.update(aggregate_data)

class MQTTSubscribeServiceThread(threading.Thread): 
    def __init__(self, service, queue, client, label_map, host, keepalive, port, topic):
        threading.Thread.__init__(self)

        self.service = service
        self.queue = queue
        self.client = client
        self.label_map = label_map
        self.host = host
        self.keepalive = keepalive
        self.port = port
        self.topic = topic
        
    def on_message(self, client, userdata, msg):
        #logdbg(msg.topic)
        #logdbg(msg.payload)
        data = self.create_archive_data(msg.payload)
        self.queue.append(data,)

    def on_connect(self, client, userdata, flags, rc):
        logdbg("Connected with result code "+str(rc))
        loginf("MQTT topic subscription: " + str(self.topic))
        client.subscribe(self.topic)

    def on_disconnect(self, client, userdata, rc):
        logdbg("Disconnected with result code "+str(rc))

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
    # ToDo - handle missing unites, use a default from the configuration
    def create_archive_data(self, json_text):

        data = self._byteify(
            json.loads(json_text, object_hook=self._byteify),
            ignore_dicts=True)

        if 'dateTime' not in data:
            data['dateTime'] = time.time()
    
        return data

    def run(self):
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect   
      
        self.client.connect(self.host, self.port, self.keepalive)

        logdbg("Starting loop")
        self.client.loop_forever()
        