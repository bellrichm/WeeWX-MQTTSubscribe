from __future__ import with_statement

import unittest
import mock

import random
import string
from collections import deque

from user.MQTTSubscribe import MessageCallbackFactory

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

if __name__ == '__main__':
    unittest.main()