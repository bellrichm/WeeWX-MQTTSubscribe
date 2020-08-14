# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest
import mock

import configobj
import paho.mqtt.client
import random
import ssl
import string

import test_weewx_stubs

from user.MQTTSubscribe import MQTTSubscribe, Logger

class Msg(object):
    # pylint: disable=too-few-public-methods
    def __init(self):
        pass

class TestInitialization(unittest.TestCase):
    @staticmethod
    def test_username_None():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': None,
            'password': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),  # pylint: disable=unused-variable
            'archive_topic': None,
            'message_callback': {},
            'topics': {
                'foobar': {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                # pylint: disable=no-member
                SUT = MQTTSubscribe(config, mock_logger)

                SUT.client.username_pw_set.assert_not_called()
                SUT.client.connect.assert_called_once_with(host, port, keepalive)

    @staticmethod
    def test_password_None():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),  # pylint: disable=unused-variable
            'password': None,
            'archive_topic': None,
            'message_callback': {},
            'topics': {
                'foobar': {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                # pylint: disable=no-member
                SUT = MQTTSubscribe(config, mock_logger)

                SUT.client.username_pw_set.assert_not_called()
                SUT.client.connect.assert_called_once_with(host, port, keepalive)

    @staticmethod
    def test_username_and_password_None():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': None,
            'password': None,
            'archive_topic': None,
            'message_callback': {},
            'topics': {
                'foobar': {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                # pylint: disable=no-member
                SUT = MQTTSubscribe(config, mock_logger)

                SUT.client.username_pw_set.assert_not_called()
                SUT.client.connect.assert_called_once_with(host, port, keepalive)

    @staticmethod
    def test_username_and_password_set():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        username = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        password = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        config_dict = {
            'console': False,
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': username,
            'password': password,
            'archive_topic': None,
            'message_callback': {},
            'topics': {
                'foobar': {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                # pylint: disable=no-member
                SUT = MQTTSubscribe(config, mock_logger)

                SUT.client.username_pw_set.assert_called_once_with(username, password)
                SUT.client.connect.assert_called_once_with(host, port, keepalive)

class Testtls_configuration(unittest.TestCase):
    def test_missing_PROTOCOL_TLS(self):
        tls_version = 'tls'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                'tls_version': tls_version
            },
            'topics': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                try:
                    del ssl.PROTOCOL_TLS
                except AttributeError:
                    pass
                with self.assertRaises(ValueError) as error:
                    MQTTSubscribe(config, mock_logger)
                self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_TLSv1(self):
        tls_version = 'tlsv1'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                'tls_version': tls_version
            },
            'topics': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                try:
                    del ssl.PROTOCOL_TLSv1
                except AttributeError:
                    pass
                with self.assertRaises(ValueError) as error:
                    MQTTSubscribe(config, mock_logger)
                self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_TLSv1_1(self):
        tls_version = 'tlsv1_1'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                'tls_version': tls_version
            },
            'topics': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                try:
                    del ssl.PROTOCOL_TLSv1_1
                except AttributeError:
                    pass
                with self.assertRaises(ValueError) as error:
                    MQTTSubscribe(config, mock_logger)
                self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_TLSv1_2(self):
        tls_version = 'tlsv1_2'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                'tls_version': tls_version
            },
            'topics': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                try:
                    del ssl.PROTOCOL_TLSv1_2
                except AttributeError:
                    pass
                with self.assertRaises(ValueError) as error:
                    MQTTSubscribe(config, mock_logger)
                self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_SSLv2(self):
        tls_version = 'sslv2'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                'tls_version': tls_version
            },
            'topics': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                try:
                    del ssl.PROTOCOL_SSLv2
                except AttributeError:
                    pass
                with self.assertRaises(ValueError) as error:
                    MQTTSubscribe(config, mock_logger)
                self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_SSLv23(self):
        tls_version = 'sslv23'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                'tls_version': tls_version
            },
            'topics': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                try:
                    del ssl.PROTOCOL_SSLv23
                except AttributeError:
                    pass
                with self.assertRaises(ValueError) as error:
                    MQTTSubscribe(config, mock_logger)
                self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_SSLv3(self):
        tls_version = 'sslv3'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                'tls_version': tls_version
            },
            'topics': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                try:
                    del ssl.PROTOCOL_SSLv3
                except AttributeError:
                    pass
                with self.assertRaises(ValueError) as error:
                    MQTTSubscribe(config, mock_logger)
                self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_invalid_certs_required(self):
        certs_required = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                'certs_required': certs_required
                },
            'topics': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                try:
                    del ssl.PROTOCOL_SSLv3
                except AttributeError:
                    pass
                with self.assertRaises(ValueError) as error:
                    MQTTSubscribe(config, mock_logger)
                self.assertEqual(error.exception.args[0], "Invalid 'certs_required'., %s" % certs_required)

    def test_missing_ca_certs(self):
        config_dict = {
            'message_callback': {},
            'tls': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): \
                     ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
            },
            'topics': {
                ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                try:
                    del ssl.PROTOCOL_SSLv3
                except AttributeError:
                    pass
                with self.assertRaises(ValueError) as error:
                    MQTTSubscribe(config, mock_logger)
                self.assertEqual(error.exception.args[0], "'ca_certs' is required.")

class Teston_connect(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = test_weewx_stubs.UNITS_CONSTANTS[unit_system_name]
    config_dict = {
        'console': False,
        'full_topic_fieldname': False,
        'keyword_delimiter': None,
        'keyword_separator': None,
        'host': 'host',
        'keepalive': random.randint(1, 10),
        'port': random.randint(1, 10),
        'username': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
        'password': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
        'archive_topic': None
    }

    def test_multiple_topics(self):
        topic1 = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        topic2 = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topics'] = {}
        config_dict['topics'][topic1] = {}
        config_dict['topics'][topic2] = {}
        config_dict['message_callback'] = {}

        config = configobj.ConfigObj(config_dict)

        subscribed_topics = dict(config_dict['topics'])
        qos = 0

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager') as mock_manager:
                    type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value=subscribed_topics)
                    type(mock_manager.return_value).get_qos = mock.Mock(return_value=qos)
                    mock_client.subscribe.return_value = [1, 0]

                    SUT = MQTTSubscribe(config, mock_logger)

                    rc = random.randint(1, 10)
                    userdata = {}
                    userdata['connect'] = False
                    SUT._on_connect(mock_client, userdata, None, rc,)   # pylint: disable=protected-access

                    self.assertEqual(mock_client.subscribe.call_count, 2)
                    mock_client.subscribe.assert_any_call(topic1, qos)
                    mock_client.subscribe.assert_any_call(topic2, qos)

if __name__ == '__main__':
    unittest.main(exit=False)
