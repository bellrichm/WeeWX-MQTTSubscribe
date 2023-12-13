#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=bad-option-value, import-outside-toplevel
# pylint: enable=bad-option-value

import importlib
import unittest
import mock

import sys

from test_weewx_stubs import weewx, random_string

class TestV4Logging(unittest.TestCase):
    def test_init_set_trace_log_level(self):
        log_level = 5

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            from user.MQTTSubscribe import Logger

            mock_logging._checkLevel.return_value = log_level # pylint: disable=protected-access
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

            SUT = Logger(random_string(), level=random_string())

            mock_logging.addLevelName.assert_called_once_with(log_level, 'TRACE')
            SUT._logmsg.setLevel.assert_called_once_with(log_level) # pylint: disable=protected-access

            mock_grandparent_handler.setLevel.assert_called_once_with(log_level)
            mock_parent_handler.setLevel.assert_called_once_with(log_level)

            self.assertEqual(SUT._logmsg.addHandler.call_count, 2) # pylint: disable=protected-access

    @staticmethod
    def test_init_filename_set():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            from user.MQTTSubscribe import Logger

            mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access

            mock_file_handler = mock.Mock()
            mock_logging.FileHandler.return_value = mock_file_handler
            mode = random_string()
            filename = random_string()

            SUT = Logger(mode, filename=filename)

            mock_logging.Formatter.assert_called_once()
            mock_logging.FileHandler.assert_called_once()
            mock_file_handler.setLevel.assert_called_once()
            mock_file_handler.setFormatter.assert_called_once()
            SUT._logmsg.addHandler.assert_called_once() # pylint: disable=protected-access

    @staticmethod
    def test_init_console_set():
        import user.MQTTSubscribe
        importlib.reload(user.MQTTSubscribe)
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            from user.MQTTSubscribe import Logger

            mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
            mode = random_string()

            SUT = Logger(mode, console=True)

            SUT._logmsg.addHandler.assert_called_once() # pylint: disable=protected-access

        importlib.reload(user.MQTTSubscribe)

    @staticmethod
    def test_error_logged():
        import user.MQTTSubscribe
        importlib.reload(user.MQTTSubscribe)
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            from user.MQTTSubscribe import Logger

            mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
            mode = random_string()
            message = random_string()

            SUT = Logger(mode)

            SUT.error(message)

            SUT._logmsg.error.assert_called_once_with(SUT.MSG_FORMAT, mode, message) # pylint: disable=protected-access

        importlib.reload(user.MQTTSubscribe)

    @staticmethod
    def test_info_logged():
        import user.MQTTSubscribe
        importlib.reload(user.MQTTSubscribe)
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            from user.MQTTSubscribe import Logger

            mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
            mode = random_string()
            message = random_string()

            SUT = Logger(mode)

            SUT.info(message)

            SUT._logmsg.info.assert_called_once_with(SUT.MSG_FORMAT, mode, message) # pylint: disable=protected-access

        importlib.reload(user.MQTTSubscribe)

    @staticmethod
    def test_debug_logged():
        import user.MQTTSubscribe
        importlib.reload(user.MQTTSubscribe)
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            from user.MQTTSubscribe import Logger

            mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
            mode = random_string()
            message = random_string()

            SUT = Logger(mode)

            SUT.debug(message)

            SUT._logmsg.debug.assert_called_once_with(SUT.MSG_FORMAT, mode, message) # pylint: disable=protected-access

        importlib.reload(user.MQTTSubscribe)

    @staticmethod
    def test_trace_logged_with_debug_set():
        import user.MQTTSubscribe
        importlib.reload(user.MQTTSubscribe)
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            from user.MQTTSubscribe import Logger

            weewx.debug = 2
            mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
            mode = random_string()
            message = random_string()

            SUT = Logger(mode)

            SUT.trace(message)

            SUT._logmsg.debug.assert_called_once_with(SUT.MSG_FORMAT, mode, message) # pylint: disable=protected-access

        importlib.reload(user.MQTTSubscribe)

    @staticmethod
    def test_trace_logged_with_debug_not_set():
        import user.MQTTSubscribe
        importlib.reload(user.MQTTSubscribe)
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            from user.MQTTSubscribe import Logger

            weewx.debug = 0
            mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
            mode = random_string()
            message = random_string()

            SUT = Logger(mode)

            SUT.trace(message)

            SUT._logmsg.log.assert_called_once_with(5, SUT.MSG_FORMAT, mode, message) # pylint: disable=protected-access

        importlib.reload(user.MQTTSubscribe)

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestV4Logging('test_test'))
    # test_suite.addTest(TestV3Logging('test_base'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
