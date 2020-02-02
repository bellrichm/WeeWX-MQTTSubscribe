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
import time

import paho.mqtt.client as mqtt

import utils

import weewx
from weewx.engine import StdEngine
from user.MQTTSubscribe import MQTTSubscribeService

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

    def service_test(self, test, config_dict, record):
        sleep = 3

        cdict = config_dict['MQTTSubscribeService']
        message_callback_config = cdict.get('message_callback', None)
        message_callback_config['type'] = test['type']

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

        host = 'localhost'
        port = 1883
        keepalive = 60

        client = mqtt.Client()
        client.connect(host, port, keepalive)
        client.loop_start()

        for topics in record:
            for topic in topics:
                topic_info = topics[topic]
                self.send_msg(test['type'], client, topic, topic_info)

        time.sleep(sleep)

        record = {}
        units = 17
        interval = 300
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / interval) + 1) * interval

        record['dateTime'] = end_period_ts
        record['usUnits'] = units
        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET, packet=record)
        service.new_loop_packet(new_loop_packet_event)
        #records.append(record)

        service.shutDown()
        client.disconnect()

        records = [record]
        utils.check(self, records, test)
        #print(records)

    def servicex_test(self, test, config_dict, record):
        sleep = 2

        cdict = config_dict['MQTTSubscribeService']
        message_callback_config = cdict.get('message_callback', None)
        message_callback_config['type'] = test['type']

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

        host = 'localhost'
        port = 1883
        keepalive = 60

        client = mqtt.Client()
        client.connect(host, port, keepalive)
        client.loop_start()

        records = []
        for topics in record:
            for topic in topics:
                topic_info = topics[topic]
                self.send_msg(test['type'], client, topic, topic_info)

                time.sleep(sleep)

                record = {}
                units = 17
                interval = 300
                current_time = int(time.time() + 0.5)
                end_period_ts = (int(current_time / interval) + 1) * interval

                record['dateTime'] = end_period_ts
                record['usUnits'] = units
                new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET, packet=record)
                service.new_loop_packet(new_loop_packet_event)
                records.append(record)

        service.shutDown()
        client.disconnect()

        #records = [record]
        utils.check(self, records, test)
        #print(records)

# do i want to accumulate packets into records? or have multiple records?

    #unittest.skip("")
    def test_get_data_individual1(self):
        with open("bin/user/tests/func/data/first.json") as file_pointer:
            testx_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                # print(test)
                self.service_test(test, config_dict, test_data)

    #unittest.skip("")
    def test_get_data_individual2(self):
        with open("bin/user/tests/func/data/firsty.json") as file_pointer:
            testx_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                # print(test)
                self.service_test(test, config_dict, test_data)

    def test_get_data_individual3(self):
        with open("bin/user/tests/func/data/accumulatedrain.json") as file_pointer:
            testx_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                # print(test)
                self.servicex_test(test, config_dict, test_data)

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
