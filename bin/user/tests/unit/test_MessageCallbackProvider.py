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

from user.MQTTSubscribe import MessageCallbackProvider, TopicManager, Logger

# Stole from six module. Added to eliminate dependency on six when running under WeeWX 3.x
PY2 = sys.version_info[0] == 2

class Msg(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain

class TestFieldsConfiguration(unittest.TestCase):
    def test_field_in_label_map(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        output_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        label_map = {}
        label_map[input_name] = output_name
        message_handler_config_dict['label_map'] = label_map

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertIn(input_name, SUT.fields)
        self.assertIn('name', SUT.fields[input_name])
        self.assertEqual(SUT.fields[input_name]['name'], output_name)

    def test_field_in_label_map_and_fields_with_name(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        output_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        label_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        label_map = {}
        label_map[input_name] = label_name
        message_handler_config_dict['label_map'] = label_map

        fields = {}
        field = {}
        field['name'] = output_name
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertIn(input_name, SUT.fields)
        self.assertIn('name', SUT.fields[input_name])
        self.assertEqual(SUT.fields[input_name]['name'], output_name)

    def test_field_in_label_map_and_fields_without_name(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        #output_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        label_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        label_map = {}
        label_map[input_name] = label_name
        message_handler_config_dict['label_map'] = label_map

        fields = {}
        field = {}
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertIn(input_name, SUT.fields)
        self.assertIn('name', SUT.fields[input_name])
        self.assertEqual(SUT.fields[input_name]['name'], label_name)


    def test_field_in_label_map_and_fields_and_contains_total(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        output_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        label_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        label_map = {}
        label_map[input_name] = label_name
        message_handler_config_dict['label_map'] = label_map

        fields = {}
        field = {}
        field['name'] = output_name
        field['contains_total'] = False
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        contains_total = [input_name]
        message_handler_config_dict['contains_total'] = contains_total

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertIn(input_name, SUT.fields)
        self.assertIn('name', SUT.fields[input_name])
        self.assertEqual(SUT.fields[input_name]['name'], output_name)
        self.assertFalse(SUT.fields[input_name]['contains_total'])

    def test_field_in_label_map_and_contains_total(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        label_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        label_map = {}
        label_map[input_name] = label_name
        message_handler_config_dict['label_map'] = label_map

        contains_total = [input_name]
        message_handler_config_dict['contains_total'] = contains_total

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertIn(input_name, SUT.fields)
        self.assertIn('name', SUT.fields[input_name])
        self.assertEqual(SUT.fields[input_name]['name'], label_name)
        self.assertTrue(SUT.fields[input_name]['contains_total'])

    def test_field_in_fields(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        output_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}
        field = {}
        field['name'] = output_name
        field['contains_total'] = False
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertIn(input_name, SUT.fields)
        self.assertIn('name', SUT.fields[input_name])
        self.assertEqual(SUT.fields[input_name]['name'], output_name)
        self.assertFalse(SUT.fields[input_name]['contains_total'])

    def test_field_in_fields_and_contains_total(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        output_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}
        field = {}
        field['name'] = output_name
        field['contains_total'] = False
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        contains_total = [input_name]
        message_handler_config_dict['contains_total'] = contains_total

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertIn(input_name, SUT.fields)
        self.assertIn('name', SUT.fields[input_name])
        self.assertEqual(SUT.fields[input_name]['name'], output_name)
        self.assertFalse(SUT.fields[input_name]['contains_total'])

    def test_field_in_contains_total(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        contains_total = [input_name]
        message_handler_config_dict['contains_total'] = contains_total

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertNotIn('name', SUT.fields[input_name])
        self.assertTrue(SUT.fields[input_name]['contains_total'])

    def test_contains_total_is_bool(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}
        field = {}
        field['contains_total'] = 'false'
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertIn(input_name, SUT.fields)
        self.assertIn('contains_total', SUT.fields[input_name])
        self.assertIsInstance(SUT.fields[input_name]['contains_total'], bool)

    def test_type_is_lowercase(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        conversion_type = 'INT'

        fields = {}
        field = {}
        field['conversion_type'] = conversion_type
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertIn(input_name, SUT.fields)
        self.assertIn('conversion_type', SUT.fields[input_name])
        self.assertEqual(SUT.fields[input_name]['conversion_type'], conversion_type.lower())

class TestGetDefaultCallBacks(unittest.TestCase):
    def test_get_unknown_payload_type(self):
        message_handler_config_dict = {}
        payload_type = 'foobar'
        message_handler_config_dict['type'] = payload_type

        with self.assertRaises(ValueError) as context:
            MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        self.assertEqual(str(context.exception), "Invalid type configured: %s" % payload_type)

    def test_get_individual_payload_type(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        callback = SUT.get_callback()
        self.assertEqual(callback, SUT._on_message_individual)

    def test_get_json_payload_type(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        callback = SUT.get_callback()
        self.assertEqual(callback, SUT._on_message_json)

    def test_get_keyword_payload_type(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        callback = SUT.get_callback()
        self.assertEqual(callback, SUT._on_message_keyword)

class TestConversionType(unittest.TestCase):
    def test_bool_conversion(self):
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

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        new_value = SUT._convert_value(input_name, value)

        self.assertIsInstance(new_value, bool)
        self.assertFalse(new_value)

    def test_float_conversion(self):
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

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        new_value = SUT._convert_value(input_name, value)

        self.assertIsInstance(new_value, float)
        self.assertEqual(new_value, value_float)

    def test_int_conversion(self):
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

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        new_value = SUT._convert_value(input_name, value)

        self.assertIsInstance(new_value, int)
        self.assertEqual(new_value, value_int)

    def test_default_conversion(self):
        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        input_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
        value_float = round(random.uniform(10, 100), 2)
        value = str(value_float)

        fields = {}
        field = {}
        fields[input_name] = field
        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        new_value = SUT._convert_value(input_name, value)

        self.assertIsInstance(new_value, float)
        self.assertEqual(new_value, value_float)

    def test_no_conversion(self):
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

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), None, None)

        new_value = SUT._convert_value(input_name, value)

        self.assertIsInstance(new_value, str)
        self.assertEqual(new_value, value)

class TestKeywordload(unittest.TestCase):
    topic = 'foo/bar'

    payload_dict = {
        'inTemp': round(random.uniform(10, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'keyword'

    def test_payload_empty(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        payload = ''
        payload = payload.encode('UTF-8')

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_payload_bad_data(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        msg = Msg(self.topic, 'field=value', 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_payload_missing_delimiter(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        msg = Msg(self.topic, 'field1=1 field2=2', 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_payload_missing_separator(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        payload = ' field:1'
        payload = payload.encode('UTF-8')

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 3)

    def test_payload_missing_dateTime(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

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

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

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

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

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

    def test_payload_no_previous_value(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'
        message_handler_config_dict['contains_total'] = 'inTemp'

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        result_dict = copy.deepcopy(payload_dict)
        result_dict['inTemp'] = None

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" % (payload_str, delim, key, payload_dict[key])

            delim = ","

        payload_str = payload_str.encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, result_dict)
        self.assertEqual(SUT.previous_values['inTemp'], payload_dict['inTemp'])

    def test_payload_larger_previous_value(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'
        message_handler_config_dict['contains_total'] = 'inTemp'

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)
        prev_temp = round(random.uniform(101, 200), 2)
        SUT.previous_values['inTemp'] = prev_temp

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        result_dict = copy.deepcopy(payload_dict)
        result_dict['inTemp'] = None

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" % (payload_str, delim, key, payload_dict[key])

            delim = ","

        payload_str = payload_str.encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, result_dict)
        self.assertEqual(SUT.previous_values['inTemp'], payload_dict['inTemp'])

    def test_payload_good_previous_value(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'
        message_handler_config_dict['contains_total'] = 'inTemp'
        prev_temp = round(random.uniform(1, 9), 2)

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)
        SUT.previous_values['inTemp'] = prev_temp

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        result_dict = copy.deepcopy(payload_dict)
        result_dict['inTemp'] = payload_dict['inTemp'] - prev_temp

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" % (payload_str, delim, key, payload_dict[key])
            delim = ","

        payload_str = payload_str.encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, result_dict)
        self.assertEqual(SUT.previous_values['inTemp'], payload_dict['inTemp'])

    def test_ignore_default_true(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'
        field_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}
        fields['ignore'] = True

        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

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

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

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

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'keyword'

        fields = {}

        field = {}
        field['ignore'] = True
        fields['inTemp'] = field

        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

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
    topic = 'foo/bar'

    payload_dict = {
        'inTemp': round(random.uniform(10, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'json'

    def test_invalid_json(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        msg = Msg(self.topic,
                  ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),  # pylint: disable=unused-variable
                  0,
                  0)

        SUT._on_message_json(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        msg = Msg(self.topic, '', 0, 0)

        SUT._on_message_json(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_missing_dateTime(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

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

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

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

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

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

    def test_payload_no_previous_value(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)

        message_handler_config_dict = copy.deepcopy(self.message_handler_config_dict)
        message_handler_config_dict['contains_total'] = 'inTemp'

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), stub_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        result_dict = copy.deepcopy(payload_dict)
        result_dict['inTemp'] = None

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, result_dict)
        self.assertEqual(SUT.previous_values['inTemp'], payload_dict['inTemp'])
        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_payload_larger_previous_value(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)

        message_handler_config_dict = copy.deepcopy(self.message_handler_config_dict)
        message_handler_config_dict['contains_total'] = 'inTemp'
        prev_temp = round(random.uniform(101, 200), 2)

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), stub_logger, mock_manager)
        SUT.previous_values['inTemp'] = prev_temp

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        result_dict = copy.deepcopy(payload_dict)
        result_dict['inTemp'] = None

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, result_dict)
        self.assertEqual(SUT.previous_values['inTemp'], payload_dict['inTemp'])
        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_payload_good_previous_value(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)

        message_handler_config_dict = copy.deepcopy(self.message_handler_config_dict)
        message_handler_config_dict['contains_total'] = 'inTemp'
        prev_temp = round(random.uniform(1, 9), 2)

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), stub_logger, mock_manager)
        SUT.previous_values['inTemp'] = prev_temp

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        result_dict = copy.deepcopy(payload_dict)
        result_dict['inTemp'] = payload_dict['inTemp'] - prev_temp

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, result_dict)
        self.assertEqual(SUT.previous_values['inTemp'], payload_dict['inTemp'])
        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_payload_nested(self):
        mock_manager = mock.Mock(spec=TopicManager)
        stub_logger = test_weewx_stubs.Logger(console=True)

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), stub_logger, mock_manager)

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

        message_handler_config_dict = copy.deepcopy(self.message_handler_config_dict)
        message_handler_config_dict['fields'] = {}
        message_handler_config_dict['fields']['nested01_inTemp'] = {}
        message_handler_config_dict['fields']['nested01_inTemp']['name'] = 'inTemp'

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), stub_logger, mock_manager)

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

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'

        fields = {}
        fields['ignore'] = True

        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

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

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

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

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'json'
        field_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}

        field = {}
        field['ignore'] = True
        fields['inTemp'] = field

        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

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

class TestIndividualPayloadSingleTopicFieldName(unittest.TestCase):
    topic_end = 'bar'
    topic = 'foo/' + topic_end
    single_topic = topic_end
    multi_topic = 'foo1/foo2/' + topic_end

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'individual'

    def test_bad_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        msg = Msg(self.topic,
                  ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),  # pylint: disable=unused-variable
                  0,
                  0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        msg = Msg(self.topic, '', 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_None_payload(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = None
        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_individual(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: None}, self.topic_end)

    def test_unicode_topic(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)
        if PY2:
            topic = unicode(self.topic)  # (never called under python 3) pylint: disable=undefined-variable
        else:
            topic = self.topic

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: payload}, self.topic_end)

        call_args_list = mock_manager.append_data.call_args_list
        second_arg = call_args_list[0].args[1]
        for key in second_arg:
            self.assertIsInstance(key, str)

    def test_payload_no_previous_value(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        topic = 'inTemp'
        message_handler_config_dict = copy.deepcopy(self.message_handler_config_dict)
        message_handler_config_dict['contains_total'] = topic

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: None}, msg.topic)
        self.assertEqual(SUT.previous_values['inTemp'], payload)

    def test_payload_larger_previous_value(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        topic = 'inTemp'
        message_handler_config_dict = copy.deepcopy(self.message_handler_config_dict)
        message_handler_config_dict['contains_total'] = topic
        prev_temp = round(random.uniform(101, 200), 2)

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)
        SUT.previous_values['inTemp'] = prev_temp

        payload = round(random.uniform(1, 100), 2)
        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: None}, msg.topic)
        self.assertEqual(SUT.previous_values['inTemp'], payload)

    def test_payload_good_previous_value(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        topic = 'inTemp'
        message_handler_config_dict = copy.deepcopy(self.message_handler_config_dict)
        message_handler_config_dict['contains_total'] = topic
        prev_temp = round(random.uniform(1, 9), 2)

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)
        SUT.previous_values['inTemp'] = prev_temp

        payload = round(random.uniform(10, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: payload - prev_temp}, msg.topic)
        self.assertEqual(SUT.previous_values['inTemp'], payload)

    def test_single_topic(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

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

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

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
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: payload}, self.topic_end)

    def test_two_topics(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

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
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic_end: payload}, self.topic_end)

    def test_ignore_default_true(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        fields = {}
        fields['ignore'] = True

        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

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

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'

        fields = {}
        fields['ignore'] = True

        field = {}
        field['ignore'] = False
        fields[self.single_topic] = field

        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

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

        message_handler_config_dict = {}
        message_handler_config_dict['type'] = 'individual'
        field_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

        fields = {}

        field = {}
        field['ignore'] = True
        fields[self.single_topic] = field
        message_handler_config_dict['fields'] = fields

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.single_topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertFalse(mock_manager.append_data.called)

class TestIndividualPayloadFullTopicFieldName(unittest.TestCase):
    topic_end = 'bar'
    topic = 'foo/' + topic_end
    single_topic = topic_end
    multi_topic = 'foo1/foo2/' + topic_end

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config_dict = {}
    message_handler_config_dict['type'] = 'individual'

    def test_bad_payload(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        msg = Msg(self.topic,
                  ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),   # pylint: disable=unused-variable
                  0,
                  0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, None)

        msg = Msg(self.topic, '', 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.error.call_count, 2)

    def test_None_payload(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config_dict = dict(self.message_handler_config_dict)
        message_handler_config_dict['full_topic_fieldname'] = True

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        msg = Msg(self.topic, None, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: None}, msg.topic)

    def test_single_topic(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(configobj.ConfigObj(self.message_handler_config_dict), mock_logger, mock_manager)

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

        message_handler_config_dict = dict(self.message_handler_config_dict)
        message_handler_config_dict['full_topic_fieldname'] = True

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.multi_topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: payload}, msg.topic)

    def test_two_topics(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config_dict = dict(self.message_handler_config_dict)
        message_handler_config_dict['full_topic_fieldname'] = True

        SUT = MessageCallbackProvider(configobj.ConfigObj(message_handler_config_dict), mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        if PY2:
            payload_str = str(payload)
        else:
            payload_str = str(payload).encode('UTF-8')

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {msg.topic: payload}, msg.topic)

if __name__ == '__main__':
    unittest.main(exit=False)
