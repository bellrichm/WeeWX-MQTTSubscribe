#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import unittest
import mock

import argparse
import random
import sys
import time

from test_weewx_stubs import random_string

import user.MQTTSubscribe

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
        archive_interval = 60
        archive_delay = 5

        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / archive_interval) + 1) * archive_interval
        end_delay_ts = end_period_ts + archive_delay
        sleep_amount = end_delay_ts - current_time

        options = argparse.Namespace()
        options.type = 'driver'
        options.binding = 'archive'
        options.record_count = len(data)
        options.archive_interval = archive_interval
        options.archive_delay = archive_delay

        options.console = random_string()
        options.log_file = None
        options.conf = random_string()
        options.verbose = random_string()

        options.frequency = None
        options.units = None

        mock_driver = mock.Mock()
        data = {}
        data['dateTime'] = 0
        mock_driver.genArchiveRecords.return_value = [data]
        mock_driver.genLoopPackets.return_value = [data]
        driver_loader_stub = DriverLoaderStub(mock_driver)

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.weeutil'):
                    with mock.patch('user.MQTTSubscribe.to_sorted_string'):
                        with mock.patch(f'{builtins_module_name}.__import__'):
                            with mock.patch.dict(sys.modules, {'user.MQTTSubscribe':driver_loader_stub}):
                                mock_time.time.return_value = current_time

                                SUT = user.MQTTSubscribe.Simulator(None, options)

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

        options.archive_interval = random.randint(1, 99)
        options.archive_delay = random.randint(1, 99)
        options.log_file = None
        options.console = random_string()
        options.conf = random_string()
        options.verbose = random_string()

        options.frequency = None
        options.units = None
        options.archive_interval = None
        options.archive_delay = None

        mock_driver = mock.Mock()
        data = {}
        data['dateTime'] = 0
        mock_driver.genArchiveRecords.return_value = [data]
        mock_driver.genLoopPackets.return_value = [data]
        driver_loader_stub = DriverLoaderStub(mock_driver)

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.weeutil'):
                with mock.patch('user.MQTTSubscribe.to_sorted_string'):
                    with mock.patch(f'{builtins_module_name}.__import__'):
                        with mock.patch.dict(sys.modules, {'user.MQTTSubscribe':driver_loader_stub}):

                            SUT = user.MQTTSubscribe.Simulator(None, options)

                            SUT.run()

                            mock_driver.genLoopPackets.assert_called_once()

class test_simulate_service(unittest.TestCase):
    @staticmethod
    def test_simulate_archive():
        data = {}
        data['dateTime'] = 0
        frequency = 300

        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / frequency) + 1) * frequency
        sleep_amount = end_period_ts - current_time

        options = argparse.Namespace()
        options.type = 'service'
        options.binding = 'archive'
        options.record_count = len(data)
        options.frequency = frequency
        options.units = 'US'

        options.console = random_string()
        options.log_file = None
        options.conf = random_string()
        options.verbose = random_string()

        options.archive_interval = None
        options.archive_delay = None        

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.MQTTSubscribeService'):
                    with mock.patch('user.MQTTSubscribe.weewx'):
                        with mock.patch('user.MQTTSubscribe.weeutil'):
                            with mock.patch('user.MQTTSubscribe.to_sorted_string'):

                                mock_time.time.return_value = current_time

                                SUT = user.MQTTSubscribe.Simulator(None, options)

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
        frequency = 300

        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / frequency) + 1) * frequency
        sleep_amount = end_period_ts - current_time

        options = argparse.Namespace()
        options.type = 'service'
        options.binding = 'loop'
        options.record_count = len(data)
        options.frequency = frequency
        options.units = 'US'

        options.log_file = None
        options.console = random_string()
        options.conf = random_string()
        options.verbose = random_string()

        options.archive_interval = None
        options.archive_delay = None        

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.MQTTSubscribeService'):
                    with mock.patch('user.MQTTSubscribe.weewx'):
                        with mock.patch('user.MQTTSubscribe.weeutil'):
                            with mock.patch('user.MQTTSubscribe.to_sorted_string'):

                                mock_time.time.return_value = current_time

                                SUT = user.MQTTSubscribe.Simulator(None, options)

                                mock_engine = mock.Mock()
                                SUT.engine = mock_engine
                                SUT.config_dict = {}
                                SUT.config_dict['MQTTSubscribeDriver'] = {}

                                SUT.run()
                                mock_time.sleep.assert_called_once_with(sleep_amount)
                                mock_engine.dispatchEvent.assert_called_once()

class test_init_config(unittest.TestCase):
    def test_init_console(self):
        config_dict = {}
        binding = 'loop'

        options = argparse.Namespace()
        options.log_file = random_string()

        MQTTSubscribeService_binding_config = {
            'MQTTSubscribeService': {
                'binding': binding
            }
        }

        MQTTSubscribeService_logfile_config = {
            'MQTTSubscribeService': {
                'logging_filename': options.log_file
            }
        }

        MQTTSubscribeService_console_config = {
            'MQTTSubscribeService': {
                'console': True
            }
        }

        MQTTSubscribeDriver_logfile_config = {
            'MQTTSubscribeDriver': {
                'logging_filename': options.log_file
            }
        }

        MQTTSubscribeDriver_console_config = {
            'MQTTSubscribeDriver': {
                'console': True
            }
        }

        options.binding = binding
        options.console = random_string()

        options.type = random_string()
        options.record_count = random.randint(1, 99)
        options.archive_interval = random.randint(1, 99)
        options.archive_delay = random.randint(1, 99)
        options.units = None

        options.conf = random_string()
        options.verbose = random_string()

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.os'):
                with mock.patch('user.MQTTSubscribe.configobj') as mock_configobj:
                    with mock.patch('user.MQTTSubscribe.weeutil'):
                        with mock.patch('user.MQTTSubscribe.merge_config') as mock_merge_config:
                            mock_configobj.ConfigObj.return_value = config_dict

                            SUT = user.MQTTSubscribe.Simulator(None, options)

                            SUT.init_configuration()

                            call_args_list = mock_merge_config.call_args_list

                            self.assertEqual(len(call_args_list), 5)
                            self.assertEqual(call_args_list[0].args[0], config_dict)
                            self.assertEqual(call_args_list[0].args[1], MQTTSubscribeService_binding_config)
                            self.assertEqual(call_args_list[1].args[0], config_dict)
                            self.assertEqual(call_args_list[1].args[1], MQTTSubscribeService_logfile_config)

                            self.assertEqual(call_args_list[2].args[0], config_dict)
                            self.assertEqual(call_args_list[2].args[1], MQTTSubscribeDriver_logfile_config)

                            self.assertEqual(call_args_list[3].args[0], config_dict)
                            self.assertEqual(call_args_list[3].args[1], MQTTSubscribeService_console_config)
                            self.assertEqual(call_args_list[4].args[0], config_dict)
                            self.assertEqual(call_args_list[4].args[1], MQTTSubscribeDriver_console_config)

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestConfigureFields('test_use_topic_as_fieldname'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
