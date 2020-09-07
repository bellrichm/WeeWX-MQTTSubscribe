# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest
import mock

import argparse
import sys
import time

#import test_weewx_stubs
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

class test_simulate_driver(unittest.TestCase):
    @staticmethod
    def test_simulate_archive():
        data = {}
        data['dateTime'] = 0
        interval = 60
        delay = 5

        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / interval) + 1) * interval
        end_delay_ts = end_period_ts + delay
        sleep_amount = end_delay_ts - current_time

        options = argparse.Namespace()
        options.type = 'driver'

        #options.binding = 'loop'
        options.binding = 'archive'

        options.record_count = len(data)
        options.interval = interval
        options.delay = delay
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
            with mock.patch('user.MQTTSubscribe.print'):
                with mock.patch('user.MQTTSubscribe.time') as mock_time:
                    with mock.patch('user.MQTTSubscribe.weeutil'):
                        with mock.patch('user.MQTTSubscribe.to_sorted_string'):
                            with mock.patch('%s.%s' % (builtins_module_name, '__import__')):
                                with mock.patch.dict(sys.modules, {'user.MQTTSubscribe':driver_loader_stub}):
                                    mock_parser = mock.Mock()
                                    mock_parser.parse_args.return_value = options
                                    mock_argparse.ArgumentParser.return_value = mock_parser

                                    mock_time.time.return_value = current_time

                                    SUT = user.MQTTSubscribe.Simulator()

                                    SUT.run()

                                    mock_time.sleep.assert_called_once_with(sleep_amount)
                                    mock_driver.genArchiveRecords.assert_called_once_with(end_period_ts)

    @staticmethod
    def test_simulate_loop():
        data = {}
        data['dateTime'] = 0

        options = argparse.Namespace()
        options.type = 'driver'
        options.binding = 'loop'
        options.record_count = len(data)

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
            with mock.patch('user.MQTTSubscribe.print'):
                with mock.patch('user.MQTTSubscribe.weeutil'):
                    with mock.patch('user.MQTTSubscribe.to_sorted_string'):
                        with mock.patch('%s.%s' % (builtins_module_name, '__import__')):
                            with mock.patch.dict(sys.modules, {'user.MQTTSubscribe':driver_loader_stub}):
                                mock_parser = mock.Mock()
                                mock_parser.parse_args.return_value = options
                                mock_argparse.ArgumentParser.return_value = mock_parser

                                SUT = user.MQTTSubscribe.Simulator()

                                SUT.run()

                                mock_driver.genLoopPackets.assert_called_once()

class test_simulate_service(unittest.TestCase):
    @staticmethod
    def test_simulate_archive():
        data = {}
        data['dateTime'] = 0
        interval = 300
        delay = 5

        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / interval) + 1) * interval
        end_delay_ts = end_period_ts + delay
        sleep_amount = end_delay_ts - current_time

        options = argparse.Namespace()
        options.type = 'service'

        #options.binding = 'loop'
        options.binding = 'archive'

        options.record_count = len(data)
        options.interval = interval
        options.delay = delay
        options.callback = 'foo'
        options.topics = 'foo'
        options.host = 'foo'
        options.console = 'foo'
        options.config_file = 'foo'
        options.units = 'US'
        options.verbose = 'foo'

        with mock.patch('user.MQTTSubscribe.argparse') as mock_argparse:
            with mock.patch('user.MQTTSubscribe.print'):
                with mock.patch('user.MQTTSubscribe.time') as mock_time:
                    with mock.patch('user.MQTTSubscribe.MQTTSubscribeService'):
                        with mock.patch('user.MQTTSubscribe.weewx'):
                            with mock.patch('user.MQTTSubscribe.weeutil'):
                                with mock.patch('user.MQTTSubscribe.to_sorted_string'):
                                    mock_parser = mock.Mock()
                                    mock_parser.parse_args.return_value = options
                                    mock_argparse.ArgumentParser.return_value = mock_parser

                                    mock_time.time.return_value = current_time

                                    SUT = user.MQTTSubscribe.Simulator()

                                    mock_engine = mock.Mock()
                                    SUT.engine = mock_engine
                                    SUT.config_dict = {}
                                    SUT.config_dict['MQTTSubscribeDriver'] = {}

                                    SUT.run()

                                    mock_time.sleep.assert_called_once_with(sleep_amount)
                                    mock_engine.dispatchEvent.assert_called_once()

    @staticmethod
    def test_simulate_loop():
        data = {}
        data['dateTime'] = 0
        interval = 300
        delay = 5

        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / interval) + 1) * interval
        end_delay_ts = end_period_ts + delay
        sleep_amount = end_delay_ts - current_time

        options = argparse.Namespace()
        options.type = 'service'

        options.binding = 'loop'

        options.record_count = len(data)
        options.interval = interval
        options.delay = delay
        options.callback = 'foo'
        options.topics = 'foo'
        options.host = 'foo'
        options.console = 'foo'
        options.config_file = 'foo'
        options.units = 'US'
        options.verbose = 'foo'

        with mock.patch('user.MQTTSubscribe.argparse') as mock_argparse:
            with mock.patch('user.MQTTSubscribe.print'):
                with mock.patch('user.MQTTSubscribe.time') as mock_time:
                    with mock.patch('user.MQTTSubscribe.MQTTSubscribeService'):
                        with mock.patch('user.MQTTSubscribe.weewx'):
                            with mock.patch('user.MQTTSubscribe.weeutil'):
                                with mock.patch('user.MQTTSubscribe.to_sorted_string'):
                                    mock_parser = mock.Mock()
                                    mock_parser.parse_args.return_value = options
                                    mock_argparse.ArgumentParser.return_value = mock_parser

                                    mock_time.time.return_value = current_time

                                    SUT = user.MQTTSubscribe.Simulator()

                                    mock_engine = mock.Mock()
                                    SUT.engine = mock_engine
                                    SUT.config_dict = {}
                                    SUT.config_dict['MQTTSubscribeDriver'] = {}

                                    SUT.run()
                                    mock_time.sleep.assert_called_once_with(sleep_amount)
                                    mock_engine.dispatchEvent.assert_called_once()

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestConfigureFields('test_use_topic_as_fieldname'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
