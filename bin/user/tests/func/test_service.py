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
    def service_test(self, test_type, testruns, config_dict):
        # pylint: disable=too-many-locals
        #sleep = 1

        cdict = config_dict['MQTTSubscribeService']
        if not 'message_callback' in config_dict['MQTTSubscribeService']:
            config_dict['MQTTSubscribeService']['message_callback'] = {}
        config_dict['MQTTSubscribeService']['message_callback']['type'] = test_type
        #message_callback_config = cdict.get('message_callback', {})
        #message_callback_config['type'] = test_type

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

        userdata = {
            'topics': [],
            'connected_flag': False,
        }
        client = mqtt.Client(userdata=userdata)
        client.on_connect = utils.on_connect
        client.connect(host, port, keepalive)
        client.loop_start()

        max_connect_wait = 1 # ToDo - configure
        i = 1
        while not userdata['connected_flag']: #wait in loop
            #print("waiting to connect")
            if i > max_connect_wait:
                self.fail("Timed out waiting for connections.")
            time.sleep(1)
            i += 1

        userdata2 = {
            'topics': cdict['topics'].sections,
            'connected_flag': False,
            'msg': False,
            'max_msg_wait': 1 #ToDo - configure
        }
        client2 = mqtt.Client(userdata=userdata2)
        client2.on_connect = utils.on_connect
        client2.on_message = utils.on_message
        client2.connect(host, port, keepalive)
        client2.loop_start()
        max_connect2_wait = 1 # ToDo - configure
        i = 1
        while not userdata2['connected_flag']: #wait in loop
            if i > max_connect2_wait:
                self.fail("Timed out waiting for connection 2.")
            #print("waiting to connect")
            time.sleep(1)
            i += 1

        for testrun in testruns:
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    #print(topic_info)
                    utils.send_msg(utils.send_mqtt_msg, test_type, client.publish, topic, topic_info, userdata2, self)

            time.sleep(1) # more fudge to allow it to get to the service
            #time.sleep(sleep)

            record = {}
            units = testrun['results']['units']
            interval = 300
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval

            record['dateTime'] = end_period_ts
            record['usUnits'] = units
            new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET, packet=record)
            service.new_loop_packet(new_loop_packet_event)
            #records.append(record)

            records = [record]
            utils.check(self, test_type, records, testrun['results']['records'])

        #print(records)
        service.shutDown()
        client.disconnect()
        client2.disconnect()

    #@unittest.skip("")
    def test_get_data_empty(self):
        with open("bin/user/tests/func/data/emptyaccumulated.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            for test_type in test_data['types']:
                self.service_test(test_type, test_data['testruns'], config_dict)

    #@unittest.skip("")
    def test_get_data_individual1(self):
        with open("bin/user/tests/func/data/wind.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            for test_type in test_data['types']:
                self.service_test(test_type, test_data['testruns'], config_dict)

    #@unittest.skip("")
    def test_get_data_individual2(self):
        with open("bin/user/tests/func/data/basic_withaccum.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            for test_type in test_data['types']:
                self.service_test(test_type, test_data['testruns'], config_dict)

    #@unittest.skip("")
    def test_get_data_individual3(self):
        with open("bin/user/tests/func/data/accumulatedrain_withaccum.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            for test_type in test_data['types']:
                self.service_test(test_type, test_data['testruns'], config_dict)

if __name__ == '__main__':
    unittest.main(exit=False, failfast=True)
