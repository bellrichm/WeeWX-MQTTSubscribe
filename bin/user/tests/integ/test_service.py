# pylint: disable=missing-docstring
# pylint: disable=wrong-import-order
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

import json
import time
import unittest
import configobj
import paho.mqtt.client as mqtt

import utils

import weewx
from weewx.engine import StdEngine
from user.MQTTSubscribe import setup_logging
from user.MQTTSubscribe import MQTTSubscribeService

class TestService(unittest.TestCase):
    def runit(self, payload, file_pointer):
        test_data = json.load(file_pointer, object_hook=utils.byteify)
        config_dict = configobj.ConfigObj(test_data['config'])
        testruns = test_data['testruns']

        cdict = config_dict['MQTTSubscribeService']
        if not 'message_callback' in config_dict['MQTTSubscribeService']:
            config_dict['MQTTSubscribeService']['message_callback'] = {}
        config_dict['MQTTSubscribeService']['message_callback']['type'] = payload
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

        #config_dict['MQTTSubscribeService']['console'] = True
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

        max_waits = 10
        for testrun in testruns:
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    #print(topic_info)
                    msg_count = utils.send_msg(utils.send_mqtt_msg, payload, client.publish, topic, topic_info, userdata2, self)
                    utils.wait_on_queue(service, topic, msg_count, max_waits, 1)

            results = testrun['results']
            result = {}
            for result in results:
                if 'service' in result['test']:
                    if payload in result['payloads']:
                        break

            record = {}
            units = result['units']
            interval = 300
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval

            record['dateTime'] = end_period_ts
            record['usUnits'] = units
            new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET, packet=record)
            service.new_loop_packet(new_loop_packet_event)
            #records.append(record)

            records = [record]
            utils.check(self, payload, records, result['records'])

        #print(records)
        service.shutDown()
        client.disconnect()
        client2.disconnect()

class TestAccumulatedRain(TestService):
    #@unittest.skip("")
    def test_accumulatedrain_individual(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_accumulatedrain_json(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_accumulatedrain_keyword(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            self.runit('keyword', file_pointer)

class TestBasic(TestService):
    #@unittest.skip("")
    def test_basic_individual(self):
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_basic_json(self):
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_basic_keyword(self):
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            self.runit('keyword', file_pointer)

class TestEmpty(TestService):
    #@unittest.skip("")
    def test_empty_individual(self):
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_empty_json(self):
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_empty_keyword(self):
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            self.runit('keyword', file_pointer)

class TestWindIndividualTopics(TestService):
    #@unittest.skip("")
    def test_wind_individual_topic(self):
        with open("bin/user/tests/integ/data/wind-individual.json") as file_pointer:
            self.runit('individual', file_pointer)

class TestWind(TestService):
    #@unittest.skip("")
    def test_wind_individual(self):
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_wind_json(self):
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_wind_keyword(self):
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            self.runit('keyword', file_pointer)

if __name__ == '__main__':
    setup_logging(1, {})
    unittest.main(exit=False, failfast=True)
