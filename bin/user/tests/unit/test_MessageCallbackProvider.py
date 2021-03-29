#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access

from __future__ import with_statement

import unittest
import mock

import configobj
import copy
import json
import random
import string
import sys
import time

import test_weewx_stubs # used to set up stubs - pylint: disable=unused-import

import user.MQTTSubscribe
from user.MQTTSubscribe import TopicManager, Logger

# Stole from six module. Added to eliminate dependency on six when running under WeeWX 3.x
PY2 = sys.version_info[0] == 2

def random_string(length=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)]) # pylint: disable=unused-variable

class Msg(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain

class TestInitialization(unittest.TestCase):
    @staticmethod
    def test_message_and_message_callback_set():
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = {}
        mock_manager.subscribed_topics[topic] = {}
        mock_manager.subscribed_topics[topic]['queue'] = {}
        mock_manager.subscribed_topics[topic]['queue']['type'] = queue_type
        mock_manager.subscribed_topics[topic][message_config_name] = {}
        mock_manager.subscribed_topics[topic][message_config_name]['type'] = 'json'

        config_dict = {}
        config_dict['type'] = 'barbar'
        config = configobj.ConfigObj(config_dict)

        user.MQTTSubscribe.MessageCallbackProvider(config, mock_logger, mock_manager)

        mock_logger.info.assert_called_once_with( \
            "Message configuration found under [[MessageCallback]] and [[Topic]]. Ignoring [[MessageCallbwck]].")

    def test_message_and_message_callback_not_set(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = {}
        mock_manager.subscribed_topics[topic] = {}
        mock_manager.subscribed_topics[topic]['queue'] = {}
        mock_manager.subscribed_topics[topic]['queue']['type'] = queue_type
        mock_manager.subscribed_topics[topic][message_config_name] = {}

        with self.assertRaises(ValueError) as error:
            user.MQTTSubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(error.exception.args[0], "%s topic is missing '[[[[Message]]]]' section" % topic)

    def test_message_callback_configuration_defaults_not_set(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        flatten_delimiter = random_string(5)
        keyword_delimiter = random_string(5)
        keyword_separator = random_string(5)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = {}
        mock_manager.subscribed_topics[topic] = {}
        mock_manager.subscribed_topics[topic]['queue'] = {}
        mock_manager.subscribed_topics[topic]['queue']['type'] = queue_type
        mock_manager.subscribed_topics[topic][message_config_name] = {}

        config_dict = {}
        config_dict['type'] = 'json'
        config_dict['flatten_delimiter'] = flatten_delimiter
        config_dict['keyword_delimiter'] = keyword_delimiter
        config_dict['keyword_separator'] = keyword_separator
        config = configobj.ConfigObj(config_dict)

        user.MQTTSubscribe.MessageCallbackProvider(config, mock_logger, mock_manager)

        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['flatten_delimiter'], flatten_delimiter)
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_delimiter'], keyword_delimiter)
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_separator'], keyword_separator)

    def test_message_configuration_defaults_set(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        flatten_delimiter = random_string(5)
        keyword_delimiter = random_string(5)
        keyword_separator = random_string(5)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = {}
        mock_manager.subscribed_topics[topic] = {}
        mock_manager.subscribed_topics[topic]['queue'] = {}
        mock_manager.subscribed_topics[topic]['queue']['type'] = queue_type
        mock_manager.subscribed_topics[topic][message_config_name] = {}
        mock_manager.subscribed_topics[topic][message_config_name]['type'] = 'json'
        mock_manager.subscribed_topics[topic][message_config_name]['flatten_delimiter'] = flatten_delimiter
        mock_manager.subscribed_topics[topic][message_config_name]['keyword_delimiter'] = keyword_delimiter
        mock_manager.subscribed_topics[topic][message_config_name]['keyword_separator'] = keyword_separator

        user.MQTTSubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['flatten_delimiter'], flatten_delimiter)
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_delimiter'], keyword_delimiter)
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_separator'], keyword_separator)

    def test_message_configuration_defaults_not_set(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = {}
        mock_manager.subscribed_topics[topic] = {}
        mock_manager.subscribed_topics[topic]['queue'] = {}
        mock_manager.subscribed_topics[topic]['queue']['type'] = queue_type
        mock_manager.subscribed_topics[topic][message_config_name] = {}
        mock_manager.subscribed_topics[topic][message_config_name]['type'] = 'json'

        user.MQTTSubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['flatten_delimiter'], '_')
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_delimiter'], ',')
        self.assertEqual(mock_manager.subscribed_topics[topic][message_config_name]['keyword_separator'], '=')

    def test_message_configuration_invalid_type(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        message_type = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = {}
        mock_manager.subscribed_topics[topic] = {}
        mock_manager.subscribed_topics[topic]['queue'] = {}
        mock_manager.subscribed_topics[topic]['queue']['type'] = queue_type
        mock_manager.subscribed_topics[topic][message_config_name] = {}
        mock_manager.subscribed_topics[topic][message_config_name]['type'] = message_type

        with self.assertRaises(ValueError) as error:
            user.MQTTSubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(error.exception.args[0], "Invalid type configured: %s" % message_type)

    def test_message_configuration_missing_type(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        topic = random_string(10)
        message_config_name = random_string()
        queue_type = random_string(10)
        config_option = random_string(10)
        config_value = random_string(10)
        mock_manager.message_config_name = message_config_name
        mock_manager.subscribed_topics = {}
        mock_manager.subscribed_topics[topic] = {}
        mock_manager.subscribed_topics[topic]['queue'] = {}
        mock_manager.subscribed_topics[topic]['queue']['type'] = queue_type
        mock_manager.subscribed_topics[topic][message_config_name] = {}
        mock_manager.subscribed_topics[topic][message_config_name][config_option] = config_value

        with self.assertRaises(ValueError) as error:
            user.MQTTSubscribe.MessageCallbackProvider(None, mock_logger, mock_manager)

        self.assertEqual(error.exception.args[0], "%s topic is missing '[[[[Message]]]] type=' section" % topic)

# missing message section? todo

class TestConversionType(unittest.TestCase):
    def test_bool_conversion(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        conversion_type = 'bool'
        value = 'false'

        fields = {}
        field = {}
        field['conversion_type'] = conversion_type
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        new_value = SUT._convert_value(fields, input_name, value)

        self.assertIsInstance(new_value, bool)
        self.assertFalse(new_value)

    def test_float_conversion(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        conversion_type = 'float'
        value_float = round(random.uniform(10, 100), 2)
        value = str(value_float)

        fields = {}
        field = {}
        field['conversion_type'] = conversion_type
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        new_value = SUT._convert_value(fields, input_name, value)

        self.assertIsInstance(new_value, float)
        self.assertEqual(new_value, value_float)

    def test_int_conversion(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        conversion_type = 'int'
        value_int = random.randint(1, 10)
        value = str(value_int)

        fields = {}
        field = {}
        field['conversion_type'] = conversion_type
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        new_value = SUT._convert_value(fields, input_name, value)

        self.assertIsInstance(new_value, int)
        self.assertEqual(new_value, value_int)

    def test_default_conversion(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        value_float = round(random.uniform(10, 100), 2)
        value = str(value_float)

        fields = {}
        field = {}
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        new_value = SUT._convert_value(fields, input_name, value)

        self.assertIsInstance(new_value, float)
        self.assertEqual(new_value, value_float)

    def test_no_conversion(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        conversion_type = 'None'
        value = str(round(random.uniform(10, 100), 2))

        fields = {}
        field = {}
        field['conversion_type'] = conversion_type
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        new_value = SUT._convert_value(fields, input_name, value)

        self.assertIsInstance(new_value, str)
        self.assertEqual(new_value, value)

class TestKeywordload(unittest.TestCase):
    topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

    payload_dict = {
        'inTemp': round(random.uniform(10, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'keyword'

    def test_payload_empty(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = ''
        payload = payload.encode('UTF-8')

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_payload_bad_data(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = 'field=value'
        if not PY2:
            payload = payload.encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_payload_missing_delimiter(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = 'field1=1 field2=2'
        if not PY2:
            payload = payload.encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_payload_missing_separator(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = ' field:1'
        payload = payload.encode('UTF-8')

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_payload_missing_dateTime(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" % (payload_str, delim, key, payload_dict[key])
            delim = ","

        payload_str = payload_str.encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_missing_units(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" % (payload_str, delim, key, payload_dict[key])
            delim = ","

        payload_str = payload_str.encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_good(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" % (payload_str, delim, key, payload_dict[key])
            delim = ","

        payload_str = payload_str.encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_ignore_default_true(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'
        field_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}
        fields['ignore'] = True

        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" % (payload_str, delim, key, payload_dict[key])
            delim = ","

        payload_str = payload_str.encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertFalse(mock_manager.append_data.called)

    def test_ignore_default_true_ignore_field_false(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'
        field_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}
        fields['ignore'] = True

        field = {}
        field['ignore'] = False
        fields['dateTime'] = field

        field = {}
        field['ignore'] = False
        fields['usUnits'] = field

        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = {}
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" % (payload_str, delim, key, payload_dict[key])
            delim = ","

        payload_str = payload_str.encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_ignore_field_true(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {'keyword_delimiter': ',', 'keyword_separator': '='}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'

        fields = {}

        field = {}
        field['ignore'] = True
        fields['inTemp'] = field

        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = {}
        payload_dict['outTemp'] = self.payload_dict['outTemp']
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" % (payload_str, delim, key, payload_dict[key])
            delim = ","

        payload_str = payload_str.encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

class TestJsonPayload(unittest.TestCase):
    topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

    payload_dict = {
        'inTemp': round(random.uniform(10, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'json'

    def test_invalid_json(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        msg = Msg(self.topic,
                  ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),  # pylint: disable=unused-variable
                  0,
                  0)

        SUT._on_message_json(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        msg = Msg(self.topic, '', 0, 0)

        SUT._on_message_json(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_missing_dateTime(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_filters.return_value = {}
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_missing_units(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_filters.return_value = {}
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_good(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_value.return_value = True
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_filters.return_value = {}
        mock_manager.get_filters.return_value = {}
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)
        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_msg_id_set(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)
        msg_id_field = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        mock_manager.get_msg_id_field.return_value = msg_id_field
        mock_manager.get_fields.return_value = {}
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_filters.return_value = {}
        mock_manager.get_filters.return_value = {}
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}


        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)
        msg_id = random.randint(1, 10)
        payload_dict[msg_id_field] = msg_id

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        final_dict = {}
        for key in payload_dict:
            #if key == msg_id_field:
            #    continue
            final_dict[key + '_' + str(msg_id)] = payload_dict[key]

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, final_dict)
        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_ignore_msg_id_field_set(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)
        msg_id_field = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        mock_manager.get_msg_id_field.return_value = msg_id_field
        mock_manager.get_fields.return_value = {}
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_filters.return_value = {}
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)
        msg_id = random.randint(1, 10)
        payload_dict[msg_id_field] = msg_id

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        ignore_msg_id_field_fields = [msg_id_field]
        for key in payload_dict:
            if key == msg_id_field:
                continue
            ignore_msg_id_field_fields.append(key)

        mock_manager.get_ignore_msg_id_field.return_value = ignore_msg_id_field_fields

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)
        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_payload_nested(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_filters.return_value = {}
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

        payload_dict = {
            'nested01': {
                'inTemp': round(random.uniform(1, 100), 2),
                'outTemp': round(random.uniform(1, 100), 2)
            }
        }

        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        flattened_payload_dict = {
            'nested01_inTemp': payload_dict['nested01']['inTemp'],
            'nested01_outTemp': payload_dict['nested01']['outTemp']
        }
        flattened_payload_dict['dateTime'] = payload_dict['dateTime']
        flattened_payload_dict['usUnits'] = payload_dict['usUnits']

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, flattened_payload_dict)

    def test_payload_nested_rename(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {'nested01_inTemp': {'name': 'inTemp'}}
        mock_manager.get_filters.return_value = {}
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = copy.deepcopy(self.message_handler_config_dict)
        message_handler_config_dict['fields'] = {}
        message_handler_config_dict['fields']['nested01_inTemp'] = {}
        message_handler_config_dict['fields']['nested01_inTemp']['name'] = 'inTemp'

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), stub_logger, mock_manager)

        payload_dict = {
            'nested01': {
                'inTemp': round(random.uniform(1, 100), 2),
                'outTemp': round(random.uniform(1, 100), 2)
            }
        }

        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        flattened_payload_dict = {
            'inTemp': payload_dict['nested01']['inTemp'],
            'nested01_outTemp': payload_dict['nested01']['outTemp']
        }
        flattened_payload_dict['dateTime'] = payload_dict['dateTime']
        flattened_payload_dict['usUnits'] = payload_dict['usUnits']

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, flattened_payload_dict)

    def test_ignore_default_true(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'

        fields = {}
        fields['ignore'] = True

        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        self.assertFalse(mock_manager.append_data.called)

    def test_ignore_default_true_ignore_field_false(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_filters.return_value = {}
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'

        fields = {}
        fields['ignore'] = True

        field = {}
        field['ignore'] = False
        fields['dateTime'] = field

        field = {}
        field['ignore'] = False
        fields['usUnits'] = field

        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = {}
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)
        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_ignore_field_true(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_filters.return_value = {}
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'
        field_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}

        field = {}
        field['ignore'] = True
        fields['inTemp'] = field

        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = {}
        payload_dict['outTemp'] = self.payload_dict['outTemp']
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)
        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_filter_message(self):
        lookup_key = 'outTemp'
        filters = {lookup_key: [self.payload_dict['outTemp']]}
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_filters.return_value = filters
        mock_manager.get_message_dict.return_value = {'flatten_delimiter': '_'}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'
        field_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}

        field = {}
        field['ignore'] = True
        fields['inTemp'] = field

        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = {}
        payload_dict['outTemp'] = self.payload_dict['outTemp']
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_not_called()
        SUT.logger.info.assert_called_with("MessageCallbackProvider on_message_json filtered out %s : %s with %s=%s"
                                           % (msg.topic, msg.payload, lookup_key, filters[lookup_key]))

class TestIndividualPayloadSingleTopicFieldName(unittest.TestCase):
    topic_end = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    topic = topic + '/' + topic_end
    single_topic = topic_end
    multi_topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    multi_topic = multi_topic + '/'
    multi_topic = multi_topic + ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    multi_topic = multi_topic + '/' + topic_end

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'individual'

    def test_bad_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = ''
        if not PY2:
            payload = payload.encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = ''
        if not PY2:
            payload = payload.encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_None_payload(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_topic_tail_is_fieldname.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = None
        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_individual(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: None}, msg.topic)

    def test_unicode_topic(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_topic_tail_is_fieldname.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        if PY2:
            topic = unicode(self.topic)  # (never called under python 3) pylint: disable=undefined-variable
        else:
            topic = self.topic

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: payload}, msg.topic)

        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_single_topic(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.single_topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: payload}, self.topic_end)

    def test_multiple_topics(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_topic_tail_is_fieldname.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.multi_topic,
                  payload_str,
                  0,
                  0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: payload}, msg.topic)

    def test_two_topics(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_topic_tail_is_fieldname.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.topic,
                  payload_str,
                  0,
                  0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: payload}, msg.topic)

    def test_ignore_default_true(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        fields = {}
        fields['ignore'] = True

        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.single_topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertFalse(mock_manager.append_data.called)

    def test_ignore_default_true_ignore_field_false(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        fields = {}
        fields['ignore'] = True

        field = {}
        field['ignore'] = False
        fields[self.single_topic] = field

        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.single_topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: payload}, self.topic_end)

    def test_ignore_field_true(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'
        field_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}

        field = {}
        field['ignore'] = True
        fields[self.single_topic] = field
        message_handler_config_dict['fields'] = fields

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.single_topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertFalse(mock_manager.append_data.called)

class TestIndividualPayloadFullTopicFieldName(unittest.TestCase):
    topic_end = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    topic = topic + '/' + topic_end
    single_topic = topic_end
    multi_topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    multi_topic = multi_topic + '/'
    multi_topic = multi_topic + ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    multi_topic = multi_topic + '/' + topic_end

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'individual'

    def test_bad_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        if not PY2:
            payload = payload.encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = ''
        if not PY2:
            payload = payload.encode("utf-8")
        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_None_payload(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_topic_tail_is_fieldname.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        message_handler_config_dict = dict(self.message_handler_config_dict)

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        msg = Msg(self.topic, None, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: None}, msg.topic)

    def test_single_topic(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        mock_manager.get_msg_id_field.return_value = None
        mock_manager.get_ignore_msg_id_field.return_value = []
        mock_manager.get_ignore_value.return_value = False
        mock_manager.get_fields.return_value = {}
        mock_manager.get_message_dict.return_value = {}
        mock_manager.subscribed_topics = {}

        SUT = user.MQTTSubscribe.MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.single_topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: payload}, self.topic_end)

if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestInitialization('test_one'))
    # test_suite.addTest(TestJsonPayload('test_ignore_msg_id_field_set'))
    unittest.TextTestRunner().run(test_suite)

   # unittest.main(exit=False)
