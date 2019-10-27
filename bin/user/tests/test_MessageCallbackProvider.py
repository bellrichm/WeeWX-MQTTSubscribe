# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access

from __future__ import with_statement

import unittest
import mock

import json
import random
import six
import string
import time

from user.MQTTSubscribe import MessageCallbackProvider, TopicManager, Logger

class Msg(object):
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain

class TestGetDefaultCallBacks(unittest.TestCase):
    def test_get_unknown_payload_type(self):
        message_handler_config = {}
        payload_type = 'foobar'
        message_handler_config['type'] = payload_type

        with self.assertRaises(ValueError) as context:
            MessageCallbackProvider(message_handler_config, None, None)

        self.assertEqual(str(context.exception), "Invalid type configured: %s" % payload_type)


    def test_get_individual_payload_type(self):
        message_handler_config = {}
        message_handler_config['type'] = 'individual'

        SUT = MessageCallbackProvider(message_handler_config, None, None)

        callback = SUT.get_callback()
        self.assertEqual(callback, SUT._on_message_individual)

    def test_get_json_payload_type(self):
        message_handler_config = {}
        message_handler_config['type'] = 'json'

        SUT = MessageCallbackProvider(message_handler_config, None, None)

        callback = SUT.get_callback()
        self.assertEqual(callback, SUT._on_message_json)

    def test_get_keyword_payload_type(self):
        message_handler_config = {}
        message_handler_config['type'] = 'keyword'

        SUT = MessageCallbackProvider(message_handler_config, None, None)

        callback = SUT.get_callback()
        self.assertEqual(callback, SUT._on_message_keyword)

class TestKeywordload(unittest.TestCase):
    topic = 'foo/bar'

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'keyword'

    def test_payload_empty(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic, '', 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 3)

    def test_payload_bad_data(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic, 'field=value', 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_payload_missing_delimiter(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic, 'field1=1 field2=2', 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_payload_missing_separator(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic, 'field1:1', 0, 0)

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 3)

    def test_payload_missing_dateTime(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim = ","

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_missing_units(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim = ","

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_good(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str = ""
        delim = ""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim = ","

        msg = Msg(self.topic, payload_str, 0, 0)

        SUT._on_message_keyword(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

class TestJsonPayload(unittest.TestCase):
    topic = 'foo/bar'

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'json'

    def test_invalid_json(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic,
                  ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), # pylint: disable=unused-variable
                  0,
                  0)

        SUT._on_message_json(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic, '', 0, 0)

        SUT._on_message_json(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_missing_dateTime(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_missing_units(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_good(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, payload_dict)

    def test_payload_nested(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

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

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg(self.topic, payload, 0, 0)

        SUT._on_message_json(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, flattened_payload_dict)

class TestIndividualPayloadSingleTopicFieldName(unittest.TestCase):
    fieldname = b'bar'
    topic = b'foo/' + fieldname
    single_topic = fieldname
    multi_topic = b'foo1/foo2/' + fieldname

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'individual'

    def test_bad_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic,
                  ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), # pylint: disable=unused-variable
                  0,
                  0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic, '', 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_None_payload(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload = None
        msg = Msg(self.topic.decode('utf-8'), payload, 0, 0)

        SUT._on_message_individual(None, None, msg)

        mock_manager.append_data.assert_called_once_with(msg.topic, {self.fieldname: None})

    def test_single_topic(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        msg = Msg(self.single_topic.decode('utf-8'), str(payload), 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.fieldname: payload})

    def test_multiple_topics(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        msg = Msg(self.multi_topic.decode('utf-8'),
                  str(payload),
                  0,
                  0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.fieldname: payload})

    def test_two_topics(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        msg = Msg(self.topic.decode('utf-8'),
                  str(payload),
                  0,
                  0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.fieldname: payload})

class TestIndividualPayloadFullTopicFieldName(unittest.TestCase):
    fieldname = b'bar'
    topic = b'foo/' + fieldname
    single_topic = fieldname
    multi_topic = b'foo1/foo2/' + fieldname

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'individual'

    def test_bad_payload(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic,
                  ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), # pylint: disable=unused-variable
                  0,
                  0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg(self.topic, '', 0, 0)

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_None_payload(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config = dict(self.message_handler_config)
        message_handler_config['full_topic_fieldname'] = True

        SUT = MessageCallbackProvider(message_handler_config, mock_logger, mock_manager)

        msg = Msg(self.topic.decode('utf-8'), None, 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic: None})

    def test_single_topic(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        msg = Msg(self.single_topic.decode('utf-8'), str(payload), 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.fieldname: payload})

    def test_multiple_topics(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config = dict(self.message_handler_config)
        message_handler_config['full_topic_fieldname'] = True

        SUT = MessageCallbackProvider(message_handler_config, mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        msg = Msg(self.multi_topic.decode('utf-8'), str(payload), 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.multi_topic: payload})

    def test_two_topics(self):
        mock_manager = mock.Mock(spec=TopicManager)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config = dict(self.message_handler_config)
        message_handler_config['full_topic_fieldname'] = True

        SUT = MessageCallbackProvider(message_handler_config, mock_logger, mock_manager)

        payload = round(random.uniform(1, 100), 2)
        msg = Msg(self.topic.decode('utf-8'), str(payload), 0, 0)

        SUT._on_message_individual(None, None, msg)
        mock_manager.append_data.assert_called_once_with(msg.topic, {self.topic: payload})

if __name__ == '__main__':
    unittest.main(exit=False)
