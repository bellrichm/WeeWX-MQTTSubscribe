# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring

import unittest

import configobj
import json
import os
import threading
import time

import paho.mqtt.client as mqtt

from user.MQTTSubscribe import MQTTSubscribe, Logger, setup_logging

class MyThread(threading.Thread):
    def __init__(self, records):
        threading.Thread.__init__(self)
        self.records = records

        config_path = os.path.abspath("bin/user/tests/data/second.conf")
        config_dict = configobj.ConfigObj(config_path, file_error=True)['MQTTSubscribe']
        message_callback_config = config_dict.get('message_callback', None)
        message_callback_config['type'] = 'json'
        #setup_logging(True)
        logger = Logger()
        setup_logging(True)
        self.subscriber = MQTTSubscribe(config_dict, logger)
        self.subscriber.start()

    def run(self):
        for data in self.subscriber.get_data('weather/loop'):
            if data:
                self.records.append(data)
            else:
                break

class TestIndividualPayload(unittest.TestCase):
    def test_get_data_test(self):
        sleep = 1
        records = []
        thread = MyThread(records)

        client_id = 'clientid'
        host = 'localhost'
        port = 1883
        keepalive = 60

        client = mqtt.Client(client_id)
        client.connect(host, port, keepalive)
        client.loop_start()

        with open("bin/user/tests/data/second.json") as fp:
            test_data = json.load(fp)
            for record in test_data:
                for payload in test_data[record]:
                    topics = test_data[record][payload]
                    for topic in topics:
                        topic_info = topics[topic]
                        payload = json.dumps(topic_info['data'])
                        mqtt_message_info = client.publish(topic, payload)
                        mqtt_message_info.wait_for_publish()

        time.sleep(sleep) # ToDo 
        thread.start()
        thread.join()

        self.assertEqual(len(records), 1)
        self.assertIn('dateTime', records[0])
        self.assertIn('usUnits', records[0])
        self.assertEqual(records[0]['usUnits'], 1)

        self.assertIn('windDir', records[0])
        self.assertEqual(records[0]['windDir'], 0)
        self.assertIn('windSpeed', records[0])
        self.assertEqual(records[0]['windSpeed'], 1)

if __name__ == '__main__':
    unittest.main(exit=False)
