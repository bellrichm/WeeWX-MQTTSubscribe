"""
An example/prototype of functional test.
Tests 'everything' needed for calls to get_data and get_accumulated_data of the MQTTSubscriber class.
These calls just wrap the TopicManager calls.
Uses MQTT, so has added complexity, but more of an end to end test.
"""
# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring

import unittest

import configobj
import json
import os
import time

import paho.mqtt.client as mqtt

from user.MQTTSubscribe import MQTTSubscribe, Logger, setup_logging

class TestJsonPayload(unittest.TestCase):
    def send_msg(self, msg_type, client, topic, topic_info):
        if msg_type == 'individual':
            for field in topic_info['data']:
                mqtt_message_info = client.publish("%s/%s" % (topic, field), topic_info['data'][field])
                mqtt_message_info.wait_for_publish()
        elif msg_type == 'json':
            payload = json.dumps(topic_info['data'])
            mqtt_message_info = client.publish(topic, payload)
            mqtt_message_info.wait_for_publish()
        elif msg_type == 'keyword':
            msg = ''
            data = topic_info['data']
            for field in data:
                msg = "%s%s%s%s%s" % (msg, field, topic_info['delimiter'], data[field], topic_info['separator'])
            msg = msg[:-1]
            msg = msg.encode("utf-8")
            mqtt_message_info = client.publish(topic, msg)
            mqtt_message_info.wait_for_publish()

    def get_data_test(self, msg_type):
        sleep = 2
        records = []

        config_path = os.path.abspath("bin/user/tests/data/second.conf")
        config_dict = configobj.ConfigObj(config_path, file_error=True)['MQTTSubscribe']
        message_callback_config = config_dict.get('message_callback', None)
        message_callback_config['type'] = msg_type
        #setup_logging(True)
        logger = Logger()
        setup_logging(True)
        subscriber = MQTTSubscribe(config_dict, logger)
        subscriber.start()

        client_id = 'clientid'
        host = 'localhost'
        port = 1883
        keepalive = 60

        client = mqtt.Client(client_id)
        client.connect(host, port, keepalive)
        client.loop_start()

        with open("bin/user/tests/data/second.json") as file_pointer:
            test_data = json.load(file_pointer)
            for record in test_data:
                for payload in test_data[record]:
                    topics = test_data[record][payload]
                    for topic in topics:
                        topic_info = topics[topic]
                        self.send_msg(msg_type, client, topic, topic_info)

        time.sleep(sleep)

        topics = config_dict.get('topics').sections
        for topic in topics:
            for data in subscriber.get_data(topic):
                if data:
                    records.append(data)
                else:
                    break

        self.assertEqual(len(records), 1)
        self.assertIn('dateTime', records[0])
        self.assertIn('usUnits', records[0])
        self.assertEqual(records[0]['usUnits'], 1)

        self.assertIn('windDir', records[0])
        self.assertEqual(records[0]['windDir'], 0)
        self.assertIn('windSpeed', records[0])
        self.assertEqual(records[0]['windSpeed'], 1)

    def get_accumulated_data_test(self, msg_type):
        sleep = 2
        records = []

        config_path = os.path.abspath("bin/user/tests/data/second.conf")
        config_dict = configobj.ConfigObj(config_path, file_error=True)['MQTTSubscribe']
        message_callback_config = config_dict.get('message_callback', None)
        message_callback_config['type'] = msg_type
        #setup_logging(True)
        logger = Logger()
        setup_logging(True)
        subscriber = MQTTSubscribe(config_dict, logger)
        subscriber.start()

        client_id = 'clientid'
        host = 'localhost'
        port = 1883
        keepalive = 60

        client = mqtt.Client(client_id)
        client.connect(host, port, keepalive)
        client.loop_start()

        start_ts = time.time() - 1
        with open("bin/user/tests/data/second.json") as file_pointer:
            test_data = json.load(file_pointer)
            for record in test_data:
                for payload in test_data[record]:
                    topics = test_data[record][payload]
                    for topic in topics:
                        topic_info = topics[topic]
                        self.send_msg(msg_type, client, topic, topic_info)
        end_ts = time.time() + 1

        time.sleep(sleep)

        records = {}
        for topic in subscriber.manager.subscribed_topics:
            data = subscriber.get_accumulated_data(topic, start_ts, end_ts, 1)
            records[topic] = data

        topic = 'weather/loop/#'
        self.assertEqual(len(records), 1)
        self.assertIn('dateTime', records[topic])
        self.assertIn('usUnits', records[topic])
        self.assertEqual(records[topic]['usUnits'], 1)

        self.assertIn('windDir', records[topic])
        self.assertEqual(records[topic]['windDir'], 0)
        self.assertIn('windSpeed', records[topic])
        self.assertEqual(records[topic]['windSpeed'], 1)

    def test_get_data_individual(self):
        self.get_data_test('individual')

    def test_get_data_json(self):
        self.get_data_test('json')

    def test_get_data_keyword(self):
        self.get_data_test('keyword')

    def test_get_accumulated_data_individual(self):
        self.get_accumulated_data_test('individual')

    def test_get_accumulated_data_json(self):
        self.get_accumulated_data_test('json')

    def test_get_accumulated_data_keyword(self):
        self.get_accumulated_data_test('keyword')

if __name__ == '__main__':
    unittest.main(exit=False)
