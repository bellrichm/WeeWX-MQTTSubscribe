from __future__ import with_statement

import unittest
import mock

import json
import random
import six
import string
import time
import weewx
from collections import deque

from user.MQTTSubscribe import MessageCallbackFactory

class Msg():
    pass

class TestGetDefaultCallBacks(unittest.TestCase):
    def test_get_unknown_payload_type(self):
        message_handler_config = {}
        message_handler_config['type'] = 'foobar'

        # ToDo - check exception
        #SUT = MessageCallbackFactory(message_handler_config)

    def test_get_individual_payload_type(self):
        message_handler_config = {}
        message_handler_config['type'] = 'individual'

        SUT = MessageCallbackFactory(message_handler_config)

        callback = SUT.get_callback()
        self.assertEqual(callback, SUT._on_message_individual)

    def test_get_json_payload_type(self):
        message_handler_config = {}
        message_handler_config['type'] = 'json'

        SUT = MessageCallbackFactory(message_handler_config)

        callback = SUT.get_callback()
        self.assertEqual(callback, SUT._on_message_json)

    def test_get_keyword_payload_type(self):
        message_handler_config = {}
        message_handler_config['type'] = 'keyword'

        SUT = MessageCallbackFactory(message_handler_config)

        callback = SUT.get_callback()
        self.assertEqual(callback, SUT._on_message_keyword)

class TestQueueSizeCheck(unittest.TestCase):
    def test_queue_max_reached(self):
        message_handler_config = {}
        message_handler_config['type'] = 'json'

        SUT = MessageCallbackFactory(message_handler_config)

        queue = deque()
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        orig_queue_size = len(queue)
        max_queue = 2

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._queue_size_check(queue, max_queue)
            self.assertEqual(mock_logerr.call_count, orig_queue_size-max_queue+1)
            self.assertEqual(len(queue), max_queue-1)

    def test_queue_max_not_reached(self):
        message_handler_config = {}
        message_handler_config['type'] = 'json'

        SUT = MessageCallbackFactory(message_handler_config)

        queue = deque()
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        orig_queue_size = len(queue)
        max_queue = 7

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._queue_size_check(queue, max_queue)
            self.assertEqual(mock_logerr.call_count, 0)
            self.assertEqual(len(queue), orig_queue_size)

    def test_queue_max_equal(self):
        message_handler_config = {}
        message_handler_config['type'] = 'json'

        SUT = MessageCallbackFactory(message_handler_config)

        queue = deque()
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        orig_queue_size = len(queue)
        max_queue = 4

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._queue_size_check(queue, max_queue)
            self.assertEqual(mock_logerr.call_count, orig_queue_size-max_queue+1)
            self.assertEqual(len(queue), max_queue-1)

class TestKeywordload(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]

    topic = 'foo/bar'
    userdata = {}
    userdata['keyword_delimiter'] = ','
    userdata['keyword_separator'] = '='
    userdata['topics'] = {}
    userdata['topics'][topic] = {}
    userdata['topics'][topic]['unit_system'] = unit_system
    userdata['topics'][topic]['max_queue'] = six.MAXSIZE

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'keyword'

    def test_payload_empty(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_keyword(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_payload_bad_data(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = 'field=value'

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_keyword(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_payload_missing_delimiter(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = 'field1=1 field2=2'

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_keyword(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_payload_missing_separator(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = 'field1:1'

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_keyword(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 3)

    def test_payload_missing_dateTime(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        self.userdata['topics'][self.topic]['queue'] = deque()

        payload_str=""
        delim=""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim=","

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload_str

        SUT._on_message_keyword(None, self.userdata, msg)

        queue = self.userdata['topics'][self.topic]['queue']
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('dateTime', data)

    def test_payload_missing_units(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()

        self.userdata['topics'][self.topic]['queue'] = deque()

        payload_str=""
        delim=""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim=","

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload_str

        SUT._on_message_keyword(None, self.userdata, msg)
        queue = self.userdata['topics'][self.topic]['queue']
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)

    def test_payload_good(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        self.userdata['topics'][self.topic]['queue'] = deque()

        payload_str=""
        delim=""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim=","

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload_str

        SUT._on_message_keyword(None, self.userdata, msg)
        queue = self.userdata['topics'][self.topic]['queue']
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictEqual(data, payload_dict)

class TestJsonPayload(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]

    topic = 'foo/bar'
    userdata = {}
    userdata['topics'] = {}
    userdata['topics'][topic] = {}
    userdata['topics'][topic]['unit_system'] = unit_system
    userdata['topics'][topic]['max_queue'] = six.MAXSIZE

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'json'

    def test_invalid_json(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_json(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_json(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_missing_dateTime(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        self.userdata['topics'][self.topic]['queue'] = deque()

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload

        SUT._on_message_json(None, self.userdata, msg)

        queue = self.userdata['topics'][self.topic]['queue']
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('dateTime', data)

    def test_missing_units(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()

        self.userdata['topics'][self.topic]['queue'] = deque()

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload

        SUT._on_message_json(None, self.userdata, msg)

        queue = self.userdata['topics'][self.topic]['queue']
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)

    def test_payload_good(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        self.userdata['topics'][self.topic]['queue'] = deque()

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg()
        msg.topic = self.topic
        msg.payload = payload

        SUT._on_message_json(None, self.userdata, msg)

        queue = self.userdata['topics'][self.topic]['queue']
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictEqual(data, payload_dict)

class TestIndividualPayloadSingleTopicFieldName(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]

    topic = 'foo/bar'
    userdata = {}
    userdata['full_topic_fieldname'] = False
    userdata['topics'] = {}
    userdata['topics'][topic] = {}
    userdata['topics'][topic]['unit_system'] = unit_system
    userdata['topics'][topic]['max_queue'] = six.MAXSIZE

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'individual'

    def test_bad_payload(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_individual(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_individual(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_None_payload(self):
        fieldname = b'bar'

        SUT = MessageCallbackFactory(self.message_handler_config)

        self.userdata['topics'][self.topic]['queue'] = deque()

        msg = Msg()
        msg.topic = self.topic
        msg.payload = None

        SUT._on_message_individual(None, self.userdata, msg)

        queue = self.userdata['topics'][self.topic]['queue']

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

        SUT = MessageCallbackFactory(self.message_handler_config)

        self.userdata['topics'][topic] = {}
        self.userdata['topics'][topic]['queue'] = deque()
        self.userdata['topics'][topic]['max_queue'] = six.MAXSIZE
        self.userdata['topics'][topic]['unit_system'] = self.unit_system

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, self.userdata, msg)

        queue = self.userdata['topics'][topic]['queue']
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

        SUT = MessageCallbackFactory(self.message_handler_config)

        self.userdata['topics'][topic] = {}
        self.userdata['topics'][topic]['queue'] = deque()
        self.userdata['topics'][topic]['max_queue'] = six.MAXSIZE
        self.userdata['topics'][topic]['unit_system'] = self.unit_system

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, self.userdata, msg)

        queue = self.userdata['topics'][topic]['queue']
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

        SUT = MessageCallbackFactory(self.message_handler_config)

        self.userdata['topics'][topic] = {}
        self.userdata['topics'][topic]['queue'] = deque()
        self.userdata['topics'][topic]['max_queue'] = six.MAXSIZE
        self.userdata['topics'][topic]['unit_system'] = self.unit_system

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, self.userdata, msg)

        queue = self.userdata['topics'][topic]['queue']
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
    userdata = {}
    userdata['full_topic_fieldname'] = True
    userdata['topics'] = {}
    userdata['topics'][topic] = {}
    userdata['topics'][topic]['unit_system'] = unit_system
    userdata['topics'][topic]['max_queue'] = six.MAXSIZE

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    message_handler_config = {}
    message_handler_config['type'] = 'individual'

    def test_bad_payload(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_individual(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        SUT = MessageCallbackFactory(self.message_handler_config)

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_individual(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_None_payload(self):
        topic_byte = b'foo/bar' # ToDo - use self.topic

        message_handler_config = dict(self.message_handler_config)
        message_handler_config['full_topic_fieldname'] = True

        SUT = MessageCallbackFactory(message_handler_config)

        self.userdata['topics'][self.topic]['queue'] = deque()

        msg = Msg()
        msg.topic = self.topic
        msg.payload = None

        SUT._on_message_individual(None, self.userdata, msg)

        queue = self.userdata['topics'][self.topic]['queue']
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

        SUT = MessageCallbackFactory(self.message_handler_config)

        self.userdata['topics'][topic] = {}
        self.userdata['topics'][topic]['queue'] = deque()
        self.userdata['topics'][topic]['max_queue'] = six.MAXSIZE
        self.userdata['topics'][topic]['unit_system'] = self.unit_system

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, self.userdata, msg)

        queue = self.userdata['topics'][topic]['queue']
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

        message_handler_config = dict(self.message_handler_config)
        message_handler_config['full_topic_fieldname'] = True

        SUT = MessageCallbackFactory(message_handler_config)

        self.userdata['topics'][topic] = {}
        self.userdata['topics'][topic]['queue'] = deque()
        self.userdata['topics'][topic]['max_queue'] = six.MAXSIZE
        self.userdata['topics'][topic]['unit_system'] = self.unit_system

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, self.userdata, msg)

        queue = self.userdata['topics'][topic]['queue']
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

        message_handler_config = dict(self.message_handler_config)
        message_handler_config['full_topic_fieldname'] = True

        SUT = MessageCallbackFactory(message_handler_config)

        self.userdata['topics'][topic] = {}
        self.userdata['topics'][topic]['queue'] = deque()
        self.userdata['topics'][topic]['max_queue'] = six.MAXSIZE
        self.userdata['topics'][topic]['unit_system'] = self.unit_system

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT._on_message_individual(None, self.userdata, msg)

        queue = self.userdata['topics'][topic]['queue']
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