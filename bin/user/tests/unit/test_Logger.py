# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=import-outside-toplevel

from __future__ import with_statement

import unittest
import mock

import random
import string
import sys

from test_weewx_stubs import weeutil

class TestV3Logging(unittest.TestCase):
    def test_test(self):
        print("start")
        with mock.patch.dict(sys.modules, {'weeutil.logger':None}):
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                from user.MQTTSubscribe import Logger

                mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
                print("v3")
                SUT = Logger('foo')
                print(SUT)
                SUT.info("foo/bar v3")
        print("done")

class TestV4Logging(unittest.TestCase):
    def test_base(self):
        print("start")
        #import logging
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                from user.MQTTSubscribe import Logger

                mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
                print("v4")
                SUT = Logger('bar')
                print(SUT)
                SUT.info("foo/bar v4")
        print("done")

    def test_init_filename_set(self):
        print("start")
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                from user.MQTTSubscribe import Logger

                mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access

                mock_file_handler = mock.Mock()
                mock_logging.FileHandler.return_value = mock_file_handler
                mode = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) # pylint: disable=unused-variable
                filename = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) # pylint: disable=unused-variable

                SUT = Logger(mode, filename=filename)

                mock_logging.Formatter.assert_called_once()
                mock_logging.FileHandler.assert_called_once()
                mock_file_handler.setLevel.assert_called_once()
                mock_file_handler.setFormatter.assert_called_once()
                SUT._logmsg.addHandler.assert_called_once() # pylint: disable=protected-access

    def test_init_console_set(self):
        print("start")
        with mock.patch.dict(sys.modules, {'weeutil.logger':weeutil.logger}):
            with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
                from user.MQTTSubscribe import Logger

                mock_logging._checkLevel.return_value = 0 # pylint: disable=protected-access
                mode = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) # pylint: disable=unused-variable

                SUT = Logger(mode, console=True)

                SUT._logmsg.addHandler.assert_called_once() # pylint: disable=protected-access

if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestV4Logging('test_test'))
    #test_suite.addTest(TestV3Logging('test_test'))
    unittest.TextTestRunner().run(test_suite)

    # unittest.main(exit=False)
