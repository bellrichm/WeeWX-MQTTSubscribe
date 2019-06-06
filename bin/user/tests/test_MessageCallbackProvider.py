from __future__ import with_statement

import unittest
import mock

import configobj
import json
import random
import six
import string
import time
import weewx
from collections import deque

# ToDo - mock TopicManager
from user.MQTTSubscribe import MessageCallbackProvider, TopicManager, Logger

class Msg():
    pass

class TestGetDefaultCallBacks(unittest.TestCase):
    def test_get_unknown_payload_type(self):
        message_handler_config = {}
        message_handler_config['type'] = 'foobar'

        # ToDo - check exception
        #SUT = MessageCallbackProvider(message_handler_config, None, None)

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
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]

    topic = 'foo/bar'
    topics = {}
    topics[topic] = {}
    topics[topic]['unit_system'] = unit_system_name
    topics[topic]['max_queue'] = six.MAXSIZE
    topic_config = configobj.ConfigObj(topics)

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'keyword'

    def test_payload_empty(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 3)

    def test_payload_bad_data(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = 'field=value'

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_payload_missing_delimiter(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = 'field1=1 field2=2'

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_payload_missing_separator(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = 'field1:1'

        SUT._on_message_keyword(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 3)

    def test_payload_missing_dateTime(self):
        manager = TopicManager(self.topic_config)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str=""
        delim=""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim=","

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload_str

        SUT._on_message_keyword(None, None, msg)

        queue = SUT.topic_manager._get_queue(self.topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('dateTime', data)

    def test_payload_missing_units(self):
        manager = TopicManager(self.topic_config)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()

        payload_str=""
        delim=""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim=","

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload_str

        SUT._on_message_keyword(None, None, msg)
        queue = SUT.topic_manager._get_queue(self.topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)

    def test_payload_good(self):
        manager = TopicManager(self.topic_config)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str=""
        delim=""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim=","

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload_str

        SUT._on_message_keyword(None, None, msg)
        queue = SUT.topic_manager._get_queue(self.topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictEqual(data, payload_dict)

class TestJsonPayload(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]

    topic = 'foo/bar'

    topics = {}
    topics[topic] = {}
    topics[topic]['unit_system'] = unit_system_name
    topics[topic]['max_queue'] = six.MAXSIZE
    topic_config = configobj.ConfigObj(topics)

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'json'

    def test_invalid_json(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        SUT._on_message_json(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''

        SUT._on_message_json(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_missing_dateTime(self):
        mock_logger = mock.Mock(spec=Logger)
        manager = TopicManager(self.topic_config)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload

        SUT._on_message_json(None, None, msg)

        queue = SUT.topic_manager._get_queue(self.topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('dateTime', data)

    def test_missing_units(self):
        manager = TopicManager(self.topic_config)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload

        SUT._on_message_json(None, None, msg)

        queue = SUT.topic_manager._get_queue(self.topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)

    def test_payload_good(self):
        mock_logger = mock.Mock(spec=Logger)
        manager = TopicManager(self.topic_config)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload

        SUT._on_message_json(None, None, msg)

        queue = SUT.topic_manager._get_queue(self.topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictEqual(data, payload_dict)

class TestIndividualPayloadSingleTopicFieldName(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]

    topic = 'foo/bar'
    topics = {}
    topics[topic] = {}
    topics[topic]['unit_system'] = unit_system_name
    topics[topic]['max_queue'] = six.MAXSIZE
    topic_config = configobj.ConfigObj(topics)

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'individual'

    def test_bad_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)
        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_None_payload(self):
        fieldname = b'bar'
        manager = TopicManager(self.topic_config)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = None

        SUT._on_message_individual(None, None, msg)

        queue = SUT.topic_manager._get_queue(self.topic) # Todo - check call to append_data

        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(fieldname, data)
        self.assertIsNone(data[fieldname])

    def test_single_topic(self):
        fieldname = b'bar'
        topic = fieldname.decode('utf-8')
        
        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system_name
        topics[topic]['max_queue'] = six.MAXSIZE
        topic_config = configobj.ConfigObj(topics)
        manager = TopicManager(topic_config)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, None, msg)

        queue = SUT.topic_manager._get_queue(topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(fieldname, data)
        self.assertIsInstance(data[fieldname], float)
        self.assertAlmostEqual(data[fieldname], payload)

    def test_multiple_topics(self):
        fieldname = b'bar'
        topic = 'foo1/foo2/' + fieldname.decode('utf-8')

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system_name
        topics[topic]['max_queue'] = six.MAXSIZE
        topic_config = configobj.ConfigObj(topics)
        manager = TopicManager(topic_config)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, None, msg)

        queue = SUT.topic_manager._get_queue(topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(fieldname, data)
        self.assertIsInstance(data[fieldname], float)
        self.assertAlmostEqual(data[fieldname], payload)

    def test_two_topics(self):
        fieldname = b'bar'
        topic = 'foo/' + fieldname.decode('utf-8')
        
        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system_name
        topics[topic]['max_queue'] = six.MAXSIZE
        topic_config = configobj.ConfigObj(topics)
        manager = TopicManager(topic_config)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, None, msg)

        queue = SUT.topic_manager._get_queue(topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(fieldname, data)
        self.assertIsInstance(data[fieldname], float)
        self.assertAlmostEqual(data[fieldname], payload)

class TestIndividualPayloadFullTopicFieldName(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]

    topic = 'foo/bar'
    topics = {}
    topics[topic] = {}
    topics[topic]['unit_system'] = unit_system_name
    topics[topic]['max_queue'] = six.MAXSIZE
    topic_config = configobj.ConfigObj(topics)

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'individual'

    def test_bad_payload(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_empty_payload(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, None)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''

        SUT._on_message_individual(None, None, msg)
        self.assertEqual(mock_logger.logerr.call_count, 2)

    def test_None_payload(self):
        topic_byte = b'foo/bar' # ToDo - use self.topic
        manager = TopicManager(self.topic_config)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config = dict(self.message_handler_config)
        message_handler_config['full_topic_fieldname'] = True

        SUT = MessageCallbackProvider(message_handler_config, mock_logger, manager)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = None

        SUT._on_message_individual(None, None, msg)

        queue = SUT.topic_manager._get_queue(self.topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(topic_byte, data)
        self.assertIsNone(data[topic_byte])

    def test_single_topic(self):
        fieldname = b'bar'
        topic = fieldname.decode('utf-8')
        
        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system_name
        topics[topic]['max_queue'] = six.MAXSIZE
        topic_config = configobj.ConfigObj(topics)
        manager = TopicManager(topic_config)
        mock_logger = mock.Mock(spec=Logger)

        SUT = MessageCallbackProvider(self.message_handler_config, mock_logger, manager)
        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, None, msg)

        queue = SUT.topic_manager._get_queue(topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(fieldname, data)
        self.assertIsInstance(data[fieldname], float)
        self.assertAlmostEqual(data[fieldname], payload)

    def test_multiple_topics(self):
        fieldname = b'bar'
        topic = 'foo1/foo2/' + fieldname.decode('utf-8')
        topic_byte = b'foo1/foo2/bar' # ToDo - fix up
        
        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system_name
        topics[topic]['max_queue'] = six.MAXSIZE
        topic_config = configobj.ConfigObj(topics)
        manager = TopicManager(topic_config)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config = dict(self.message_handler_config)
        message_handler_config['full_topic_fieldname'] = True

        SUT = MessageCallbackProvider(message_handler_config, mock_logger, manager)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, None, msg)

        queue = SUT.topic_manager._get_queue(topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(topic_byte, data)
        self.assertIsInstance(data[topic_byte], float)
        self.assertAlmostEqual(data[topic_byte], payload)

    def test_two_topics(self):
        fieldname = b'bar'
        topic = 'foo/' + fieldname.decode('utf-8')
        topic_byte = b'foo/bar' # ToDo - fix up
        
        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system_name
        topics[topic]['max_queue'] = six.MAXSIZE
        topic_config = configobj.ConfigObj(topics)
        manager = TopicManager(topic_config)
        mock_logger = mock.Mock(spec=Logger)

        message_handler_config = dict(self.message_handler_config)
        message_handler_config['full_topic_fieldname'] = True

        SUT = MessageCallbackProvider(message_handler_config, mock_logger, manager)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, None, msg)

        queue = SUT.topic_manager._get_queue(topic) # Todo - check call to append_data
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(topic_byte, data)
        self.assertIsInstance(data[topic_byte], float)
        self.assertAlmostEqual(data[topic_byte], payload)

if __name__ == '__main__':
    unittest.main()