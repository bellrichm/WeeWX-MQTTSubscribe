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

import random
import sys

from test_weewx_stubs import weeutil, weewx, random_string

class TestV3Logging(unittest.TestCase):
    def test_init_filename(self):
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.open') as mock_open:
                    from user.MQTTSubscribe import Logger
                    mode = random_string()
                    filename = random_string()

                    mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
                    Logger(mode, filename=filename)

                    self.assertEqual(mock_open.call_count, 1)
                    mock_open.assert_called_once_with(filename, 'w')

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_error_not_logged():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                    from user.MQTTSubscribe import Logger

                    mode = random_string()
                    message = random_string()
                    mock_logging._checkLevel.return_value = random.randint(41, 99) # pylint: disable=protected-access

                    SUT = Logger(mode)

                    SUT.error(message)

                    mock_syslog.syslog.assert_not_called()

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_error_logged():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                    from user.MQTTSubscribe import Logger
                    log_level = random.randint(1, 99)
                    mode = random_string()
                    message = random_string()
                    mock_logging._checkLevel.return_value = random.randint(1, 40) # pylint: disable=protected-access
                    type(mock_syslog).LOG_ERR = mock.PropertyMock(return_value=log_level)

                    SUT = Logger(mode)

                    SUT.error(message)

                    mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_error_logged_to_file():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.open') as mock_open:
                    with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                        from user.MQTTSubscribe import Logger
                        mock_file = mock.Mock()
                        mock_open.return_value = mock_file
                        log_level = random.randint(1, 99)
                        mode = random_string()
                        message = random_string()
                        filename = random_string()
                        mock_logging._checkLevel.return_value = random.randint(1, 40) # pylint: disable=protected-access
                        type(mock_syslog).LOG_ERR = mock.PropertyMock(return_value=log_level)

                        SUT = Logger(mode, filename=filename)

                        SUT.error(message)

                        mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))
                        mock_file.write.assert_called_once_with('user.MQTTSubscribe: %s\n' % message)

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_error_logged_to_console():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.print') as mock_print:
                    with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                        from user.MQTTSubscribe import Logger
                        log_level = random.randint(1, 99)
                        mode = random_string()
                        message = random_string()
                        mock_logging._checkLevel.return_value = random.randint(1, 40) # pylint: disable=protected-access
                        type(mock_syslog).LOG_ERR = mock.PropertyMock(return_value=log_level)

                        SUT = Logger(mode, console=True)

                        SUT.error(message)

                        mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))
                        mock_print.assert_called_once_with('user.MQTTSubscribe: %s' % message)

                importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_info_not_logged():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                    from user.MQTTSubscribe import Logger

                    mode = random_string()
                    message = random_string()
                    mock_logging._checkLevel.return_value = random.randint(21, 99) # pylint: disable=protected-access

                    SUT = Logger(mode)

                    SUT.info(message)

                    mock_syslog.syslog.assert_not_called()

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_info_logged():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                    from user.MQTTSubscribe import Logger
                    log_level = random.randint(1, 99)
                    mode = random_string()
                    message = random_string()
                    mock_logging._checkLevel.return_value = random.randint(1, 20) # pylint: disable=protected-access
                    type(mock_syslog).LOG_INFO = mock.PropertyMock(return_value=log_level)

                    SUT = Logger(mode)

                    SUT.info(message)

                    mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_info_logged_to_file():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.open') as mock_open:
                    with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                        from user.MQTTSubscribe import Logger
                        mock_file = mock.Mock()
                        mock_open.return_value = mock_file
                        log_level = random.randint(1, 99)
                        mode = random_string()
                        message = random_string()
                        filename = random_string()
                        mock_logging._checkLevel.return_value = random.randint(1, 20) # pylint: disable=protected-access
                        type(mock_syslog).LOG_INFO = mock.PropertyMock(return_value=log_level)

                        SUT = Logger(mode, filename=filename)

                        SUT.info(message)

                        mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))
                        mock_file.write.assert_called_once_with('user.MQTTSubscribe: %s\n' % message)

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_info_logged_to_console():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.print') as mock_print:
                    with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                        from user.MQTTSubscribe import Logger
                        log_level = random.randint(1, 99)
                        mode = random_string()
                        message = random_string()
                        mock_logging._checkLevel.return_value = random.randint(1, 20) # pylint: disable=protected-access
                        type(mock_syslog).LOG_INFO = mock.PropertyMock(return_value=log_level)

                        SUT = Logger(mode, console=True)

                        SUT.info(message)

                        mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))
                        mock_print.assert_called_once_with('user.MQTTSubscribe: %s' % message)

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_debug_not_logged():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                    from user.MQTTSubscribe import Logger

                    mode = random_string()
                    message = random_string()
                    mock_logging._checkLevel.return_value = random.randint(41, 99) # pylint: disable=protected-access

                    SUT = Logger(mode)

                    SUT.debug(message)

                    mock_syslog.syslog.assert_not_called()

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_debug_logged():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                    from user.MQTTSubscribe import Logger
                    log_level = random.randint(1, 99)
                    mode = random_string()
                    message = random_string()
                    mock_logging._checkLevel.return_value = random.randint(1, 10) # pylint: disable=protected-access
                    type(mock_syslog).LOG_DEBUG = mock.PropertyMock(return_value=log_level)

                    SUT = Logger(mode)

                    SUT.debug(message)

                    mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_debug_logged_to_file():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.open') as mock_open:
                    with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                        from user.MQTTSubscribe import Logger
                        mock_file = mock.Mock()
                        mock_open.return_value = mock_file
                        log_level = random.randint(1, 99)
                        mode = random_string()
                        message = random_string()
                        filename = random_string()
                        mock_logging._checkLevel.return_value = random.randint(1, 10) # pylint: disable=protected-access
                        type(mock_syslog).LOG_DEBUG = mock.PropertyMock(return_value=log_level)

                        SUT = Logger(mode, filename=filename)

                        SUT.debug(message)

                        mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))
                        mock_file.write.assert_called_once_with('user.MQTTSubscribe: %s\n' % message)

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_debug_logged_to_console():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.print') as mock_print:
                    with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                        from user.MQTTSubscribe import Logger
                        log_level = random.randint(1, 99)
                        mode = random_string()
                        message = random_string()
                        mock_logging._checkLevel.return_value = random.randint(1, 10) # pylint: disable=protected-access
                        type(mock_syslog).LOG_DEBUG = mock.PropertyMock(return_value=log_level)

                        SUT = Logger(mode, console=True)

                        SUT.debug(message)

                        mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))
                        mock_print.assert_called_once_with('user.MQTTSubscribe: %s' % message)

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_trace_not_logged():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                    from user.MQTTSubscribe import Logger
                    weewx.debug = 0
                    mode = random_string()
                    message = random_string()
                    mock_logging._checkLevel.return_value = random.randint(41, 99) # pylint: disable=protected-access

                    SUT = Logger(mode)

                    SUT.trace(message)

                    mock_syslog.syslog.assert_not_called()

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_trace_logged():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                    from user.MQTTSubscribe import Logger
                    log_level = random.randint(1, 99)
                    mode = random_string()
                    message = random_string()
                    mock_logging._checkLevel.return_value = random.randint(41, 99) # pylint: disable=protected-access
                    type(mock_syslog).LOG_DEBUG = mock.PropertyMock(return_value=log_level)

                    SUT = Logger(mode)

                    SUT.trace(message)

                    mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_trace_logged_to_file():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.open') as mock_open:
                    with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                        from user.MQTTSubscribe import Logger
                        mock_file = mock.Mock()
                        mock_open.return_value = mock_file
                        log_level = random.randint(1, 99)
                        mode = random_string()
                        message = random_string()
                        filename = random_string()
                        mock_logging._checkLevel.return_value = random.randint(1, 10) # pylint: disable=protected-access
                        type(mock_syslog).LOG_DEBUG = mock.PropertyMock(return_value=log_level)

                        SUT = Logger(mode, filename=filename)

                        SUT.trace(message)

                        mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))
                        mock_file.write.assert_called_once_with('user.MQTTSubscribe: %s\n' % message)

            importlib.reload(user.MQTTSubscribe) 

    @staticmethod
    def test_trace_logged_to_console():
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            import user.MQTTSubscribe
            importlib.reload(user.MQTTSubscribe) 
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                with mock.patch('user.MQTTSubscribe.print') as mock_print:
                    with mock.patch('user.MQTTSubscribe.syslog') as mock_syslog:
                        from user.MQTTSubscribe import Logger
                        log_level = random.randint(1, 99)
                        mode = random_string()
                        message = random_string()
                        mock_logging._checkLevel.return_value = random.randint(1, 10) # pylint: disable=protected-access
                        type(mock_syslog).LOG_DEBUG = mock.PropertyMock(return_value=log_level)

                        SUT = Logger(mode, console=True)

                        SUT.trace(message)

                        mock_syslog.syslog.assert_called_once_with(log_level, '(%s) user.MQTTSubscribe: %s' % (mode, message))
                        mock_print.assert_called_once_with('user.MQTTSubscribe: %s' % message)

            importlib.reload(user.MQTTSubscribe) 

class TestV4Logging(unittest.TestCase):
    def test_init_set_trace_log_level(self):
        log_level = 5

        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                from user.MQTTSubscribe import Logger

                mock_logging._checkLevel.return_value = log_level # pylint: disable=protected-access
                mock_logging.getLevelName.return_value = 'Level %i' % log_level

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
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
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
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
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
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
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
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
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
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
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
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
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
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
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
