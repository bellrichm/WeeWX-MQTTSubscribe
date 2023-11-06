#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
'''
This is a set of 'function' tests. 
These test that the MQTTSubscribe configuration is correct for the payload.
'''

# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access

import unittest

import configobj
import json
import random
import string
import time

from io import StringIO

from user.MQTTSubscribe import Logger, MessageCallbackProvider, TopicManager

def random_string(length=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)]) # pylint: disable=unused-variable

class Msg(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain

class TestJSONMessage(unittest.TestCase):
    def test_basic_message(self):
        logger = Logger('FuncTest', level='ERROR', console=True)

        topic = random_string()
        config_str = '''
[MQTTSubscribe]
    [[topics]]
        [[[%s]]]
            [[[[message]]]]
                type = json
'''

        config = configobj.ConfigObj(StringIO(config_str % topic))

        topic_manager = TopicManager(None, config['MQTTSubscribe']['topics'], logger)

        SUT = MessageCallbackProvider(None, logger, topic_manager)

        payload_dict = {
            'dateTime': time.time(),
            'usUnits': random.randint(1, 10),
            'inTemp': round(random.uniform(10, 100), 2),
            'outTemp': round(random.uniform(1, 100), 2),
        }

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(topic, payload, 0, 0)
        SUT._on_message_json(None, None, msg)

        queue = topic_manager._get_queue(topic)
        data = queue['data'].popleft()['data']
        self.assertDictEqual(data, payload_dict)

    def test_nested_json_message(self):
        logger = Logger('FuncTest', level='ERROR', console=True)

        topic = random_string()
        config_str = '''
[MQTTSubscribe]
    [[topics]]
        [[[%s]]]
            [[[[message]]]]
                type = json

            [[[[temps]]]]
                [[[[[subfields]]]]]
                    [[[[[[temp1]]]]]]
                    [[[[[[temp2]]]]]]
'''

        config = configobj.ConfigObj(StringIO(config_str % topic))

        topic_manager = TopicManager(None, config['MQTTSubscribe']['topics'], logger)

        SUT = MessageCallbackProvider(None, logger, topic_manager)

        payload_dict = {
            'dateTime': time.time(),
            'usUnits': random.randint(1, 10),
            'temps': {
                'temp1': round(random.uniform(10, 100), 2),
                'temp2': round(random.uniform(1, 100), 2),
            },
        }

        payload = json.dumps(payload_dict).encode("utf-8")

        expected_data = {
            'dateTime': payload_dict['dateTime'],
            'usUnits': payload_dict['usUnits'],
            'temps_temp1': payload_dict['temps']['temp1'],
            'temps_temp2': payload_dict['temps']['temp2'],
        }

        msg = Msg(topic, payload, 0, 0)
        SUT._on_message_json(None, None, msg)

        queue = topic_manager._get_queue(topic)
        data = queue['data'].popleft()['data']
        self.assertDictEqual(data, expected_data)

    def test_array_of_values(self):
        logger = Logger('FuncTest', level='ERROR', console=True)

        topic = random_string()
        config_str = '''
[MQTTSubscribe]
    [[topics]]
        [[[%s]]]
            [[[[message]]]]
                type = json

            [[[[temps]]]]
                [[[[[subfields]]]]]
                    [[[[[[temp1]]]]]]
                    [[[[[[temp2]]]]]]
'''

        config = configobj.ConfigObj(StringIO(config_str % topic))

        topic_manager = TopicManager(None, config['MQTTSubscribe']['topics'], logger)

        SUT = MessageCallbackProvider(None, logger, topic_manager)

        payload_dict = {
            'dateTime': time.time(),
            'usUnits': random.randint(1, 10),
            'temps': [round(random.uniform(10, 100), 2),  round(random.uniform(1, 100), 2),]
        }

        payload = json.dumps(payload_dict).encode("utf-8")

        expected_data = {
            'dateTime': payload_dict['dateTime'],
            'usUnits': payload_dict['usUnits'],
            'temp1': payload_dict['temps'][0],
            'temp2': payload_dict['temps'][1],
        }

        msg = Msg(topic, payload, 0, 0)
        SUT._on_message_json(None, None, msg)

        queue = topic_manager._get_queue(topic)
        data = queue['data'].popleft()['data']
        self.assertDictEqual(data, expected_data)


if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestConfigureFields('test_use_topic_as_fieldname'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
