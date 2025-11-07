#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import unittest
import mock

import sys

import test_weewx_stubs
from test_weewx_stubs import random_string
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import Logger

class TestV4Logging(unittest.TestCase):
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

    def test_init_set_trace_log_level(self):
        log_level = 5

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:

            mock_logging._checkLevel.return_value = log_level
            mock_logging.getLevelName.return_value = f'Level {int(log_level)}'

            mock_grandparent_handler = mock.Mock()
            mock_grandparent_logger = mock.Mock()
            mock_grandparent_logger.handlers = [mock_grandparent_handler]
            mock_grandparent_logger.parent = None

            mock_parent_handler = mock.Mock()
            mock_parent_logger = mock.Mock()
            mock_parent_logger.handlers = [mock_parent_handler]
            mock_parent_logger.parent = mock_grandparent_logger

            mock_logger = mock.Mock()
            mock_logger.parent = mock_parent_logger
            mock_logging.getLogger.return_value = mock_logger

            SUT = Logger({'mode': random_string()}, level=random_string())

            mock_logging.addLevelName.assert_called_once_with(log_level, 'TRACE')
            SUT._logmsg.setLevel.assert_called_once_with(log_level)

            mock_grandparent_handler.setLevel.assert_called_once_with(log_level)
            mock_parent_handler.setLevel.assert_called_once_with(log_level)

            self.assertEqual(SUT._logmsg.addHandler.call_count, 2)

    @staticmethod
    def test_init_filename_set():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:

            mock_logging._checkLevel.return_value = 0

            mock_file_handler = mock.Mock()
            mock_logging.FileHandler.return_value = mock_file_handler
            mode = random_string()
            filename = random_string()

            SUT = Logger({'mode': mode}, filename=filename)

            mock_logging.Formatter.assert_called_once()
            mock_logging.FileHandler.assert_called_once()
            mock_file_handler.setLevel.assert_called_once()
            mock_file_handler.setFormatter.assert_called_once()
            SUT._logmsg.addHandler.assert_called_once()

    @staticmethod
    def test_init_console_set():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:

            mock_logging._checkLevel.return_value = 0
            mode = random_string()

            SUT = Logger({'mode': mode}, console=True)

            SUT._logmsg.addHandler.assert_called_once()

    @staticmethod
    def test_error_logged():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:

            mock_logging._checkLevel.return_value = 0
            mode = random_string()
            message = random_string()

            SUT = Logger({'mode': mode})

            SUT.error(message)

            SUT._logmsg.error.assert_called_once_with(SUT.MSG_FORMAT, mode, message)

    @staticmethod
    def test_info_logged():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:

            mock_logging._checkLevel.return_value = 0
            mode = random_string()
            message = random_string()

            SUT = Logger({'mode': mode})

            SUT.info(message)

            SUT._logmsg.info.assert_called_once_with(SUT.MSG_FORMAT, mode, message)

    @staticmethod
    def test_debug_logged():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:

            mock_logging._checkLevel.return_value = 0
            mode = random_string()
            message = random_string()

            SUT = Logger({'mode': mode})

            SUT.debug(message)

            SUT._logmsg.debug.assert_called_once_with(SUT.MSG_FORMAT, mode, message)

    @staticmethod
    def test_trace_logged_with_debug_set():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:

            sys.modules['weewx'].debug = 2
            mock_logging._checkLevel.return_value = 0
            mode = random_string()
            message = random_string()

            SUT = Logger({'mode': mode})

            SUT.trace(message)

            SUT._logmsg.debug.assert_called_once_with(SUT.MSG_FORMAT, mode, message)

    @staticmethod
    def test_trace_logged_with_debug_not_set():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:

            mock_logging._checkLevel.return_value = 0
            mode = random_string()
            message = random_string()

            SUT = Logger({'mode': mode})
            SUT.weewx_debug = 0

            SUT.trace(message)

            SUT._logmsg.log.assert_called_once_with(5, SUT.MSG_FORMAT, mode, message)

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestV4Logging('test_test'))
    # test_suite.addTest(TestV3Logging('test_base'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
