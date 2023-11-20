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
        interval = 60
        delay = 5

        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / interval) + 1) * interval
        end_delay_ts = end_period_ts + delay
        sleep_amount = end_delay_ts - current_time

        options = argparse.Namespace()
        options.type = 'driver'
        options.binding = 'archive'
        options.record_count = len(data)
        options.interval = interval
        options.delay = delay
        options.units = 'US'

        options.callback = random_string()
        options.topics = random_string()
        options.host = random_string()
        options.console = random_string()
        options.config_file = random_string()
        options.verbose = random_string()

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

                                SUT = user.MQTTSubscribe.Simulator(options)

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
        options.units = 'US'

        options.interval = random.randint(1, 99)
        options.delay = random.randint(1, 99)
        options.callback = random_string()
        options.topics = random_string()
        options.host = random_string()
        options.console = random_string()
        options.config_file = random_string()
        options.verbose = random_string()

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

                            SUT = user.MQTTSubscribe.Simulator(options)

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
        options.binding = 'archive'
        options.record_count = len(data)
        options.interval = interval
        options.delay = delay
        options.units = 'US'

        options.callback = random_string()
        options.topics = random_string()
        options.host = random_string()
        options.console = random_string()
        options.config_file = random_string()
        options.verbose = random_string()

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.MQTTSubscribeService'):
                    with mock.patch('user.MQTTSubscribe.weewx'):
                        with mock.patch('user.MQTTSubscribe.weeutil'):
                            with mock.patch('user.MQTTSubscribe.to_sorted_string'):

                                mock_time.time.return_value = current_time

                                SUT = user.MQTTSubscribe.Simulator(options)

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
        options.units = 'US'

        options.callback = random_string()
        options.topics = random_string()
        options.host = random_string()
        options.console = random_string()
        options.config_file = random_string()
        options.verbose = random_string()

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.MQTTSubscribeService'):
                    with mock.patch('user.MQTTSubscribe.weewx'):
                        with mock.patch('user.MQTTSubscribe.weeutil'):
                            with mock.patch('user.MQTTSubscribe.to_sorted_string'):

                                mock_time.time.return_value = current_time

                                SUT = user.MQTTSubscribe.Simulator(options)

                                mock_engine = mock.Mock()
                                SUT.engine = mock_engine
                                SUT.config_dict = {}
                                SUT.config_dict['MQTTSubscribeDriver'] = {}

                                SUT.run()
                                mock_time.sleep.assert_called_once_with(sleep_amount)
                                mock_engine.dispatchEvent.assert_called_once()

class test_init_config(unittest.TestCase):
    def test_init_topics(self):
        # pylint:  disable=too-many-locals
        config_dict = {
            'MQTTSubscribeDriver': {
                'topics': {}
            },
            'MQTTSubscribeService': {
                'topics': {}
            }
        }
        binding = 'loop'
        topic_count = random.randint(1, 5)

        MQTTSubscribeService_binding_config = {
            'MQTTSubscribeService': {
                'binding': binding
            }
        }

        topics = []
        i = 0
        while i < topic_count:
            topics.append(random_string())
            i += 1

        topics_string = ','.join(topics)

        options = argparse.Namespace()
        options.binding = binding
        options.callback = None
        options.topics = topics_string
        options.host = None
        options.console = None

        options.type = None
        options.record_count = random.randint(1, 99)
        options.interval = random.randint(1, 99)
        options.delay = random.randint(1, 99)
        options.units = None

        options.config_file = random_string()
        options.verbose = random_string()

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.os'):
                with mock.patch('user.MQTTSubscribe.configobj') as mock_configobj:
                    with mock.patch('user.MQTTSubscribe.weeutil'):
                        with mock.patch('user.MQTTSubscribe.merge_config') as mock_merge_config:

                            mock_configobj.ConfigObj.return_value = config_dict

                            SUT = user.MQTTSubscribe.Simulator(options)

                            SUT.init_configuration()

                            call_args_list = mock_merge_config.call_args_list

                            self.assertEqual(len(call_args_list), 1 + (2 * topic_count))
                            self.assertEqual(call_args_list[0].args[0], config_dict)
                            self.assertEqual(call_args_list[0].args[1], MQTTSubscribeService_binding_config)

                            i = 0
                            while i < topic_count:
                                MQTTSubscribeService_topic_config = {
                                    'MQTTSubscribeService': {
                                        'topics':  {
                                            topics[i]: {}
                                        }
                                    }
                                }

                                MQTTSubscribeDriver_topic_config = {
                                    'MQTTSubscribeDriver': {
                                        'topics': {
                                            topics[i]: {}
                                        }
                                    }
                                }

                                self.assertEqual(call_args_list[2*i+1].args[0], config_dict)
                                self.assertEqual(call_args_list[2*i+1].args[1], MQTTSubscribeService_topic_config)
                                self.assertEqual(call_args_list[2*i+2].args[0], config_dict)
                                self.assertEqual(call_args_list[2*i+2].args[1], MQTTSubscribeDriver_topic_config)
                                i += 1

    def test_init_host(self):
        config_dict = {}
        binding = 'loop'
        host = random_string()

        MQTTSubscribeService_binding_config = {
            'MQTTSubscribeService': {
                'binding': binding
            }
        }

        MQTTSubscribeService_host_config = {
            'MQTTSubscribeService': {
                'host':  host
            }
        }

        MQTTSubscribeDriver_host_config = {
            'MQTTSubscribeDriver': {
                'host': host
            }
        }

        options = argparse.Namespace()
        options.binding = binding
        options.callback = None
        options.topics = None
        options.host = host
        options.console = None

        options.type = None
        options.record_count = random.randint(1, 99)
        options.interval = random.randint(1, 99)
        options.delay = random.randint(1, 99)
        options.units = None

        options.config_file = random_string()
        options.verbose = random_string()

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.os'):
                with mock.patch('user.MQTTSubscribe.configobj') as mock_configobj:
                    with mock.patch('user.MQTTSubscribe.weeutil'):
                        with mock.patch('user.MQTTSubscribe.merge_config') as mock_merge_config:
                            mock_configobj.ConfigObj.return_value = config_dict

                            SUT = user.MQTTSubscribe.Simulator(options)

                            SUT.init_configuration()

                            call_args_list = mock_merge_config.call_args_list

                            self.assertEqual(len(call_args_list), 3)
                            self.assertEqual(call_args_list[0].args[0], config_dict)
                            self.assertEqual(call_args_list[0].args[1], MQTTSubscribeService_binding_config)
                            self.assertEqual(call_args_list[1].args[0], config_dict)
                            self.assertEqual(call_args_list[1].args[1], MQTTSubscribeService_host_config)
                            self.assertEqual(call_args_list[2].args[0], config_dict)
                            self.assertEqual(call_args_list[2].args[1], MQTTSubscribeDriver_host_config)

    def test_init_callback(self):
        config_dict = {}
        binding = 'loop'
        callback = random_string()

        MQTTSubscribeService_binding_config = {
            'MQTTSubscribeService': {
                'binding': binding
            }
        }

        MQTTSubscribeService_callback_config = {
            'MQTTSubscribeService': {
                'message_callback': {
                    'type': callback
                }
            }
        }

        MQTTSubscribeDriver_callback_config = {
            'MQTTSubscribeDriver': {
                'message_callback': {
                    'type': callback
                }
            }
        }

        options = argparse.Namespace()
        options.binding = binding
        options.callback = callback
        options.topics = None
        options.host = None
        options.console = None

        options.type = None
        options.record_count = random.randint(1, 99)
        options.interval = random.randint(1, 99)
        options.delay = random.randint(1, 99)
        options.units = None

        options.config_file = random_string()
        options.verbose = random_string()

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.os'):
                with mock.patch('user.MQTTSubscribe.configobj') as mock_configobj:
                    with mock.patch('user.MQTTSubscribe.weeutil'):
                        with mock.patch('user.MQTTSubscribe.merge_config') as mock_merge_config:
                            mock_configobj.ConfigObj.return_value = config_dict

                            SUT = user.MQTTSubscribe.Simulator(options)

                            SUT.init_configuration()

                            call_args_list = mock_merge_config.call_args_list

                            self.assertEqual(len(call_args_list), 3)
                            self.assertEqual(call_args_list[0].args[0], config_dict)
                            self.assertEqual(call_args_list[0].args[1], MQTTSubscribeService_binding_config)
                            self.assertEqual(call_args_list[1].args[0], config_dict)
                            self.assertEqual(call_args_list[1].args[1], MQTTSubscribeService_callback_config)
                            self.assertEqual(call_args_list[2].args[0], config_dict)
                            self.assertEqual(call_args_list[2].args[1], MQTTSubscribeDriver_callback_config)

    def test_init_console(self):
        config_dict = {}
        binding = 'loop'

        MQTTSubscribeService_binding_config = {
            'MQTTSubscribeService': {
                'binding': binding
            }
        }

        MQTTSubscribeService_console_config = {
            'MQTTSubscribeService': {
                'console': True
            }
        }

        MQTTSubscribeDriver_console_config = {
            'MQTTSubscribeDriver': {
                'console': True
            }
        }

        options = argparse.Namespace()
        options.binding = binding
        options.callback = None
        options.topics = None
        options.host = None
        options.console = random_string()

        options.type = None
        options.record_count = random.randint(1, 99)
        options.interval = random.randint(1, 99)
        options.delay = random.randint(1, 99)
        options.units = None

        options.config_file = random_string()
        options.verbose = random_string()

        with mock.patch('user.MQTTSubscribe.print'):
            with mock.patch('user.MQTTSubscribe.os'):
                with mock.patch('user.MQTTSubscribe.configobj') as mock_configobj:
                    with mock.patch('user.MQTTSubscribe.weeutil'):
                        with mock.patch('user.MQTTSubscribe.merge_config') as mock_merge_config:
                            mock_configobj.ConfigObj.return_value = config_dict

                            SUT = user.MQTTSubscribe.Simulator(options)

                            SUT.init_configuration()

                            call_args_list = mock_merge_config.call_args_list

                            self.assertEqual(len(call_args_list), 3)
                            self.assertEqual(call_args_list[0].args[0], config_dict)
                            self.assertEqual(call_args_list[0].args[1], MQTTSubscribeService_binding_config)
                            self.assertEqual(call_args_list[1].args[0], config_dict)
                            self.assertEqual(call_args_list[1].args[1], MQTTSubscribeService_console_config)
                            self.assertEqual(call_args_list[2].args[0], config_dict)
                            self.assertEqual(call_args_list[2].args[1], MQTTSubscribeDriver_console_config)

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestConfigureFields('test_use_topic_as_fieldname'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
