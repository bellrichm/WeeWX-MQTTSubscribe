#
#    Copyright (c) 2024 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import unittest
import mock

import configobj
import random
import sys

import test_weewx_stubs
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import MQTTSubscriberV1, Logger

mock_client = None

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

        rc = random.randint(1, 10)

        with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
            with mock.patch('user.MQTTSubscribe.TopicManager'):
                # pylint: disable=no-member, protected-access
                SUT = MQTTSubscriberV1(config, mock_logger)

                SUT._on_disconnect(None, None, rc)

                SUT.logger.info.assert_called_with(f"Disconnected with result code {int(rc)}")

    @staticmethod
    def test_on_subscribe():
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        mid = random.randint(1, 10)
        granted_qos = [random.randint(1, 10)]

        with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
            with mock.patch('user.MQTTSubscribe.TopicManager'):
                # pylint: disable=no-member, protected-access
                SUT = MQTTSubscriberV1(config, mock_logger)

                SUT._on_subscribe(None, None, mid, granted_qos)

                SUT.logger.info.assert_called_with(f"Subscribed to mid: {mid} is size {len(granted_qos)} has a QOS of {granted_qos[0]}")

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestInitialization('test_connect_exception'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
