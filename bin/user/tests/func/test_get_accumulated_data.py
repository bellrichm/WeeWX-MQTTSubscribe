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
    def get_accumulated_data_test(self, test_type, testruns, config_dict):
        logger = Logger()
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)

        on_message = utils.get_callback(test_type, config_dict, manager, logger)
        for testrun in testruns:
            start_ts = time.time()
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    utils.send_msg(utils.send_direct_msg, test_type, on_message, topic, topic_info)
                #utils.send_msg(utils.send_direct_msg, test_type, on_message, topics)
            end_ts = time.time()

            records = []
            for topic in manager.subscribed_topics:
                data = manager.get_accumulated_data(topic, start_ts, end_ts, testrun['results']['units'])
                records.append(data)

            utils.check(self, test_type, records, testrun['results']['records'])

    #@unittest.skip("")
    def test_get_accumulated_data_empty(self):
        with open("bin/user/tests/func/data/emptyaccumulated.json") as fp:
            test_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            for test_type in test_data['types']:
                self.get_accumulated_data_test(test_type, test_data['testruns'], config_dict)

    #@unittest.skip("")
    def test_get_accumulated_data_individual1(self):
        with open("bin/user/tests/func/data/wind.json") as fp:
            test_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            for test_type in test_data['types']:
                self.get_accumulated_data_test(test_type, test_data['testruns'], config_dict)

    #@unittest.skip("")
    def test_get_accumulated_data_individual(self):
        with open("bin/user/tests/func/data/basic_withaccum.json") as fp:
            test_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            for test_type in test_data['types']:
                self.get_accumulated_data_test(test_type, test_data['testruns'], config_dict)

    #@unittest.skip("")
    def test_get_accumulated_datax_individual3(self):
        with open("bin/user/tests/func/data/accumulatedrain_withaccum.json") as fp:
            test_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            for test_type in test_data['types']:
                self.get_accumulated_data_test(test_type, test_data['testruns'], config_dict)

if __name__ == '__main__':
    unittest.main(exit=False)
