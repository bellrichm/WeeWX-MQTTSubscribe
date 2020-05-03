# pylint: disable=missing-docstring
# pylint: disable=wrong-import-order
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches

import json
import time
import unittest

import configobj
import paho.mqtt.client as mqtt

import utils

from user.MQTTSubscribe import MQTTSubscribeDriver
from user.MQTTSubscribe import setup_logging

class TestDriver(unittest.TestCase):
    def runit(self, payload, file_pointer):
        test_data = json.load(file_pointer, object_hook=utils.byteify)
        config_dict = configobj.ConfigObj(test_data['config'])
        testruns = test_data['testruns']

        cdict = config_dict['MQTTSubscribeService']
        if not 'message_callback' in config_dict['MQTTSubscribeService']:
            config_dict['MQTTSubscribeService']['message_callback'] = {}
        config_dict['MQTTSubscribeService']['message_callback']['type'] = payload

        driver = MQTTSubscribeDriver(**cdict)

        host = 'localhost'
        port = 1883
        keepalive = 60

        userdata = {
            'topics': [],
            'connected_flag': False
        }
        client = mqtt.Client(userdata=userdata)
        client.on_connect = utils.on_connect
        client.connect(host, port, keepalive)
        client.loop_start()

        max_connect_wait = 1 # ToDo - configure
        i = 1
        while not userdata['connected_flag']:
            if i > max_connect_wait:
                self.fail("Timed out waiting for connections.")
            time.sleep(1)
            i += 1

        userdata2 = {
            'topics': cdict['topics'].sections,
            'connected_flag': False,
            'msg': False,
            'max_msg_wait': 1 # ToDo - configure
        }
        client2 = mqtt.Client(userdata=userdata2)
        client2.on_connect = utils.on_connect
        client2.on_message = utils.on_message
        client2.connect(host, port, keepalive)
        client2.loop_start()

        max_connect2_wait = 1 # ToDo - configure
        i = 1
        while not userdata2['connected_flag']:
            #print("waiting to connect")
            if i > max_connect2_wait:
                self.fail("Timed out waiting for connection 2.")
            time.sleep(1)
            i += 1

        max_waits = 10
        for testrun in testruns:
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    msg_count = utils.send_msg(utils.send_mqtt_msg, payload, client.publish, topic, topic_info, userdata2, self)
                    wait_count = utils.wait_on_queue(driver, msg_count, max_waits, 1)

                    # If queue not filled, fail now
                    # otherwise will end up in 'infinite' loop in genLoopPackets
                    if wait_count >= max_waits:
                        self.fail("Could not fill queue.")

            records = []
            gen = driver.genLoopPackets()

            results = testrun['results']
            result = {}
            found = False
            for result in results:
                if 'driver' in result['test']:
                    if payload in result['payloads']:
                        found = True
                        break

            self.assertTrue(found, "No results for %s" %payload)

            i = 0
            # ToDo not great, but no way to know if more records
            # could possibly check the queues..
            # Todo this needs to be fixed for new debug code
            while i < len(result['records']):
                data = next(gen, None)
                records.append(data)
                i += 1

            utils.check(self, payload, records, result['records'])

        driver.closePort()
        client.disconnect()
        client2.disconnect()

class TestAccumulatedRain(TestDriver):
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

class TestBasic(TestDriver):
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

class TestEmpty(TestDriver):
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

class TestWindIndividualTopics(TestDriver):
    #@unittest.skip("")
    def test_wind_individual_topic(self):
        with open("bin/user/tests/integ/data/wind-individual.json") as file_pointer:
            self.runit('individual', file_pointer)

class TestWindIndividualWind(TestDriver):
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
