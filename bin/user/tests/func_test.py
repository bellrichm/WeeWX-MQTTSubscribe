#!/usr/bin/python

# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring

import configobj
import os
import threading
import time
import paho.mqtt.client as mqtt

from user.MQTTSubscribe import MQTTSubscribe, Logger, setup_logging

EXITFLAG = 0

class MyThread(threading.Thread):
    def __init__(self, thread_id, name, delay, records):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.delay = delay
        self.records = records

        config_path = os.path.abspath("bin/user/tests/data/second.conf")
        config_dict = configobj.ConfigObj(config_path, file_error=True)['MQTTSubscribe']
        #config_dict['host'] = 'weather-data.local'
        message_callback_config = config_dict.get('message_callback', None)
        message_callback_config['type'] = 'json'
        #setup_logging(True)
        logger = Logger(console=True)
        setup_logging(True)
        self.subscriber = MQTTSubscribe(config_dict, logger)
        self.subscriber.start()
        print("test")

    def run(self):
        print("Starting " + self.name)
        print_time(self.name, 5, self.delay)
        print("Exiting " + self.name)
        #records = []
        for data in self.subscriber.get_data('weather/loop'):
            if data:
                self.records.append(data)
            else:
                break
        #print(records)

def print_time(thread_name, counter, delay):
    while counter:
        if EXITFLAG:
            thread_name.exit()
        time.sleep(delay)
        print("%s: %s" % (thread_name, time.ctime(time.time())))
        counter -= 1

def on_connect(client, userdata, flags, rc):  # (match callback signature) pylint: disable=unused-argument
    """ The on_connect callback. """
    # https://pypi.org/project/paho-mqtt/#on-connect
    # rc:
    # 0: Connection successful
    # 1: Connection refused - incorrect protocol version
    # 2: Connection refused - invalid client identifier
    # 3: Connection refused - server unavailable
    # 4: Connection refused - bad username or password
    # 5: Connection refused - not authorised
    # 6-255: Currently unused.
    print("Connected with result code %i" % rc)
    print("Connected flags %s" % str(flags))


def on_disconnect(client, userdata, rc):  # (match callback signature) pylint: disable=unused-argument
    """ The on_connect callback. """
    # https://pypi.org/project/paho-mqtt/#on-connect
    # rc:
    # 0: Connection successful
    print("Disconnected with result code %i" % rc)

def on_publish(client, userdata, mid):  # (match callback signature) pylint: disable=unused-argument
    """ The on_publish callback. """
    print("Published: %s" % mid)

# Create new threads
records = []
THREAD1 = MyThread(1, "Thread-1", 1, records)
#THREAD2 = MyThread(2, "Thread-2", 2)

# Start new Threads
#THREAD1.start()
# sudo /usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf
client_id = 'clientid'
host = 'localhost'
port = 1883
keepalive = 60

client = mqtt.Client(client_id)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.connect(host, port, keepalive)
client.loop_start()

#THREAD1.join()
#THREAD2.start()

print(records)
print("Exiting Main Thread")
