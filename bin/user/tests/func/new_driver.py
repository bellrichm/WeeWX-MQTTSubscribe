# pylint: disable=missing-docstring

import json
import time
import unittest

import configobj
import paho.mqtt.client as mqtt

import utils

from user.MQTTSubscribe import MQTTSubscribeDriver
from user.MQTTSubscribe import setup_logging

class TestOne(unittest.TestCase):
    def get_tests(self, file):
        test_data = json.load(file, object_hook=utils.byteify)
        ##config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
        config_dict = configobj.ConfigObj(test_data['config'])
        #print(config_dict)
        testruns = test_data['testruns']
        #print(testruns)
        return config_dict, testruns

    def run_test(self, config_dict, testruns, payload):
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
                if result['test'] == 'single' or result['test'] == 'both':
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

    def test_one(self):
        payload = 'individual'
        with open("bin/user/tests/func/data/new_accumulatedrain.json") as file:
            config_dict, testruns = self.get_tests(file)
            self.run_test(config_dict, testruns, payload)
            #for testrun in testruns:
            #    results = testrun['results']
            #    for result in results:
            #        if result['test'] == 'single' or result['test'] == 'both':
            #            if payload in result['payloads']:
            #                self.run_test(config_dict, testrun['messages'], result, payload)
            print(testruns)
            print("working")
        print("done")

if __name__ == '__main__':
    setup_logging(1, {})
    unittest.main(exit=False, failfast=True)
