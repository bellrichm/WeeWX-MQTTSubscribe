from __future__ import with_statement

import unittest
import mock

from collections import deque
import configobj
import random
import string
import time

from user.MQTTSubscribe import TopicManager

class TestQueueSizeCheck(unittest.TestCase):
    topic = 'foo/bar'
    config_dict = {}
    config_dict[topic] = {}
    config = configobj.ConfigObj(config_dict)

    def test_queue_max_reached(self):
        SUT = TopicManager(self.config)

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
        SUT = TopicManager(self.config)

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
        SUT = TopicManager(self.config)

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

class TestAppendData(unittest.TestCase):
    topic = 'foo/bar'
    config_dict = {}
    config_dict[topic] = {}
    config = configobj.ConfigObj(config_dict)

    def test_append_good_wind_data(self):
        fieldname = 'windSpeed'
        queue_data = {
            fieldname: random.uniform(1, 100),
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': time.time()
        }

        SUT = TopicManager(self.config)

        SUT.append_data(self.topic, queue_data, fieldname=fieldname)
        queue = SUT._get_queue(self.topic)
        wind_queue = SUT._get_wind_queue(self.topic)

        self.assertEqual(len(wind_queue), 1)
        self.assertEqual(len(queue), 0)
        queue_element = wind_queue.popleft()
        self.assertDictEqual(queue_element, queue_data)

    def test_append_good_data(self):
        queue_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': time.time()
        }

        SUT = TopicManager(self.config)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)
        wind_queue = SUT._get_wind_queue(self.topic)

        self.assertEqual(len(wind_queue), 0)
        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        self.assertDictEqual(queue_element, queue_data)

    def test_missing_datetime(self):
        queue_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1
        }

        SUT = TopicManager(self.config)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)
        wind_queue = SUT._get_wind_queue(self.topic)

        self.assertEqual(len(wind_queue), 0)
        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        self.assertDictContainsSubset(queue_data, queue_element)
        self.assertIn('dateTime', queue_element)

    def test_missing_units(self):
        queue_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'dateTime': time.time()
        }

        SUT = TopicManager(self.config)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)
        wind_queue = SUT._get_wind_queue(self.topic)

        self.assertEqual(len(wind_queue), 0)
        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        self.assertDictContainsSubset(queue_data, queue_element)
        self.assertIn('usUnits', queue_element)

if __name__ == '__main__':
    unittest.main()