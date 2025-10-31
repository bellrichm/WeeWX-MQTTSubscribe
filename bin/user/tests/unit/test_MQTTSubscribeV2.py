#
#    Copyright (c) 2024-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import unittest
import mock

import configobj
import random
import sys

import paho

import test_weewx_stubs
from test_weewx_stubs import random_string
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import MQTTSubscriberV2, Logger

@unittest.skipIf(not hasattr(paho.mqtt.client, 'CallbackAPIVersion'), "paho-mqtt is v1, skipping tests.")
class TestCallbacks(unittest.TestCase):
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
    def test_on_disconnect():
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        reason_code = paho.mqtt.reasoncodes.ReasonCode(paho.mqtt.packettypes.PacketTypes.CONNACK,
                                                       identifier=random.randint(131, 138))

        with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
            with mock.patch('user.MQTTSubscribe.TopicManager'):
                SUT = MQTTSubscriberV2(config, mock_logger)

                SUT._on_disconnect(None, None, None, reason_code, None)

                SUT.logger.info.assert_called_with(f"Disconnected with result code {int(reason_code.value)}")

    @staticmethod
    def test_on_subscribe():
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        mid = random.randint(1, 10)
        reason_code = paho.mqtt.reasoncodes.ReasonCode(paho.mqtt.packettypes.PacketTypes.CONNACK,
                                                       identifier=random.randint(131, 138))
        reason_codes = [reason_code]

        with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
            with mock.patch('user.MQTTSubscribe.TopicManager'):
                SUT = MQTTSubscriberV2(config, mock_logger)

                SUT._on_subscribe(None, None, mid, reason_codes, None)

                SUT.logger.info.assert_called_with(f"Subscribed to mid: {mid} is size {len(reason_codes)} has a QOS of {reason_codes[0].value}")

    @staticmethod
    def test_on_log():
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        level = 1
        msg = random_string()

        with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
            with mock.patch('user.MQTTSubscribe.TopicManager'):
                with mock.patch('user.MQTTSubscribe.mqtt.Client'):
                    SUT = MQTTSubscriberV2(config, mock_logger)

                    SUT._on_log(None, None, level, msg)

                    SUT.logger.info.assert_called_with(f"MQTTSubscribe MQTT: {msg}")

    def test_mqtt_log_set(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {
            'message_callback': {},
            'topics': {
                random_string(): {}
            },
            'log': True
        }

        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
            with mock.patch('user.MQTTSubscribe.TopicManager'):
                with mock.patch('user.MQTTSubscribe.mqtt.Client'):
                    SUT = MQTTSubscriberV2(config, mock_logger)

                    self.assertEqual(SUT.client.on_log, SUT._on_log)

    def test_mqtt_log_not_set(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {

            'message_callback': {},
            'topics': {
                random_string(): {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
            with mock.patch('user.MQTTSubscribe.TopicManager'):
                with mock.patch('user.MQTTSubscribe.mqtt.Client'):
                    SUT = MQTTSubscriberV2(config, mock_logger)

                    self.assertNotEqual(SUT.client.on_log, SUT._on_log)

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestInitialization('test_connect_exception'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
