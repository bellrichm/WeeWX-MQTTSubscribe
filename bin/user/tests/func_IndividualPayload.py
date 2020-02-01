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
    def get_data_test(self, test, config_dict, record):
        if 'skip' in test and test['skip']:
            return

        logger = Logger()
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)

        utils.setup(test, config_dict, record, manager, logger)

        records = []
        for topic in manager.subscribed_topics:
            for data in manager.get_data(topic):
                if data:
                    records.append(data)
                else:
                    break

        utils.check(self, records, test)

    def get_accumulated_data_test(self, test, config_dict, record):
        logger = Logger()
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)

        start_ts = time.time()
        utils.setup(test, config_dict, record, manager, logger)
        end_ts = time.time()

        records = []
        for topic in manager.subscribed_topics:
            data = manager.get_accumulated_data(topic, start_ts, end_ts, test['units'])
            records.append(data)

        utils.check(self, records, test)

    def test_get_data_individual0(self):
        with open("bin/user/tests/data/accumulatedrain.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribe']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_data_test(test, config_dict, test_data)

    #unittest.skip("")
    def test_get_data_individual1(self):
        with open("bin/user/tests/data/first.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribe']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_data_test(test, config_dict, test_data)

    #unittest.skip("")
    def test_get_accumulated_data_individual1(self):
        with open("bin/user/tests/data/first.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribe']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_accumulated_data_test(test, config_dict, test_data)

    @unittest.skip("")
    def test_get_data_individual(self):
        with open("bin/user/tests/data/firstx.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribe']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_data_test(test, config_dict, test_data)

    @unittest.skip("")
    def test_get_accumulated_data_individual(self):
        with open("bin/user/tests/data/firsty.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribe']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_accumulated_data_test(test, config_dict, test_data)

if __name__ == '__main__':
    unittest.main(exit=False)
