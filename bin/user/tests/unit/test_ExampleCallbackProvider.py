#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import unittest
import mock

import random
import sys
import xml.etree

import test_weewx_stubs
from test_weewx_stubs import random_ascii_letters
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import Logger
from user.ExampleMessageCallbackProvider import MessageCallbackProvider

class Msg:
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain

class Test1(unittest.TestCase):
    def setUp(self):
        # reset stubs for every test
        test_weewx_stubs.setup_stubs()

    def tearDown(self):
        # cleanup stubs
        del sys.modules['weecfg']
        del sys.modules['weeutil']
        del sys.modules['weeutil.config']
        del sys.modules['weeutil.weeutil']
        del sys.modules['weeutil.logger']
        del sys.modules['weewx']
        del sys.modules['weewx.drivers']
        del sys.modules['weewx.engine']

    @staticmethod
    def create_observation_dict(size):
        observation_dict = {}

        i = 0
        while i < size:
            observation_dict[random_ascii_letters()] = round(random.uniform(101, 200), 2)
            i += 1

        return observation_dict

    @staticmethod
    def create_observation_xml(parent, observation_dict):
        xml_element = xml.etree.ElementTree.Element(parent)
        for key, value in observation_dict.items():
            child = xml.etree.ElementTree.Element(key)
            child.text = str(value)
            xml_element.append(child)
        return xml_element

    def test_get_observations(self):
        observation_dict = self.create_observation_dict(5)
        root = self.create_observation_xml('observations', observation_dict)

        SUT = MessageCallbackProvider({}, None, None)

        results = SUT.get_observations(root, "", {}, 1)

        self.assertDictEqual(observation_dict, results)

    def test_on_message(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock()
        mock_manager.get_fields.return_value = {}

        observation_dict = self.create_observation_dict(5)
        root = self.create_observation_xml('observations', observation_dict)
        xml_string = xml.etree.ElementTree.tostring(root)
        msg = Msg("topic", xml_string, 0, 0)

        SUT = MessageCallbackProvider({}, mock_logger, mock_manager)

        SUT._on_message(msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, observation_dict)

if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(Test1('test_get_observations'))
    test_suite.addTest(Test1('test_on_message'))
    unittest.TextTestRunner().run(test_suite)

    # unittest.main(exit=False)
