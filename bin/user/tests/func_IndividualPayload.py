# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import utils
import unittest

import configobj
import json
import os
import time

import weeutil

from user.MQTTSubscribe import TopicManager, Logger

class TestIndividualPayload(unittest.TestCase):
    def get_data_test(self, msg_type, send_msgs):
        config_path = os.path.abspath("bin/user/tests/data/first.conf")
        config_dict = configobj.ConfigObj(config_path, file_error=True)['MQTTSubscribe']

        topics_dict = config_dict.get('topics', {})

        logger = Logger()

        message_callback_config = config_dict.get('message_callback', None)
        if message_callback_config is None:
            raise ValueError("[[message_callback]] is required.")

        message_callback_config['type'] = msg_type

        message_callback_provider_name = config_dict.get('message_callback_provider',
                                                         'user.MQTTSubscribe.MessageCallbackProvider')

        manager = TopicManager(topics_dict, logger)

        message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
        message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                    logger,
                                                                    manager)

        on_message = message_callback_provider.get_callback()

        with open("bin/user/tests/data/first.json") as fp:
            test_data = json.load(fp)
            for record in test_data:
                for payload in test_data[record]:
                    send_msgs(on_message, test_data[record][payload])

        records = []
        for topic in manager.subscribed_topics:
            for data in manager.get_data(topic):
                if data:
                    records.append(data)
                else:
                    break

        self.assertEqual(len(records), 1)
        self.assertIn('dateTime', records[0])
        self.assertIn('usUnits', records[0])
        self.assertEqual(records[0]['usUnits'], 17)

        self.assertIn('windDir', records[0])
        self.assertEqual(records[0]['windDir'], 0)
        self.assertIn('windSpeed', records[0])
        self.assertEqual(records[0]['windSpeed'], 1)

    def get_accumulated_data_test(self, msg_type, send_msgs):
        config_path = os.path.abspath("bin/user/tests/data/first.conf")
        config_dict = configobj.ConfigObj(config_path, file_error=True)['MQTTSubscribe']

        topics_dict = config_dict.get('topics', {})

        logger = Logger()

        message_callback_config = config_dict.get('message_callback', None)
        if message_callback_config is None:
            raise ValueError("[[message_callback]] is required.")

        message_callback_provider_name = config_dict.get('message_callback_provider',
                                                         'user.MQTTSubscribe.MessageCallbackProvider')

        message_callback_config['type'] = msg_type

        manager = TopicManager(topics_dict, logger)

        message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
        message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                    logger,
                                                                    manager)

        on_message = message_callback_provider.get_callback()

        start_ts = time.time()
        with open("bin/user/tests/data/first.json") as fp:
            test_data = json.load(fp)
            for record in test_data:
                for payload in test_data[record]:
                    send_msgs(on_message, test_data[record][payload])
        end_ts = time.time()

        records = {}
        for topic in manager.subscribed_topics:
            data = manager.get_accumulated_data(topic, start_ts, end_ts, 17)
            records[topic] = data

        topic = 'weewx/#'
        self.assertEqual(len(records), 1)
        self.assertIn('dateTime', records[topic])
        self.assertIn('usUnits', records[topic])
        self.assertEqual(records[topic]['usUnits'], 17)

        self.assertIn('windDir', records[topic])
        self.assertEqual(records[topic]['windDir'], 0)
        self.assertIn('windSpeed', records[topic])
        self.assertEqual(records[topic]['windSpeed'], 1)

    def test_get_data_individual(self):
        self.get_data_test('individual', utils.send_individual_msgs)

    def test_get_data_json(self):
        self.get_data_test('json', utils.send_json_msgs)

    def test_get_data_keyword(self):
        self.get_data_test('keyword', utils.send_keyword_msgs)

    def test_get_accumulated_data_individual(self):
        self.get_accumulated_data_test('individual', utils.send_individual_msgs)

    def test_get_accumulated_data_json(self):
        self.get_accumulated_data_test('json', utils.send_json_msgs)

    def test_get_accumulated_data_keyword(self):
        self.get_accumulated_data_test('keyword', utils.send_keyword_msgs)        

if __name__ == '__main__':
    unittest.main(exit=False)
