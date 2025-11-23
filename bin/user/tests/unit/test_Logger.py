#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import unittest
import mock

import configobj
import random
import sys
import time

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
            with mock.patch('user.MQTTSubscribe.threading') as mock_threading:
                mock_logging._checkLevel.return_value = 0
                thread_id = random.randint(10000, 99999)
                mock_threading.get_native_id.return_value = thread_id
                mode = random_string()
                message_text = random_string()

                SUT = Logger({'mode': mode})

                SUT.error(random.randint(1, 100), message_text)

                SUT._logmsg.error.assert_called_once_with(SUT.MSG_FORMAT, mode, thread_id, -1, message_text)

    @staticmethod
    def test_info_logged():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.threading') as mock_threading:
                mock_logging._checkLevel.return_value = 0
                thread_id = random.randint(10000, 99999)
                mock_threading.get_native_id.return_value = thread_id
                mode = random_string()
                message = random_string()

                SUT = Logger({'mode': mode})

                SUT.info(random.randint(1, 100), message)

                SUT._logmsg.info.assert_called_once_with(SUT.MSG_FORMAT, mode, thread_id, -1, message)

    @staticmethod
    def test_debug_logged():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.threading') as mock_threading:
                mock_logging._checkLevel.return_value = 0
                thread_id = random.randint(10000, 99999)
                mock_threading.get_native_id.return_value = thread_id
                mode = random_string()
                message = random_string()

                SUT = Logger({'mode': mode})

                SUT.debug(random.randint(1, 100), message)

                SUT._logmsg.debug.assert_called_once_with(SUT.MSG_FORMAT, mode, thread_id, -1, message)

    @staticmethod
    def test_trace_logged_with_debug_set():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.threading') as mock_threading:
                sys.modules['weewx'].debug = 2
                mock_logging._checkLevel.return_value = 0
                thread_id = random.randint(10000, 99999)
                mock_threading.get_native_id.return_value = thread_id
                mode = random_string()
                message = random_string()

                SUT = Logger({'mode': mode})

                SUT.trace(random.randint(1, 100), message)

                SUT._logmsg.debug.assert_called_once_with(SUT.MSG_FORMAT, mode, thread_id, -1, message)

    @staticmethod
    def test_trace_logged_with_debug_not_set():
        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.threading') as mock_threading:
                mock_logging._checkLevel.return_value = 0
                thread_id = random.randint(10000, 99999)
                mock_threading.get_native_id.return_value = thread_id
                mode = random_string()
                message = random_string()

                SUT = Logger({'mode': mode})
                SUT.weewx_debug = 0

                SUT.trace(random.randint(1, 100), message)

                SUT._logmsg.log.assert_called_once_with(5, SUT.MSG_FORMAT, mode, thread_id, -1, message)

class TestThrottling(unittest.TestCase):
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

    def test_duration_is_zero(self):
        msg_id = random_string()
        duration = 0
        max = random.randint(1, 1000)

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': {
                    msg_id: {
                        'duration': duration,
                        'max': max
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_logging._checkLevel.return_value = 0

                SUT = Logger(config)

                throttle = SUT._check_message(msg_id, SUT.throttle_config['message'][msg_id])

                self.assertTrue(throttle)
                self.assertEqual(len(SUT.logged_ids), 0)
                self.assertEqual(mock_time.timer.call_count, 0)

    def test_max_is_none(self):
        msg_id = random_string()
        duration = random.randint(60, 600)
        max = 'None'

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': {
                    msg_id: {
                        'duration': duration,
                        'max': max
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_logging._checkLevel.return_value = 0

                SUT = Logger(config)

                throttle = SUT._check_message(msg_id, SUT.throttle_config['message'][msg_id])

                self.assertFalse(throttle)
                self.assertEqual(len(SUT.logged_ids), 0)
                self.assertEqual(mock_time.timer.call_count, 0)

    def test_frst_time_message_is_logged(self):
        msg_id = random_string()
        duration = random.randint(60, 600)
        max = random.randint(1, 1000)
        now = time.time()

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': {
                    msg_id: {
                        'duration': duration,
                        'max': max
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_logging._checkLevel.return_value = 0
                mock_time.time.return_value = now

                SUT = Logger(config)

                throttle = SUT._check_message(msg_id, SUT.throttle_config['message'][msg_id])

                logged_ids = {
                    msg_id: {
                        'window': now // duration,
                        'count': 1,
                        'previous_count': 0,
                    }
                }

                self.assertFalse(throttle)
                self.assertEqual(len(SUT.logged_ids), 1)
                self.assertDictEqual(SUT.logged_ids, logged_ids)

    def test_new_window(self):
        msg_id = random_string()
        duration = random.randint(60, 600)
        max = random.randint(1, 1000)
        count = random.randint(1, 100)
        previous_count = random.randint(1, 100)
        now = time.time()

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': {
                    msg_id: {
                        'duration': duration,
                        'max': max
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_logging._checkLevel.return_value = 0
                mock_time.time.return_value = now

                SUT = Logger(config)

                SUT.logged_ids = {
                    msg_id: {
                        'window': -1,
                        'count': count,
                        'previous_count': previous_count,
                    }
                }

                throttle = SUT._check_message(msg_id, SUT.throttle_config['message'][msg_id])

                logged_ids = {
                    msg_id: {
                        'window': now // duration,
                        'count': 1,
                        'previous_count': count,
                    }
                }

                self.assertFalse(throttle)
                self.assertEqual(len(SUT.logged_ids), 1)
                self.assertDictEqual(SUT.logged_ids, logged_ids)

    def test_message_within_threshold(self):
        msg_id = random_string()
        duration = random.randint(60, 600)
        count = random.randint(1, 100)
        previous_count = random.randint(1, 100)
        max = count + previous_count + 1
        now = time.time()

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': {
                    msg_id: {
                        'duration': duration,
                        'max': max
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_logging._checkLevel.return_value = 0
                mock_time.time.return_value = now

                SUT = Logger(config)

                SUT.logged_ids = {
                    msg_id: {
                        'window': -1,
                        'count': count,
                        'previous_count': previous_count,
                    }
                }

                throttle = SUT._check_message(msg_id, SUT.throttle_config['message'][msg_id])

                logged_ids = {
                    msg_id: {
                        'window': now // duration,
                        'count': 1,
                        'previous_count': count,
                    }
                }

                self.assertFalse(throttle)
                self.assertEqual(len(SUT.logged_ids), 1)
                self.assertDictEqual(SUT.logged_ids, logged_ids)

    def test_threshold_is_met(self):
        now = time.time()
        mode = random_string()
        msg_id = random_string()
        duration = random.randint(60, 600)
        count = random.randint(1, 100)
        previous_count = random.randint(1, 100)
        window_elapsed = now % duration / duration
        threshold = round(count * (1 - window_elapsed) + 1)
        max = threshold

        config_dict = {
            'mode': mode,
            'throttle': {
                'messages': {
                    msg_id: {
                        'duration': duration,
                        'max': max
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.threading') as mock_threading:
                    mock_logging._checkLevel.return_value = 0
                    mock_time.time.return_value = now
                    thread_id = random.randint(10000, 99999)
                    mock_threading.get_native_id.return_value = thread_id

                    SUT = Logger(config)

                    SUT.logged_ids = {
                        msg_id: {
                            'window': -1,
                            'count': count,
                            'previous_count': previous_count,
                        }
                    }

                    throttle = SUT._check_message(msg_id, SUT.throttle_config['message'][msg_id])

                    logged_ids = {
                        msg_id: {
                            'window': now // duration,
                            'count': 1,
                            'previous_count': count,
                        }
                    }
                    message_text = f"{threshold} messages have been suppressed."

                    self.assertTrue(throttle)
                    self.assertEqual(len(SUT.logged_ids), 1)
                    self.assertDictEqual(SUT.logged_ids, logged_ids)
                    SUT._logmsg.error.assert_called_once_with(SUT.MSG_FORMAT, mode, thread_id, -1, message_text)

    def test_message_is_over_threshold(self):
        mode = random_string()
        msg_id = random_string()
        duration = random.randint(60, 600)
        count = random.randint(1, 100)
        previous_count = random.randint(1, 100)
        max = count - 2
        now = duration

        config_dict = {
            'mode': mode,
            'throttle': {
                'messages': {
                    msg_id: {
                        'duration': duration,
                        'max': max
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.threading') as mock_threading:
                    mock_logging._checkLevel.return_value = 0
                    mock_time.time.return_value = now
                    thread_id = random.randint(10000, 99999)
                    mock_threading.get_native_id.return_value = thread_id

                    SUT = Logger(config)

                    SUT.logged_ids = {
                        msg_id: {
                            'window': -1,
                            'count': count,
                            'previous_count': previous_count,
                        }
                    }

                    throttle = SUT._check_message(msg_id, SUT.throttle_config['message'][msg_id])

                    logged_ids = {
                        msg_id: {
                            'window': now // duration,
                            'count': 1,
                            'previous_count': count,
                        }
                    }

                    self.assertTrue(throttle)
                    self.assertEqual(len(SUT.logged_ids), 1)
                    self.assertDictEqual(SUT.logged_ids, logged_ids)

    def test_initialization(self):
        print('start')

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            mock_logging._checkLevel.return_value = 0

            config_dict = {
                'mode': random_string(),
                'throttle': {
                    'category': {
                        'ALL': {
                            'duration': 300,
                            'max': 2
                        },
                        'ERROR': {
                            'duration': 300,
                            'max': 5,
                        },
                    },
                    'messages': {
                        'REPLACE_ME_with_specific_message_ids': {
                            'messages': ['m1', 'm2'],
                            'duration': 0,
                            'max': 1
                        },
                        'REPLACE_ME_with_single_message_id': {
                            'duration': 1,
                            'max': 0
                        }
                    }
                }
            }
            config = configobj.ConfigObj(config_dict)

            Logger(config)

        print('end')

    def test_test(self):
        print('start')
        now = time.time()

        with mock.patch('user.MQTTSubscribe.logging') as mock_logging:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_logging._checkLevel.return_value = 0
                mock_time.time.return_value = now

                config_dict = {
                    'mode': random_string(),
                    'throttle': {
                        'category': {
                            'ALL': {
                                'duration': 300,
                                'max': 2
                            },
                            'ERROR': {
                                'duration': 300,
                                'max': 5,
                            },
                        },
                        'messages': {
                            'REPLACE_ME_with_specific_message_ids': {
                                'messages': ['m1', 'm2'],
                                'duration': 0,
                                'max': 1
                            },
                            'm3': {
                                'duration': 1,
                                'max': 'none'
                            }
                        }
                    }
                }
                config = configobj.ConfigObj(config_dict)

                SUT = Logger(config)

                SUT._is_throttled("ERROR", 'm3')

            # SUT._logmsg.addHandler.assert_called_once()
        print('end')


if __name__ == '__main__':
    # testcase = sys.argv[1]
    testcase = 'test_new_window'

    test_suite = unittest.TestSuite()
    test_suite.addTest(TestThrottling(testcase))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
