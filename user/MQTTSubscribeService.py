from __future__ import with_statement
import syslog
import Queue
import paho.mqtt.client as mqtt
import threading
import weewx
from weewx.engine import StdService

def logmsg(dst, msg):
    print(msg)
    syslog.syslog(dst, 'MQTTSUB: %s' % msg)

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
        host = service_dict.get('host', 'weather-data.local')
        keepalive = service_dict.get('keepalive', 60)
        port = service_dict.get('port', 1883)
        topic = service_dict.get('topic', 'weather/archive')
        username = service_dict.get('username', None)
        password = service_dict.get('password', None)
        # ToDo randomize this
        clientid = service_dict.get('clientid', 'MQTTSubscribeService') 

        #log config options
        loginf("host is %s" % host)      
        
        self.queue = Queue.Queue() 
        
        self.client = mqtt.Client(client_id=clientid)
        
        self.thread = MQTTSubscribeServiceThread(self, self.queue, self.client, host, keepalive, port, topic, username, password)
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
        while not self.queue.empty():
            try:
                msg = self.queue.get_nowait()
                logdbg(msg.topic)
                logdbg(msg.payload)
            except Empty, e:
                break 

class MQTTSubscribeServiceThread(threading.Thread):
    def __init__(self, service, queue, client, host, keepalive, port, topic, username, password):
        threading.Thread.__init__(self)

        self.service = service
        self.queue = queue
        self.client = client
        self.host = host
        self.keepalive = keepalive
        self.port = port
        self.topic = topic
        self.username = username
        self.password = password
        
    def on_message(self, client, userdata, msg):
        #logdbg(msg.topic)
        #logdbg(msg.payload)
        self.queue.put(msg,)

    def on_connect(self, client, userdata, flags, rc):
        logdbg("Connected with result code "+str(rc))
        loginf("MQTT topic subscription: " + str(self.topic))
        client.subscribe(self.topic)

    def on_disconnect(self, client, userdata, rc):
        logdbg("Disconnected with result code "+str(rc))

    def run(self):
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        if self.username is not None and self.password is not None:
            self.client.username_pw_set(username, password)
      
        self.client.connect(self.host, self.port, self.keepalive)

        logdbg("Starting loop")
        self.client.loop_forever()
        