# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest
import mock

import argparse
import sys

import user.MQTTSubscribe

# Stole from six module. Added to eliminate dependency on six when running under WeeWX 3.x
PY2 = sys.version_info[0] == 2
if PY2:
    builtins_module_name = '__builtin__'
else:
    builtins_module_name = 'builtins'

class DriverLoaderStub():
    # pylint: disable=too-few-public-methods
    def __init__(self, mock_driver):
        self.mock_driver = mock_driver

    def loader(self, config_dict, engine): #  Need to match signature pylint: disable=unused-argument
        return self.mock_driver

class test_test(unittest.TestCase):
    def test_test(self):
        print("start")

        options = argparse.Namespace()
        #options.type = 'service'
        options.type = 'driver'

        #options.binding = 'loop'
        options.binding = 'archive'

        options.record_count = 3
        options.interval = 99
        options.delay = 99
        options.callback = 'foo'
        options.topics = 'foo'
        options.host = 'foo'
        options.console = 'foo'
        options.config_file = 'foo'
        options.units = 'US'
        options.verbose = 'foo'

        mock_driver = mock.Mock()
        data = {}
        data['dateTime'] = 0
        mock_driver.genArchiveRecords.return_value = [data]
        mock_driver.genLoopPackets.return_value = [data]
        driver_loader_stub = DriverLoaderStub(mock_driver)

        with mock.patch('user.MQTTSubscribe.argparse') as mock_argparse:
            with mock.patch('user.MQTTSubscribe.time'):
                #with mock.patch('user.MQTTSubscribe.MQTTSubscribeService') as mock_service:
                with mock.patch('user.MQTTSubscribe.weeutil'):
                    with mock.patch('user.MQTTSubscribe.to_sorted_string'):
                        with mock.patch('%s.%s' % (builtins_module_name, '__import__')):
                            with mock.patch.dict(sys.modules, {'user.MQTTSubscribe':driver_loader_stub}):

                                mock_parser = mock.Mock()
                                mock_parser.parse_args.return_value = options
                                mock_argparse.ArgumentParser.return_value = mock_parser

                                SUT = user.MQTTSubscribe.Simulator()

                                mock_engine = mock.Mock()
                                SUT.engine = mock_engine
                                SUT.config_dict = {}
                                SUT.config_dict['MQTTSubscribeDriver'] = {}

                                SUT.run()

        print("end")

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestConfigureFields('test_use_topic_as_fieldname'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
