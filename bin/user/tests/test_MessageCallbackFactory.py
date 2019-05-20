from __future__ import with_statement

import unittest
import mock

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
        payload_type = 'foobar'

        SUT = MessageCallbackFactory()

        #callback = SUT.get_callback(payload_type)

        #print(callback)

    def test_get_individual_payload_type(self):
        payload_type = 'individual'

        SUT = MessageCallbackFactory()

        callback = SUT.get_callback(payload_type)
        self.assertEqual(callback, SUT._on_message_individual)

    def test_get_json_payload_type(self):
        payload_type = 'json'

        SUT = MessageCallbackFactory()

        callback = SUT.get_callback(payload_type)
        self.assertEqual(callback, SUT._on_message_json)

    def test_get_json_payload_type(self):
        payload_type = 'keyword'

        SUT = MessageCallbackFactory()

        callback = SUT.get_callback(payload_type)
        self.assertEqual(callback, SUT._on_message_keyword)

class Testadd_callback(unittest.TestCase):
    def on_message_test_callback():
        pass

    def test_add_callback(self):
        payload_type = 'foobar'

        SUT = MessageCallbackFactory()

        SUT.add_callback(payload_type, self.on_message_test_callback)

        callbacks = SUT.Callbacks
        self.assertTrue(payload_type in callbacks)
        self.assertEqual(callbacks[payload_type], self.on_message_test_callback)

class TestQueueSizeCheck(unittest.TestCase):
    def test_queue_max_reached(self):
        config_dict = {}
        config_dict['unit_system'] = 'US'
        config_dict['topic'] = 'foo/bar'

        SUT = MessageCallbackFactory()

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
        config_dict = {}
        config_dict['unit_system'] = 'US'
        config_dict['topic'] = 'foo/bar'

        SUT = MessageCallbackFactory()

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
        config_dict = {}
        config_dict['unit_system'] = 'US'
        config_dict['topic'] = 'foo/bar'

        SUT = MessageCallbackFactory()

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
    userdata['label_map'] = {}
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

    def test_payload_empty(self):
        SUT = MessageCallbackFactory()

        msg = Msg()
        msg.topic = self.topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_keyword(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_payload_bad_data(self):
        SUT = MessageCallbackFactory()

        msg = Msg()
        msg.topic = self.topic
        msg.payload = 'field=value'

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_keyword(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_payload_missing_delimiter(self):
        SUT = MessageCallbackFactory()

        msg = Msg()
        msg.topic = self.topic
        msg.payload = 'field1=1 field2=2'

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_keyword(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_payload_missing_separator(self):
        SUT = MessageCallbackFactory()

        msg = Msg()
        msg.topic = self.topic
        msg.payload = 'field1:1'

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT._on_message_keyword(None, self.userdata, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_payload_missing_dateTime(self):
        SUT = MessageCallbackFactory()

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
        SUT = MessageCallbackFactory()

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
        SUT = MessageCallbackFactory()

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


if __name__ == '__main__':
    unittest.main()