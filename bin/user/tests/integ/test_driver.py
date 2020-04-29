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

class TestOne(unittest.TestCase):
    def runit(self, config_dict, testruns, payload):
        #sleep = 2

        cdict = config_dict['MQTTSubscribeService']
        if not 'message_callback' in config_dict['MQTTSubscribeService']:
            config_dict['MQTTSubscribeService']['message_callback'] = {}
        config_dict['MQTTSubscribeService']['message_callback']['type'] = payload

        #message_callback_config = cdict.get('message_callback', None)
        #message_callback_config['type'] = test_type

        #config_dict['MQTTSubscribeService']['console'] = True
        driver = MQTTSubscribeDriver(**cdict)

        #client_id = 'clientid'
        host = 'localhost'
        port = 1883
        keepalive = 60

        #client = mqtt.Client(client_id)
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
        while not userdata['connected_flag']: #wait in loop
            if i > max_connect_wait:
                self.fail("Timed out waiting for connections.")
            #print("waiting to connect")
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
        while not userdata2['connected_flag']: #wait in loop
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
                    wait_count = utils.wait_on_queue(driver, topic, msg_count, max_waits, 1)

                    # If queue not filled, fail now
                    # otherwise will end up in 'infinite' loop in genLoopPackets
                    if wait_count >= max_waits:
                        self.fail("Could not fill queue.")

            records = []
            gen = driver.genLoopPackets()

            results = testrun['results']
            result = {}
            for result in results:
                if 'single' in result['test']:
                    if payload in result['payloads']:
                        break

            i = 0
            while i < len(result['records']): # not great, but no way to know if more records
                data = next(gen, None)
                #print(data)
                records.append(data)
                i += 1

            utils.check(self, payload, records, result['records'])

        driver.closePort()
        client.disconnect()
        client2.disconnect()

    #@unittest.skip("")
    def test_accumulatedrain_individual(self):
        payload = 'individual'
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_accumulatedrain_json(self):
        payload = 'json'
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_accumulatedrain_keyword(self):
        payload = 'keyword'
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_basic_individual(self):
        payload = 'individual'
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_basic_json(self):
        payload = 'json'
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_basic_keyword(self):
        payload = 'keyword'
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_empty_individual(self):
        payload = 'individual'
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_empty_json(self):
        payload = 'json'
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_empty_keyword(self):
        payload = 'keyword'
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_wind_individual(self):
        payload = 'individual'
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_wind_json(self):
        payload = 'json'
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_wind_keyword(self):
        payload = 'keyword'
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

if __name__ == '__main__':
    setup_logging(1, {})
    unittest.main(exit=False, failfast=True)
