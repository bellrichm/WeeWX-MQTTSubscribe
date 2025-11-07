#
#    Copyright (c) 2023-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
'''
This is a set of 'function' tests.
These test that the MQTTSubscribe configuration is correct for the payload.
'''

import unittest

import configobj
import json
import random
import string
import time

from io import StringIO

from user.MQTTSubscribe import Logger, MessageCallbackProvider, TopicManager

def random_string(length=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])

class Msg:
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain

class TestJSONMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logger = Logger({'mode': 'FuncTest'}, level='ERROR', console=True)

        cls.topic = random_string()
        cls.config_str = '''
[MQTTSubscribe]
    [[topics]]
        [[[%s]]]
            [[[[message]]]]
                type = json
'''

    def run_test(self, payload_dict, expected_data):
        config = configobj.ConfigObj(StringIO(self.config_str % self.topic))

        topic_manager = TopicManager(None, config['MQTTSubscribe']['topics'], self.logger)

        message_callback = MessageCallbackProvider(None, self.logger, topic_manager)

        payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)
        message_callback._on_message_json(msg)

        queue = topic_manager._get_queue(self.topic)
        data = queue['data'].popleft()['data']

        self.assertDictEqual(data, expected_data)

    def test_basic_message(self):
        payload_dict = {
            'dateTime': time.time(),
            'usUnits': random.randint(1, 10),
            'inTemp': round(random.uniform(10, 100), 2),
            'outTemp': round(random.uniform(1, 100), 2),
        }

        self.run_test(payload_dict, payload_dict)

    def test_nested_json_message(self):
        payload_dict = {
            'dateTime': time.time(),
            'usUnits': random.randint(1, 10),
            'temps': {
                'temp1': round(random.uniform(10, 100), 2),
                'temp2': round(random.uniform(1, 100), 2),
            },
        }

        expected_data = {
            'dateTime': payload_dict['dateTime'],
            'usUnits': payload_dict['usUnits'],
            'temps_temp1': payload_dict['temps']['temp1'],
            'temps_temp2': payload_dict['temps']['temp2'],
        }

        self.run_test(payload_dict, expected_data)

    def test_multi_nested_json_message(self):
        payload_dict = {
            'dateTime': time.time(),
            'usUnits': random.randint(1, 10),
            'level1': {
                'level2': {
                    'temps': {
                        'temp1': round(random.uniform(10, 100), 2),
                        'temp2': round(random.uniform(1, 100), 2),
                    },
                },
            },
        }

        expected_data = {
            'dateTime': payload_dict['dateTime'],
            'usUnits': payload_dict['usUnits'],
            'level1_level2_temps_temp1': payload_dict['level1']['level2']['temps']['temp1'],
            'level1_level2_temps_temp2': payload_dict['level1']['level2']['temps']['temp2'],
        }

        self.run_test(payload_dict, expected_data)

    def test_array_of_values(self):
        self.config_str += '''
            [[[[temps]]]]
                [[[[[subfields]]]]]
                    [[[[[[temp1]]]]]]
                    [[[[[[temp2]]]]]]
'''

        payload_dict = {
            'dateTime': time.time(),
            'usUnits': random.randint(1, 10),
            'temps': [round(random.uniform(10, 100), 2), round(random.uniform(1, 100), 2),]
        }

        expected_data = {
            'dateTime': payload_dict['dateTime'],
            'usUnits': payload_dict['usUnits'],
            'temp1': payload_dict['temps'][0],
            'temp2': payload_dict['temps'][1],
        }

        self.run_test(payload_dict, expected_data)

    def test_array_of_objects(self):
        self.config_str += '''
            [[[[temps]]]]
                [[[[[subfields]]]]]
                    [[[[[[temp]]]]]]
            [[[[temp_temp1]]]]
                name = temp1
            [[[[temp_temp2]]]]
                name = temp2
'''

        payload_dict = {
            'dateTime': time.time(),
            'usUnits': random.randint(1, 10),
            'temps': [
                {
                    'temp1': round(random.uniform(10, 100), 2),
                    'temp2': round(random.uniform(1, 100), 2),
                },
            ],
        }

        expected_data = {
            'dateTime': payload_dict['dateTime'],
            'usUnits': payload_dict['usUnits'],
            'temp1': payload_dict['temps'][0]['temp1'],
            'temp2': payload_dict['temps'][0]['temp2'],
        }

        self.run_test(payload_dict, expected_data)

    def test_array_of_arrays(self):
        self.config_str += '''
            [[[[sensors]]]]
                [[[[[subfields]]]]]
                    [[[[[[outTemps]]]]]]
                    [[[[[[inTemps]]]]]]
            [[[[outTemps]]]]
                [[[[[subfields]]]]]
                    [[[[[[outTemp1]]]]]]
                    [[[[[[outTemp2]]]]]]
            [[[[inTemps]]]]
                [[[[[subfields]]]]]
                    [[[[[[inTemp1]]]]]]
                    [[[[[[inTemp2]]]]]]
'''

        payload_dict = {
            'dateTime': time.time(),
            'usUnits': random.randint(1, 10),
            'sensors': [
                [round(random.uniform(10, 100), 2), round(random.uniform(1, 100), 2),],
                [round(random.uniform(10, 100), 2), round(random.uniform(1, 100), 2),],
            ]
        }

        expected_data = {
            'dateTime': payload_dict['dateTime'],
            'usUnits': payload_dict['usUnits'],
            'outTemps_outTemp1': payload_dict['sensors'][0][0],
            'outTemps_outTemp2': payload_dict['sensors'][0][1],
            'inTemps_inTemp1': payload_dict['sensors'][1][0],
            'inTemps_inTemp2': payload_dict['sensors'][1][1],
        }

        self.run_test(payload_dict, expected_data)

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestConfigureFields('test_use_topic_as_fieldname'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
