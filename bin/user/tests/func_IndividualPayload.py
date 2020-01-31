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

import weeutil

from user.MQTTSubscribe import TopicManager, Logger

class TestIndividualPayload(unittest.TestCase):
    def get_data_test(self, test, config_dict, record):
        if test['type'] == 'individual':
            msg_def = utils.INDIVIDUAL_PAYLOAD
        elif test['type'] == 'json':
            msg_def = utils.JSON_PAYLOAD
        elif test['type'] == 'keyword':
            msg_def = utils.KEYWORD_PAYLOAD
        logger = Logger()

        topics_dict = config_dict.get('topics', {})

        message_callback_config = config_dict.get('message_callback', None)
        if message_callback_config is None:
            raise ValueError("[[message_callback]] is required.")

        message_callback_config['type'] = msg_def['payload_type']

        message_callback_provider_name = config_dict.get('message_callback_provider',
                                                         'user.MQTTSubscribe.MessageCallbackProvider')

        manager = TopicManager(topics_dict, logger)

        message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
        message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                    logger,
                                                                    manager)

        on_message = message_callback_provider.get_callback()

        for topics in record:
            msg_def['on_message'](on_message, topics)

        records = []
        for topic in manager.subscribed_topics:
            for data in manager.get_data(topic):
                if data:
                    records.append(data)
                else:
                    break

        self.assertEqual(len(records), len(test['records']))
        i = 0
        for recordx in test['records']:
            for field in recordx:
                self.assertIn(field, records[i])
                if recordx[field]:
                    self.assertEqual(records[i][field], recordx[field])
            i = +1

    def get_accumulated_data_test(self, test, config_dict, record):
        if test['type'] == 'individual':
            msg_def = utils.INDIVIDUAL_PAYLOAD
        elif test['type'] == 'json':
            msg_def = utils.JSON_PAYLOAD
        elif test['type'] == 'keyword':
            msg_def = utils.KEYWORD_PAYLOAD
        logger = Logger()

        start_ts = time.time()
        topics_dict = config_dict.get('topics', {})

        message_callback_config = config_dict.get('message_callback', None)
        if message_callback_config is None:
            raise ValueError("[[message_callback]] is required.")

        message_callback_config['type'] = msg_def['payload_type']

        message_callback_provider_name = config_dict.get('message_callback_provider',
                                                         'user.MQTTSubscribe.MessageCallbackProvider')

        manager = TopicManager(topics_dict, logger)

        message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
        message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                    logger,
                                                                    manager)

        on_message = message_callback_provider.get_callback()
        for topics in record:
            msg_def['on_message'](on_message, topics)

        end_ts = time.time()

        records = []
        for topic in manager.subscribed_topics:
            data = manager.get_accumulated_data(topic, start_ts, end_ts, test['units'])
            records.append(data)

        self.assertEqual(len(records), len(test['records']))
        i = 0
        for recordx in test['records']:
            for field in recordx:
                self.assertIn(field, records[i])
                if recordx[field]:
                    self.assertEqual(records[i][field], recordx[field])
            i = +1

    def test_get_data_individual(self):
        with open("bin/user/tests/data/firstx.json") as fp:
            testx_data = json.load(fp)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribe']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_data_test(test, config_dict, test_data)

    def test_get_accumulated_data_individual(self):
        with open("bin/user/tests/data/firsty.json") as fp:
            testx_data = json.load(fp)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribe']
            test_data = testx_data['data']['payload']
            for test in testx_data['data']['results']:
                self.get_accumulated_data_test(test, config_dict, test_data)

if __name__ == '__main__':
    unittest.main(exit=False)
