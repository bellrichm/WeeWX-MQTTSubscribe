#!/usr/bin/python

# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring

import configobj
import os
import threading
import time


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
        config_dict['host'] = 'weather-data.local'
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

# Create new threads
records = []
THREAD1 = MyThread(1, "Thread-1", 1, records)
#THREAD2 = MyThread(2, "Thread-2", 2)

# Start new Threads
THREAD1.start()
THREAD1.join()
#THREAD2.start()

print(records)
print("Exiting Main Thread")
