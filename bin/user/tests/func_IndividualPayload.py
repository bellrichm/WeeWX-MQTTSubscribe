# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest

import configobj
import json
import time

import weeutil

from user.MQTTSubscribe import TopicManager, Logger

class Msg(object):
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain

class TestIndividualPayload(unittest.TestCase):
    def default_config(self):
        return """
[MQTTSubscribe]
    # Configuration for the message callback.
    [[message_callback]]
       [[[label_map]]]
          baro_mb = barometer
          windRaw = windSpeed

        [[[fields]]]
            # The incoming field name from MQTT
            [[[[windRaw]]]]
              # The WeeWX name.
              # Default is the name from MQTT.
                name = windSpeed
              # The conversion type necessary for WeeWX compatibility
              # Valid values: bool, float, int, none
              # Default is float
                conversion_type = float
              # True if the incoming data is cumulative.
              # Valid values: True, False
              # Default is False
                contains_total = False

    # The topics to subscribe to.
    [[topics]]
        unit_system = METRICWX
        [[[weewx/#]]]

"""
    def test_get_data(self):
        config_text = self.default_config().splitlines()
        config_dict = configobj.ConfigObj(config_text)['MQTTSubscribe']

        topics_dict = config_dict.get('topics', {})

        logger = Logger()

        message_callback_config = config_dict.get('message_callback', None)
        if message_callback_config is None:
            raise ValueError("[[message_callback]] is required.")

        message_callback_config['type'] = 'individual'

        message_callback_provider_name = config_dict.get('message_callback_provider',
                                                         'user.MQTTSubscribe.MessageCallbackProvider')

        manager = TopicManager(topics_dict, logger)

        message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
        message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                    logger,
                                                                    manager)

        on_message = message_callback_provider.get_callback()

        with open("bin/user/tests/data/first.json") as fp:
            t = json.load(fp)
            for record in t:
                for payload in t[record]:
                    for topic in t[record][payload]:
                        topic_info = t[record][payload][topic]
                        if 'separator' in topic_info:
                            print("      %s" % topic_info['separator'])
                        if 'delimiter' in topic_info:
                            print("      %s" % topic_info['delimiter'])
                        for field in topic_info['data']:
                            on_message(None, None, Msg("%s/%s" % (topic, field), topic_info['data'][field], 0, 0))

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

    def test_get_accumulated_data(self):
        config_text = self.default_config().splitlines()
        config_dict = configobj.ConfigObj(config_text)['MQTTSubscribe']

        topics_dict = config_dict.get('topics', {})

        logger = Logger()

        message_callback_config = config_dict.get('message_callback', None)
        if message_callback_config is None:
            raise ValueError("[[message_callback]] is required.")

        message_callback_provider_name = config_dict.get('message_callback_provider',
                                                         'user.MQTTSubscribe.MessageCallbackProvider')

        message_callback_config['type'] = 'individual'

        manager = TopicManager(topics_dict, logger)

        message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
        message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                    logger,
                                                                    manager)

        on_message = message_callback_provider.get_callback()

        start_ts = time.time()
        on_message(None, None, Msg("weewx/windDir", "0", 0, 0))
        on_message(None, None, Msg("weewx/windSpeed", "1", 0, 0))
        end_ts = time.time()

        records = {}
        for topic in manager.subscribed_topics:
            data = manager.get_accumulated_data(topic, start_ts, end_ts, 17)
            records[topic] = data
            print(data)

        for topic in records:
            print("%s: %s" %(topic, records[topic]))


        topic = 'weewx/#'
        self.assertEqual(len(records), 1)
        self.assertIn('dateTime', records[topic])
        self.assertIn('usUnits', records[topic])
        self.assertEqual(records[topic]['usUnits'], 17)

        self.assertIn('windDir', records[topic])
        self.assertEqual(records[topic]['windDir'], 0)
        self.assertIn('windSpeed', records[topic])
        self.assertEqual(records[topic]['windSpeed'], 1)


if __name__ == '__main__':
    unittest.main(exit=False)
