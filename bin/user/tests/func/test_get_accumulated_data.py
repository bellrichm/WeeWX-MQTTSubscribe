"""
An example/prototype of functional test.
Tests 'everything' needed for calls to get_data and get_accumulated_data of the TopicManager class.
Calls the on_message callback directly, so no dependency on MQTT.
"""
# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import utils
import unittest

import configobj
import json
import time

from user.MQTTSubscribe import TopicManager, Logger

class TestIndividualPayload(unittest.TestCase):
    def get_accumulated_data_test(self, testtype, testruns, config_dict):
        logger = Logger()
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)


        on_message = utils.setup(testtype, config_dict, manager, logger)
        for testrun in testruns:
            start_ts = time.time()
            for topics in testrun['payload']:
                utils.send_msg(testtype, on_message, topics)
            end_ts = time.time()

            records = []
            for topic in manager.subscribed_topics:
                data = manager.get_accumulated_data(topic, start_ts, end_ts, testrun['results']['units'])
                records.append(data)

            utils.check(self, testtype, records, testrun['results']['records'])

    #@unittest.skip("")
    def test_get_accumulated_data_individual1(self):
        with open("bin/user/tests/func/data/first.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            for testtype in testx_data['types']:
                self.get_accumulated_data_test(testtype, testx_data['data'], config_dict)

    #@unittest.skip("")
    def test_get_accumulated_data_individual(self):
        with open("bin/user/tests/func/data/firsty.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            for testtype in testx_data['types']:
                self.get_accumulated_data_test(testtype, testx_data['data'], config_dict)

    #@unittest.skip("")
    def test_get_accumulated_datax_individual3(self):
        with open("bin/user/tests/func/data/accumulatedraina.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            for testtype in testx_data['types']:
                self.get_accumulated_data_test(testtype, testx_data['data'], config_dict)

if __name__ == '__main__':
    unittest.main(exit=False)
