"""
An example/prototype of functional test.
Tests the driver, MQTTSubscribeDriver and the service, MQTTSubscribeService.
As close to an end to end test - but not called from WeeWX.
"""
# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring

import unittest

import configobj
import json
import os
import time

import paho.mqtt.client as mqtt

import utils

import weewx
from weewx.engine import StdEngine
from user.MQTTSubscribe import MQTTSubscribeService, MQTTSubscribeDriver

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

    def driver_test(self, test, cdict, record):
        sleep = 2

        #cdict = config_dict['MQTTSubscribe']
        message_callback_config = cdict.get('message_callback', None)
        message_callback_config['type'] = test['type']

        driver = MQTTSubscribeDriver(**cdict)

        client_id = 'clientid'
        host = 'localhost'
        port = 1883
        keepalive = 60

        client = mqtt.Client(client_id)
        client.connect(host, port, keepalive)
        client.loop_start()

        for topics in record:
            for topic in topics:
                topic_info = topics[topic]
                self.send_msg(test['type'], client, topic, topic_info)

        time.sleep(sleep)

        records = []
        gen = driver.genLoopPackets()

        i = 0
        while i < len(test['records']): # not great, but no way to know if more records
            data = next(gen, None)
            records.append(data)
            i += 1

        driver.closePort()

        utils.check(self, records, test)
        return

    def driver_test0(self, msg_type):
        sleep = 2

        config_path = os.path.abspath("bin/user/tests/data/fourth.conf")
        config_dict = configobj.ConfigObj(config_path, file_error=True)
        cdict = config_dict['MQTTSubscribeDriver']
        message_callback_config = cdict.get('message_callback', None)
        message_callback_config['type'] = msg_type

        driver = MQTTSubscribeDriver(**cdict)

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

        for data in driver.genLoopPackets():
            record = data
            break

        driver.closePort()

        self.assertIn('dateTime', record)
        self.assertIn('usUnits', record)
        self.assertEqual(record['usUnits'], 1)

        self.assertIn('windDir', record)
        self.assertEqual(record['windDir'], 0)
        self.assertIn('windSpeed', record)
        self.assertEqual(record['windSpeed'], 1)

    def service_test0(self, msg_type):
        sleep = 2

        config_path = os.path.abspath("bin/user/tests/data/third.conf")
        config_dict = configobj.ConfigObj(config_path, file_error=True)
        cdict = config_dict['MQTTSubscribeService']
        message_callback_config = cdict.get('message_callback', None)
        message_callback_config['type'] = msg_type

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

        engine = StdEngine(min_config_dict)

        service = MQTTSubscribeService(engine, config_dict)

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

        record = {}
        units = 1
        interval = 300
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / interval) + 1) * interval

        record['dateTime'] = end_period_ts
        record['usUnits'] = units
        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET, packet=record)
        service.new_loop_packet(new_loop_packet_event)

        service.shutDown()

        self.assertIn('dateTime', record)
        self.assertEqual(record['dateTime'], end_period_ts)
        self.assertIn('usUnits', record)
        self.assertEqual(record['usUnits'], units)

        self.assertIn('windDir', record)
        self.assertEqual(record['windDir'], 0)
        self.assertIn('windSpeed', record)
        self.assertEqual(record['windSpeed'], 1)

    def test_get_data_individual1(self):
        with open("bin/user/tests/data/first.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribe']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                # print(test)
                self.driver_test(test, config_dict, test_data)

    #def test_get_data_individual(self):
        #self.driver_test('individual')

    #def test_get_data_json(self):
        #self.driver_test('json')

    #def test_get_data_keyword(self):
        #self.driver_test('keyword')

    #def test_get_accumulated_data_individual(self):
        #self.service_test('individual')

    #def test_get_accumulated_data_json(self):
        #self.service_test('json')

    #def test_get_accumulated_data_keyword(self):
        #self.service_test('keyword')

if __name__ == '__main__':
    unittest.main(exit=False)
