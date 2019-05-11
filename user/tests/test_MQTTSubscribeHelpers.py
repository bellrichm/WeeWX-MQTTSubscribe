from __future__ import with_statement

import unittest
import mock

import random
import string

from user.MQTTSubscribe import create_topics

class TestInitialization(unittest.TestCase):
    def test_not_both_topic_and_topics(self):
        topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        config_dict = {}
        config_dict['topics'] = {}
        config_dict['topics'][topic] = {}
        config_dict['topic'] = topic

        with self.assertRaises(ValueError):
            create_topics(False, config_dict)


    def test_topics(self):
        unit_system = 1
        topic1 = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        topic2 = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        config_dict = {}
        config_dict['unit_system'] ='US'
        config_dict['topics'] = {}
        config_dict['topics'][topic1] = {}
        config_dict['topics'][topic2] = {}

        test_dict = {}
        test_dict[topic1] = {}
        test_dict[topic1]['unit_system'] = unit_system
        test_dict[topic2] = {}
        test_dict[topic2]['unit_system'] = unit_system

        topics = create_topics(False, config_dict)

        self.assertEqual(len(topics), 2)
        self.assertDictContainsSubset(test_dict[topic1], topics[topic1])
        self.assertIn('queue', topics[topic1])
        self.assertDictContainsSubset(test_dict[topic2], topics[topic2])
        self.assertIn('queue', topics[topic2])

    def test_topic(self):
        unit_system = 1
        topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        config_dict = {}
        config_dict['unit_system'] ='US'
        config_dict['topic'] = topic

        test_dict = {}
        test_dict[topic] = {}
        test_dict[topic]['unit_system'] = unit_system

        topics = create_topics(False, config_dict)

        self.assertEqual(len(topics), 1)
        self.assertDictContainsSubset(test_dict[topic], topics[topic])
        self.assertIn('queue', topics[topic])

if __name__ == '__main__':
    unittest.main()
