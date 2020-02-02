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
    def get_accumulated_data_test(self, test, config_dict, record):
        if test['type'] == 'individual':
            msg_def = utils.INDIVIDUAL_PAYLOAD
        elif test['type'] == 'json':
            msg_def = utils.JSON_PAYLOAD
        elif test['type'] == 'keyword':
            msg_def = utils.KEYWORD_PAYLOAD

        logger = Logger()
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)

        start_ts = time.time()
        on_message = utils.setup(msg_def, config_dict, manager, logger)
        for topics in record:
            msg_def['on_message'](on_message, topics)
        end_ts = time.time()

        records = []
        for topic in manager.subscribed_topics:
            data = manager.get_accumulated_data(topic, start_ts, end_ts, test['units'])
            records.append(data)

        utils.check(self, records, test)

    def get_accumulated_datax_test(self, test, config_dict, record):
        if test['type'] == 'individual':
            msg_def = utils.INDIVIDUAL_PAYLOAD
        elif test['type'] == 'json':
            msg_def = utils.JSON_PAYLOAD
        elif test['type'] == 'keyword':
            msg_def = utils.KEYWORD_PAYLOAD

        logger = Logger()
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)

        start_ts = time.time()
        on_message = utils.setup(msg_def, config_dict, manager, logger)
        records = []
        for topics in record:
            msg_def['on_message'](on_message, topics)
            end_ts = time.time()
            topicx = list(topics.keys())[0] # ToDo - support multipe topics
            topic = "%s/#" % topicx
            data = manager.get_accumulated_data(topic, start_ts, end_ts, test['units'])
            records.append(data)

        utils.check(self, records, test)

    #@unittest.skip("")
    def test_get_accumulated_data_individual1(self):
        with open("bin/user/tests/func/data/first.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_accumulated_data_test(test, config_dict, test_data)

    #@unittest.skip("")
    def test_get_accumulated_data_individual(self):
        with open("bin/user/tests/func/data/firsty.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_accumulated_data_test(test, config_dict, test_data)

    #@unittest.skip("'")
    def test_get_accumulated_datax_individual3(self):
        with open("bin/user/tests/func/data/accumulatedrain.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_accumulated_datax_test(test, config_dict, test_data)

if __name__ == '__main__':
    unittest.main(exit=False)
