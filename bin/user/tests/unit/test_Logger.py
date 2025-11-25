#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import unittest
import mock

import configobj
import copy
import random
import sys
import time

import test_weewx_stubs
from test_weewx_stubs import BaseTestClass, random_string
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import Logger

class TestInintialization(BaseTestClass):
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

    def test_throttle_not_in_config(self):
        config_dict = {
            'mode': random_string(),
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': {},
            'message': {},
        }

        SUT = Logger(config)
        self.assertDictEqual(SUT.throttle_config, expected_throttle_config)

    def test_empty_throttle_section(self):
        config_dict = {
            'mode': random_string(),
            'throttle': {}
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': {},
            'message': {},
        }

        SUT = Logger(config)
        self.assertDictEqual(SUT.throttle_config, expected_throttle_config)

    def test_throttle_category_section(self):
        category = {
            random_string(): {
                random_string(): random.randint(1, 10),
            }
        }

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'category': copy.deepcopy(category),
            }
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': copy.deepcopy(category),
            'message': {},
        }

        SUT = Logger(config)
        self.assertDictEqual(SUT.throttle_config, expected_throttle_config)

    def test_no_messages_specified_in_message_section(self):
        message_id = random_string()
        message = {
            message_id: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
            }
        }

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': {},
            'message': {
                message_id: copy.deepcopy(message[message_id])
            },
        }

        SUT = Logger(config)
        self.assertDictEqual(SUT.throttle_config, expected_throttle_config)

    def test_single_message_specified_in_message_section(self):
        messages_name = random_string()
        message_ids = random_string()
        message = {
            messages_name: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
                'messages': message_ids,
            }
        }

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': {},
            'message': {
                message_ids: copy.deepcopy(message[messages_name])
            },
        }
        del expected_throttle_config['message'][message_ids]['messages']

        SUT = Logger(config)
        self.assertDictEqual(SUT.throttle_config, expected_throttle_config)

    def test_multiple_messages_specified_in_message_section(self):
        messages_name = random_string()
        message_ids = [random_string(), random_string()]
        duration = random.randint(1, 10)
        max = random.randint(1, 10)
        message = {
            messages_name: {
                'duration': duration,
                'max': max,
                'messages': message_ids,
            }
        }

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        expected_throttle_config = {
            'category': {},
            'message': {
            },
        }
        for message_id in message_ids:
            expected_throttle_config['message'][message_id] = {
                'duration': duration,
                'max': max,
            }

        SUT = Logger(config)
        self.assertDictEqual(SUT.throttle_config, expected_throttle_config)

    def test_message_id_in_list_already_specified(self):
        messages_name = random_string()
        message_ids = random_string()
        message = {
            message_ids: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
            },
            messages_name: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
                'messages': message_ids,
            },
        }

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            Logger(config)

        self.assertEqual(error.exception.args[0], f"{message_ids} has been configured multiple times")

    def test_message_id_already_specified(self):
        messages_name = random_string()
        message_ids = random_string()
        message = {
            messages_name: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
                'messages': message_ids,
            },
            message_ids: {
                'duration': random.randint(1, 10),
                'max': random.randint(1, 10),
            },
        }

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'messages': copy.deepcopy(message),
            }
        }
        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            Logger(config)

        self.assertEqual(error.exception.args[0], f"{message_ids} has been configured multiple times")

    def test_is_throttled_all_level_id_set(self):
        logging_level = random_string()
        message_id = random_string()

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'category': {
                    'ALL': {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    },
                    logging_level: {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    },
                },                
                'messages': {
                    message_id: {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch.object(Logger, '_check_message') as mock_check_message:
            SUT = Logger(config)
            SUT._is_throttled(logging_level, message_id)

            mock_check_message.assert_called_once_with(message_id, config_dict['throttle']['messages'][message_id])

    def test_is_throttled_all_level_set(self):
        logging_level = random_string()
        message_id = random_string()
        random_message_id = random_string()

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'category': {
                    'ALL': {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    },
                    logging_level: {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    },
                },                
                'messages': {
                    message_id: {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch.object(Logger, '_check_message') as mock_check_message:
            SUT = Logger(config)
            SUT._is_throttled(logging_level, random_message_id)

            mock_check_message.assert_called_once_with(random_message_id, config_dict['throttle']['category'][logging_level])

    def test_is_throttled_all_set(self):
        logging_level = random_string()
        message_id = random_string()
        random_message_id = random_string()

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'category': {
                    'ALL': {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    },
                    logging_level: {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    },
                },                
                'messages': {
                    message_id: {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch.object(Logger, '_check_message') as mock_check_message:
            SUT = Logger(config)
            SUT._is_throttled(random_string(), random_message_id)

            mock_check_message.assert_called_once_with(random_message_id, config_dict['throttle']['category']['ALL'])

    def test_is_throttled_no_match(self):
        logging_level = random_string()
        message_id = random_string()
        random_message_id = random_string()

        config_dict = {
            'mode': random_string(),
            'throttle': {
                'category': {
                    logging_level: {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    },
                },                
                'messages': {
                    message_id: {
                        'duration': random.randint(1, 10),
                        'max': random.randint(1, 10),                        
                    }
                }
            }
        }
        config = configobj.ConfigObj(config_dict)

        with mock.patch.object(Logger, '_check_message') as mock_check_message:
            SUT = Logger(config)
            SUT._is_throttled(random_string(), random_message_id)

            mock_check_message.assert_not_called()

class TestLogging(BaseTestClass):
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

class TestThrottling(BaseTestClass):
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

                SUT.logged_ids = {
                    msg_id: {
                        'count': random.randint(1,10),
                    }
                }

                throttle = SUT._check_message(msg_id, SUT.throttle_config['message'][msg_id])

                self.assertTrue(throttle)
                self.assertEqual(len(SUT.logged_ids), 1)
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

    def test_first_time_message_is_logged(self):
        msg_id = random_string()
        duration = random.randint(60, 600)
        max = random.randint(1, 1000)
        now = int(time.time())

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
                        'passed_threshold': False,
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
                        'passed_threshold': False,
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
                        'passed_threshold': False,
                    }
                }

                self.assertFalse(throttle)
                self.assertEqual(len(SUT.logged_ids), 1)
                self.assertDictEqual(SUT.logged_ids, logged_ids)

    def test_first_time_passed_threshold(self):
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
                            'passed_threshold': True,
                        }
                    }
                    window_elapsed = (now % duration) / duration
                    threshold = count * (1 - window_elapsed) + 1

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
                            'window': now // duration,
                            'count': count,
                            'previous_count': previous_count,
                            'passed_threshold': True,
                        }
                    }

                    throttle = SUT._check_message(msg_id, SUT.throttle_config['message'][msg_id])

                    logged_ids = {
                        msg_id: {
                            'window': now // duration,
                            'count': count + 1,
                            'previous_count': previous_count,
                            'passed_threshold': True,
                        }
                    }

                    self.assertTrue(throttle)
                    self.assertEqual(len(SUT.logged_ids), 1)
                    self.assertDictEqual(SUT.logged_ids, logged_ids)

if __name__ == '__main__':
    # testcase = sys.argv[1]
    testcase = 'test_message_is_over_threshold'

    test_suite = unittest.TestSuite()
    test_suite.addTest(TestThrottling(testcase))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
