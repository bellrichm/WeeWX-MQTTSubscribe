#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest
import mock

import configobj
import paho.mqtt.client
import random
import ssl
import types

import test_weewx_stubs
from test_weewx_stubs import random_string
from test_weewx_stubs import weewx
from test_weewx_stubs import weeutil

from user.MQTTSubscribe import MQTTSubscriber, Logger

class Msg(object):
    # pylint: disable=too-few-public-methods
    def __init(self):
        pass

class TestInitialization(unittest.TestCase):
    def test_mqtt_log_set(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {
            'message_callback': {},
            'topics': {
                random_string(): {}
            },
            'log': True
        }

        config = configobj.ConfigObj(config_dict)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=protected-access
                    SUT = MQTTSubscriber(config, mock_logger)

                    self.assertEqual(SUT.client.on_log, SUT._on_log)

    def test_mqtt_log_not_set(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {

            'message_callback': {},
            'topics': {
                random_string(): {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=protected-access
                    SUT = MQTTSubscriber(config, mock_logger)

                    self.assertNotEqual(SUT.client.on_log, SUT._on_log)

    def test_connect_exception(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {
            'message_callback': {},
            'topics': {
                random_string(): {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        exception = Exception("Connect exception.")

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                mock_client.return_value = mock_client
                mock_client.connect.side_effect = mock.Mock(side_effect=exception)
                with self.assertRaises(weewx.WeeWxIOError) as error:
                    with mock.patch('user.MQTTSubscribe.TopicManager'):
                        MQTTSubscriber(config, mock_logger)

                self.assertEqual(error.exception.args[0], exception)


    def test_missing_topics(self):
        config_dict = {

            'message_callback': {},
        }
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)
        with self.assertRaises(ValueError) as error:
            MQTTSubscriber(config, mock_logger)

        self.assertEqual(error.exception.args[0], "[[topics]] is required.")

    def test_missing_archive_topic_in_topics(self):
        archive_topic = random_string()
        config_dict = {
            'archive_topic': archive_topic,
            'message_callback': {},
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)
        with self.assertRaises(ValueError) as error:
            with mock.patch('user.MQTTSubscribe.TopicManager'):
                MQTTSubscriber(config, mock_logger)

        self.assertEqual(error.exception.args[0], ("Archive topic %s must be in [[topics]]" % archive_topic))

    @staticmethod
    def test_username_None():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': None,
            'password': random_string(),
            'archive_topic': None,
            'message_callback': {},
            'topics': {
                random_string(): {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=no-member
                    SUT = MQTTSubscriber(config, mock_logger)

                    SUT.client.username_pw_set.assert_not_called()
                    SUT.client.connect.assert_called_once_with(host, port, keepalive)

    @staticmethod
    def test_password_None():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': random_string(),
            'password': None,
            'archive_topic': None,
            'message_callback': {},
            'topics': {
                random_string(): {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=no-member
                    SUT = MQTTSubscriber(config, mock_logger)

                    SUT.client.username_pw_set.assert_not_called()
                    SUT.client.connect.assert_called_once_with(host, port, keepalive)

    @staticmethod
    def test_username_and_password_None():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
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
                random_string(): {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=no-member
                    SUT = MQTTSubscriber(config, mock_logger)

                    SUT.client.username_pw_set.assert_not_called()
                    SUT.client.connect.assert_called_once_with(host, port, keepalive)

    @staticmethod
    def test_username_and_password_set():
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        username = random_string()
        password = random_string()
        config_dict = {
            'console': False,
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
                random_string(): {}
            }
        }

        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=no-member
                    SUT = MQTTSubscriber(config, mock_logger)

                    SUT.client.username_pw_set.assert_called_once_with(username, password)
                    SUT.client.connect.assert_called_once_with(host, port, keepalive)
class  TestWeewx_configuration(unittest.TestCase):
    def tearDown(self):
        weewx.units.USUnits = weeutil.ListOfDicts({})

        weewx.units.MetricUnits = weeutil.ListOfDicts({})

        weewx.units.MetricWXUnits = weeutil.ListOfDicts({})

        weewx.units.default_unit_format_dict = {}

        weewx.units.default_unit_label_dict = {}

        weewx.units.conversionDict = {}
        weewx.units.conversionDict['unit_name'] = {'foobar': lambda x: x / 1}

    def test_configure_observation(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        name = random_string(10)
        value = random_string(10)
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['observations'] = {}
        config_dict['weewx']['observations'][name] = value

        config = configobj.ConfigObj(config_dict)

        MQTTSubscriber(config, mock_logger)

        self.assertEqual(len(weewx.units.obs_group_dict), 2)
        self.assertIn(name, weewx.units.obs_group_dict)
        self.assertEqual(value, weewx.units.obs_group_dict[name])

    def test_missing_group(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        unit = random_string(5)
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['units'] = {}
        config_dict['weewx']['units'][unit] = {}

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            MQTTSubscriber(config, mock_logger)

        self.assertEqual(error.exception.args[0], "%s is missing a group." % unit)

    def test_missing_unit_system(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        unit = random_string(5)
        group = random_string(10)
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['units'] = {}
        config_dict['weewx']['units'][unit] = {}
        config_dict['weewx']['units'][unit]['group'] = group

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            MQTTSubscriber(config, mock_logger)

        self.assertEqual(error.exception.args[0], "%s is missing an unit_system." % unit)

    def test_invalid_unit_system(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        unit = random_string(5)
        group = random_string(10)
        unit_system = random_string(5)
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['units'] = {}
        config_dict['weewx']['units'][unit] = {}
        config_dict['weewx']['units'][unit]['group'] = group
        config_dict['weewx']['units'][unit]['unit_system'] = unit_system

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            MQTTSubscriber(config, mock_logger)

        self.assertEqual(error.exception.args[0], "Invalid unit_system %s for %s." % (unit_system, unit))

    def test_configure_default_label(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'us'
        label = random_string(10)
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['units'] = {}
        config_dict['weewx']['units'][unit] = {}
        config_dict['weewx']['units'][unit]['group'] = group
        config_dict['weewx']['units'][unit]['unit_system'] = unit_system
        config_dict['weewx']['units'][unit]['label'] = label

        config = configobj.ConfigObj(config_dict)

        default_unit_label_dict = {}
        default_unit_label_dict[unit] = label

        MQTTSubscriber(config, mock_logger)

        self.assertDictEqual(weewx.units.default_unit_label_dict, default_unit_label_dict)

    def test_configure_default_format(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'us'
        format_value = random_string(10)
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['units'] = {}
        config_dict['weewx']['units'][unit] = {}
        config_dict['weewx']['units'][unit]['group'] = group
        config_dict['weewx']['units'][unit]['unit_system'] = unit_system
        config_dict['weewx']['units'][unit]['format'] = format_value

        config = configobj.ConfigObj(config_dict)

        default_unit_format_dict = {}
        default_unit_format_dict[unit] = format_value

        MQTTSubscriber(config, mock_logger)

        self.assertDictEqual(weewx.units.default_unit_format_dict, default_unit_format_dict)

    def test_configure_conversion(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'us'
        to_unit = random_string(5)
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['units'] = {}
        config_dict['weewx']['units'][unit] = {}
        config_dict['weewx']['units'][unit]['group'] = group
        config_dict['weewx']['units'][unit]['unit_system'] = unit_system
        config_dict['weewx']['units'][unit]['conversion'] = {}
        config_dict['weewx']['units'][unit]['conversion'][to_unit] = 'lambda x: x / 1'

        config = configobj.ConfigObj(config_dict)

        conversionDict = {}
        conversionDict['unit_name'] = {'foobar': lambda x: x / 1}
        conversionDict[unit] = {to_unit: lambda x: x / 1}

        MQTTSubscriber(config, mock_logger)

        self.assertEqual(len(weewx.units.conversionDict), len(conversionDict))
        for key in conversionDict:
            self.assertIn(key, weewx.units.conversionDict)
            self.assertEqual(len(weewx.units.conversionDict[key]), len(conversionDict[key]))
            for key2 in conversionDict[key]:
                self.assertIn(key2, weewx.units.conversionDict[key])
                self.assertIsInstance(weewx.units.conversionDict[key][key2], types.FunctionType)

    def test_unit_system_us(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'us'
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['units'] = {}
        config_dict['weewx']['units'][unit] = {}
        config_dict['weewx']['units'][unit]['group'] = group
        config_dict['weewx']['units'][unit]['unit_system'] = unit_system
        config_dict['weewx']['units'][unit]['conversion'] = {}

        config = configobj.ConfigObj(config_dict)

        units = weeutil.ListOfDicts({})
        units.extend({group: unit})

        MQTTSubscriber(config, mock_logger)

        self.assertEqual(len(weewx.units.USUnits), len(units))
        for key in units:
            self.assertIn(key, weewx.units.USUnits)
            self.assertEqual(units[key], weewx.units.USUnits[key])

    def test_unit_system_metric(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'metric'
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['units'] = {}
        config_dict['weewx']['units'][unit] = {}
        config_dict['weewx']['units'][unit]['group'] = group
        config_dict['weewx']['units'][unit]['unit_system'] = unit_system
        config_dict['weewx']['units'][unit]['conversion'] = {}

        config = configobj.ConfigObj(config_dict)

        units = weeutil.ListOfDicts({})
        units.extend({group: unit})

        MQTTSubscriber(config, mock_logger)

        self.assertEqual(len(weewx.units.MetricUnits), len(units))
        for key in units:
            self.assertIn(key, weewx.units.MetricUnits)
            self.assertEqual(units[key], weewx.units.MetricUnits[key])

    def test_unit_system_metricwx(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'metricwx'
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topics'][topic]['message'] = {}
        config_dict['topics'][topic]['message']['type'] = 'json'
        config_dict['weewx'] = {}
        config_dict['weewx']['units'] = {}
        config_dict['weewx']['units'][unit] = {}
        config_dict['weewx']['units'][unit]['group'] = group
        config_dict['weewx']['units'][unit]['unit_system'] = unit_system
        config_dict['weewx']['units'][unit]['conversion'] = {}

        config = configobj.ConfigObj(config_dict)

        units = weeutil.ListOfDicts({})
        units.extend({group: unit})

        MQTTSubscriber(config, mock_logger)

        self.assertEqual(len(weewx.units.MetricWXUnits), len(units))
        for key in units:
            self.assertIn(key, weewx.units.MetricWXUnits)
            self.assertEqual(units[key], weewx.units.MetricWXUnits[key])

class  Testtls_configuration(unittest.TestCase):
    @staticmethod
    def test_tls_configuration_good():
        ca_certs = random_string()
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': ca_certs
            },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=no-member
                    SUT = MQTTSubscriber(config, mock_logger)
                    SUT.client.tls_set.assert_called_once_with(ca_certs=ca_certs,
                                                               certfile=None,
                                                               keyfile=None,
                                                               cert_reqs=ssl.CERT_REQUIRED,
                                                               tls_version=ssl.PROTOCOL_TLSv1_2,
                                                               ciphers=None)

    def test_missing_PROTOCOL_TLS(self):
        tls_version = 'tls'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': random_string(),
                'tls_version': tls_version
            },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    try:
                        saved_version = ssl.PROTOCOL_TLS
                        del ssl.PROTOCOL_TLS
                    except AttributeError:
                        saved_version = None
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    if saved_version:
                        ssl.PROTOCOL_TLS = saved_version
                    self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_TLSv1(self):
        tls_version = 'tlsv1'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': random_string(),
                'tls_version': tls_version
            },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    try:
                        saved_version = ssl.PROTOCOL_TLSv1
                        del ssl.PROTOCOL_TLSv1
                    except AttributeError:
                        saved_version = None
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    if saved_version:
                        ssl.PROTOCOL_TLSv1 = saved_version
                    self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_TLSv1_1(self):
        tls_version = 'tlsv1_1'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': random_string(),
                'tls_version': tls_version
            },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    try:
                        saved_version = ssl.PROTOCOL_TLSv1_1
                        del ssl.PROTOCOL_TLSv1_1
                    except AttributeError:
                        saved_version = None
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    if saved_version:
                        ssl.PROTOCOL_TLSv1_1 = saved_version
                    self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_TLSv1_2(self):
        tls_version = 'tlsv1_2'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': random_string(),
                'tls_version': tls_version
            },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    try:
                        saved_version = ssl.PROTOCOL_TLSv1_2
                        del ssl.PROTOCOL_TLSv1_2
                    except AttributeError:
                        saved_version = None
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    if saved_version:
                        ssl.PROTOCOL_TLSv1_2 = saved_version
                    self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_SSLv2(self):
        tls_version = 'sslv2'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': random_string(),
                'tls_version': tls_version
            },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    try:
                        saved_version = ssl.PROTOCOL_SSLv2
                        del ssl.PROTOCOL_SSLv2
                    except AttributeError:
                        saved_version = None
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    if saved_version:
                        ssl.PROTOCOL_SSLv2 = saved_version
                    self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_SSLv23(self):
        tls_version = 'sslv23'
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': random_string(),
                'tls_version': tls_version
            },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    try:
                        saved_version = ssl.PROTOCOL_SSLv23
                        del ssl.PROTOCOL_SSLv23
                    except AttributeError:
                        saved_version = None
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    if saved_version:
                        ssl.PROTOCOL_SSLv23 = saved_version
                    self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_missing_PROTOCOL_SSLv3(self):
        tls_version = 'sslv3'
        config_dict = {
            'message_callback': {},

            'tls': {
                'ca_certs': random_string(),
                'tls_version': tls_version
            },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    try:
                        saved_version = ssl.PROTOCOL_SSLv3
                        del ssl.PROTOCOL_SSLv3
                    except AttributeError:
                        saved_version = None
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    if saved_version:
                        ssl.PROTOCOL_SSLv3 = saved_version
                    self.assertEqual(error.exception.args[0], "Invalid 'tls_version'., %s" % tls_version)

    def test_invalid_certs_required(self):
        certs_required = random_string()
        config_dict = {
            'message_callback': {},
            'tls': {
                'ca_certs': random_string(),
                'certs_required': certs_required
                },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    try:
                        saved_version = ssl.PROTOCOL_SSLv3
                        del ssl.PROTOCOL_SSLv3
                    except AttributeError:
                        saved_version = None
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    if saved_version:
                        ssl.PROTOCOL_SSLv3 = saved_version
                    self.assertEqual(error.exception.args[0], "Invalid 'certs_required'., %s" % certs_required)

    def test_missing_ca_certs(self):
        config_dict = {
            'message_callback': {},
            'tls': {
                random_string(): random_string()
            },
            'topics': {
                random_string(): {}
            }
        }
        config = configobj.ConfigObj(config_dict)
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    try:
                        saved_version = ssl.PROTOCOL_SSLv3
                        del ssl.PROTOCOL_SSLv3
                    except AttributeError:
                        saved_version = None
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    if saved_version:
                        ssl.PROTOCOL_SSLv3 = saved_version
                    self.assertEqual(error.exception.args[0], "'ca_certs' is required.")

class TestDeprecatedOptions(unittest.TestCase):
    def test_topic_is_deprecated(self):
        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config_dict['topic'] = random_string()
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)

                    self.assertEqual(error.exception.args[0], "'topic' is deprecated, use '[[topics]][[[topic name]]]'")

    def test_overlap_is_deprecated(self):
        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config_dict['overlap'] = random_string()
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    self.assertEqual(error.exception.args[0], "'overlap' is deprecated, use 'adjust_start_time'")

    def test_archive_field_cache_is_deprecated(self):
        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config_dict['archive_field_cache'] = random_string()
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    self.assertEqual(error.exception.args[0],
                                     "'archive_field_cache' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]'")

    def test_full_topic_fieldname_is_deprecated(self):
        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config_dict['message_callback']['full_topic_fieldname'] = random_string()
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    self.assertEqual(error.exception.args[0],
                                     "'full_topic_fieldname' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]'")

    def test_contains_total_is_deprecated(self):
        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config_dict['message_callback']['contains_total'] = random_string()
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    self.assertEqual(error.exception.args[0],
                                     "'contains_total' is deprecated use '[[topics]][[[topic name]]][[[[field name]]]]' contains_total setting.")

    def test_label_map_is_deprecated(self):
        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config_dict['message_callback']['label_map'] = {}
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    self.assertEqual(error.exception.args[0],
                                     "'label_map' is deprecated use '[[topics]][[[topic name]]][[[[field name]]]]' name setting.")

    def test_fields_is_deprecated(self):
        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config_dict['message_callback']['fields'] = {}
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with self.assertRaises(ValueError) as error:
                        MQTTSubscriber(config, mock_logger)
                    self.assertEqual(error.exception.args[0], "'fields' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]'")

    def test_use_topic_as_fieldname(self):
        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config_dict['topics']['use_topic_as_fieldname'] = 'true'
        config = configobj.ConfigObj(config_dict)

        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    SUT = MQTTSubscriber(config, mock_logger)

                    self.assertEqual(SUT.logger.info.call_count, 12)
                    mock_logger.info.assert_any_call("'use_topic_as_fieldname' option is no longer needed and can be removed.")

class TestStart(unittest.TestCase):
    def set_connection_success(self, *args, **kwargs): # match signature pylint: disable=unused-argument
        self.SUT.userdata['connect'] = True

    def test_bad_connection_return_code(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)
        connect_rc = random.randint(1, 10)
        flags = random.randint(0, 255)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with mock.patch('user.MQTTSubscribe.time'):
                        # pylint: disable=no-member
                        with self.assertRaises(weewx.WeeWxIOError) as error:
                            SUT = MQTTSubscriber(config, mock_logger)

                            SUT.userdata = {}
                            SUT.userdata['connect'] = True
                            SUT.userdata['connect_rc'] = connect_rc
                            SUT.userdata['connect_flags'] = flags

                            SUT.start()

                        SUT.client.loop_start.assert_called_once()
                        self.assertEqual(error.exception.args[0], "Unable to connect. Return code is %i flags are %s." % (connect_rc, flags))

    @staticmethod
    def test_immediate_connection():
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with mock.patch('user.MQTTSubscribe.time') as mock_time:
                        # pylint: disable=no-member
                        SUT = MQTTSubscriber(config, mock_logger)

                        SUT.userdata = {}
                        SUT.userdata['connect'] = True
                        SUT.userdata['connect_rc'] = 0

                        SUT.start()
                        SUT.client.loop_start.assert_called_once()
                        mock_time.sleep.assert_not_called()

    def test_wait_for_connection(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    with mock.patch('user.MQTTSubscribe.time') as mock_time:
                        # pylint: disable=no-member
                        SUT = MQTTSubscriber(config, mock_logger)

                        self.SUT = SUT # pylint: disable=attribute-defined-outside-init
                        SUT.userdata = {}
                        SUT.userdata['connect'] = False
                        SUT.userdata['connect_rc'] = 0
                        mock_time.sleep.side_effect = mock.Mock(side_effect=self.set_connection_success) # Hack, use this to escape the loop

                        SUT.start()
                        SUT.client.loop_start.assert_called_once()
                        mock_time.sleep.assert_called_once()

class Test_disconnect(unittest.TestCase):
    @staticmethod
    def test_disconnect():
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=no-member
                    SUT = MQTTSubscriber(config, mock_logger)

                    SUT.disconnect()

                    SUT.client.disconnect.assert_called_once()

class TestCallbacks(unittest.TestCase):
    @staticmethod
    def test_on_disconnect():
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        rc = random.randint(1, 10)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=no-member, protected-access
                    SUT = MQTTSubscriber(config, mock_logger)

                    SUT._on_disconnect(None, None, rc)

                    SUT.logger.info.assert_called_with("Disconnected with result code %i" % rc)

    @staticmethod
    def test_on_subscribe():
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        mid = random.randint(1, 10)
        granted_qos = [random.randint(1, 10)]

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=no-member, protected-access
                    SUT = MQTTSubscriber(config, mock_logger)

                    SUT._on_subscribe(None, None, mid, granted_qos)

                    SUT.logger.info.assert_called_with("Subscribed to mid: %i is size %i has a QOS of %i" \
                                                        %(mid, len(granted_qos), granted_qos[0]))

    @staticmethod
    def test_on_log():
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}
        config_dict['message_callback'] = {}
        config_dict['topics'] = {}
        config = configobj.ConfigObj(config_dict)

        level = 1
        msg = random_string()

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client):
            with mock.patch('user.MQTTSubscribe.MessageCallbackProvider'):
                with mock.patch('user.MQTTSubscribe.TopicManager'):
                    # pylint: disable=no-member, protected-access
                    SUT = MQTTSubscriber(config, mock_logger)

                    SUT._on_log(None, None, level, msg)

                    SUT.logger.info.assert_called_with("MQTTSubscribe MQTT: %s" % msg)

class Teston_connect(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = test_weewx_stubs.UNITS_CONSTANTS[unit_system_name]
    config_dict = {
        'console': False,
        'keyword_delimiter': None,
        'keyword_separator': None,
        'host': 'host',
        'keepalive': random.randint(1, 10),
        'port': random.randint(1, 10),
        'username': random_string(),
        'password': random_string(),
        'archive_topic': None
    }

    def test_multiple_topics(self):
        topic1 = random_string()
        topic2 = random_string()
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topics'] = {}
        config_dict['topics'][topic1] = {}
        config_dict['topics'][topic1]['subscribe'] = True
        config_dict['topics'][topic2] = {}
        config_dict['topics'][topic2]['subscribe'] = True
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

                    SUT = MQTTSubscriber(config, mock_logger)

                    rc = random.randint(1, 10)
                    userdata = {}
                    userdata['connect'] = False
                    SUT._on_connect(mock_client, userdata, None, rc,)   # pylint: disable=protected-access

                    self.assertEqual(mock_client.subscribe.call_count, 2)
                    mock_client.subscribe.assert_any_call(topic1, qos)
                    mock_client.subscribe.assert_any_call(topic2, qos)

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestInitialization('test_connect_exception'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
