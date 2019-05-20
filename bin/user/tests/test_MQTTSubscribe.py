from __future__ import with_statement

import unittest
import mock

from collections import deque
import json
import paho.mqtt.client
import random
import six
import string
import time
import weewx
from user.MQTTSubscribe import MQTTSubscribe

class Msg():
    pass

class TestInitialization(unittest.TestCase):
    def test_username_None(self):
        unit_system = random.randint(1, 10)
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'label_map': {},
            'payload_type': None,
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': None,
            'password': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
            'topic': None,
            'archive_topic': None
        }

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                SUT.client.username_pw_set.assert_not_called()
                SUT.client.connect.assert_called_once_with(host, port, keepalive)

    def test_password_None(self):
        unit_system = random.randint(1, 10)
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'label_map': {},
            'payload_type': None,
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
            'password': None,
            'topic': None,
            'archive_topic': None
        }

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                SUT.client.username_pw_set.assert_not_called()
                SUT.client.connect.assert_called_once_with(host, port, keepalive)

    def test_username_and_password_None(self):
        unit_system = random.randint(1, 10)
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'label_map': {},
            'payload_type': None,
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': None,
            'password': None,
            'topic': None,
            'archive_topic': None
        }

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                SUT.client.username_pw_set.assert_not_called()
                SUT.client.connect.assert_called_once_with(host, port, keepalive)

    def test_username_and_password_set(self):
        unit_system = random.randint(1, 10)
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        username = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        password = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        config_dict = {
            'console': False,
            'label_map': {},
            'payload_type': None,
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': username,
            'password': password,
            'topic': None,
            'archive_topic': None
        }

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                SUT.client.username_pw_set.assert_called_once_with(username, password)
                SUT.client.connect.assert_called_once_with(host, port, keepalive)

class Teston_connect(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]
    config_dict = {
        'console': False,
        'label_map': {},
        'payload_type': None,
        'full_topic_fieldname': False,
        'keyword_delimiter': None,
        'keyword_separator': None,
        'host': 'host',
        'keepalive': random.randint(1, 10),
        'port': random.randint(1, 10),
        'username': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
        'password': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
        'archive_topic': None
    }

    def test_multiple_topics(self):
        topic1 = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        topic2 = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topics'] = {}
        config_dict['topics'][topic1] = {}
        config_dict['topics'][topic2] = {}

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                rc = random.randint(1, 10)
                SUT._on_connect(mock_client, None, None, rc,)

                self.assertEqual(mock_client.subscribe.call_count, 2)
                mock_client.subscribe.assert_any_call(topic1)
                mock_client.subscribe.assert_any_call(topic2)

class TestIndividualPayloadSingleTopicFieldName(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]
    config_dict = {
        'console': False,
        'label_map': {},
        'payload_type': 'keyword',
        'full_topic_fieldname': False,
        'keyword_delimiter': None,
        'keyword_separator': None,
        'host': 'host',
        'keepalive': random.randint(1, 10),
        'port': random.randint(1, 10),
        'username': None,
        'password': None,
        'topic': None,
        'archive_topic': None
    }

    def test_bad_payload(self):
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            SUT = MQTTSubscribe(config_dict)

            msg = Msg()
            msg.topic = topic
            msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

            ##with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
                ##SUT._on_message_individual(None, None, msg)
                ##self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            SUT = MQTTSubscribe(config_dict)

            msg = Msg()
            msg.topic = topic
            msg.payload = ''

            ##with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
                ##SUT._on_message_individual(None, None, msg)
                ##self.assertEqual(mock_logerr.call_count, 2)

    def test_None_payload(self):
        fieldname = b'bar'
        topic = 'foo/' + fieldname.decode('utf-8')
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            SUT = MQTTSubscribe(config_dict)

            msg = Msg()
            msg.topic = topic
            msg.payload = None

            ##SUT._on_message_individual(None, None, msg)
            ##queue = SUT.topics[topic]['queue']
            ##self.assertEqual(len(queue), 1)
            ##data = queue[0]
            ##self.assertIn('dateTime', data)
            ##self.assertIsInstance(data['dateTime'], float)
            ##self.assertIn('usUnits', data)
            ##self.assertEqual(data['usUnits'], self.unit_system)
            ##self.assertIn(fieldname, data)
            ##self.assertIsNone(data[fieldname])

    def test_single_topic(self):
        fieldname = b'bar'
        topic = fieldname.decode('utf-8')
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                msg = Msg()
                msg.topic = topic
                payload = random.uniform(1, 100)
                msg.payload = str(payload)

                ##SUT._on_message_individual(None, None, msg)
                ##queue = SUT.topics[topic]['queue']
                ##self.assertEqual(len(queue), 1)
                ##data = queue[0]
                ##self.assertIn('dateTime', data)
                ##self.assertIsInstance(data['dateTime'], float)
                ##self.assertIn('usUnits', data)
                ##self.assertEqual(data['usUnits'], self.unit_system)
                ##self.assertIn(fieldname, data)
                ##self.assertIsInstance(data[fieldname], float)
                ##self.assertAlmostEqual(data[fieldname], payload)

    def test_multiple_topics(self):
        fieldname = b'bar'
        topic = 'foo1/foo2/' + fieldname.decode('utf-8')
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                msg = Msg()
                msg.topic = topic
                payload = random.uniform(1, 100)
                msg.payload = str(payload)

                ##SUT._on_message_individual(None, None, msg)
                ##queue = SUT.topics[topic]['queue']
                ##self.assertEqual(len(queue), 1)
                ##data = queue[0]
                ##self.assertIn('dateTime', data)
                ##self.assertIsInstance(data['dateTime'], float)
                ##self.assertIn('usUnits', data)
                ##self.assertEqual(data['usUnits'], self.unit_system)
                ##self.assertIn(fieldname, data)
                ##self.assertIsInstance(data[fieldname], float)
                ##self.assertAlmostEqual(data[fieldname], payload)

    def test_two_topics(self):
        fieldname = b'bar'
        topic = 'foo/' + fieldname.decode('utf-8')
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                msg = Msg()
                msg.topic = topic
                payload = random.uniform(1, 100)
                msg.payload = str(payload)

                ##SUT._on_message_individual(None, None, msg)
                ##queue = SUT.topics[topic]['queue']
                ##self.assertEqual(len(queue), 1)
                ##data = queue[0]
                ##self.assertIn('dateTime', data)
                ##self.assertIsInstance(data['dateTime'], float)
                ##self.assertIn('usUnits', data)
                ##self.assertEqual(data['usUnits'], self.unit_system)
                ##self.assertIn(fieldname, data)
                ##self.assertIsInstance(data[fieldname], float)
                ##self.assertAlmostEqual(data[fieldname], payload)

class TestIndividualPayloadFullTopicFieldName(unittest.TestCase):
    unit_system_name = 'US'
    unit_system = weewx.units.unit_constants[unit_system_name]
    config_dict = {
        'console': False,
        'label_map': {},
        'payload_type': None,
        'full_topic_fieldname': True,
        'keyword_delimiter': None,
        'keyword_separator': None,
        'host': 'host',
        'keepalive': random.randint(1, 10),
        'port': random.randint(1, 10),
        'username': None,
        'password': None,
        'topic': None,
        'archive_topic': None
    }

    def test_bad_payload(self):
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                msg = Msg()
                msg.topic = topic
                msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

                ##with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
                    ##SUT._on_message_individual(None, None, msg)
                    ##self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                msg = Msg()
                msg.topic = topic
                msg.payload = ''

                ##with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
                    ##SUT._on_message_individual(None, None, msg)
                    ##self.assertEqual(mock_logerr.call_count, 2)

    def test_None_payload(self):
        topic_byte = b'foo/bar'
        topic = topic_byte.decode('utf-8')
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                msg = Msg()
                msg.topic = topic
                msg.payload = None

            ##with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
                ##SUT._on_message_individual(None, None, msg)

                ##queue = SUT.topics[topic]['queue']
                ##self.assertEqual(len(queue), 1)
                ##data = queue[0]
                ##self.assertIn('dateTime', data)
                ##self.assertIsInstance(data['dateTime'], float)
                ##self.assertIn('usUnits', data)
                ##self.assertIn(topic_byte, data)
                ##self.assertIsNone(data[topic_byte])

    def test_single_topic(self):
        topic_byte = b'bar'
        topic = topic_byte.decode('utf-8')
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                msg = Msg()
                msg.topic = topic
                payload = random.uniform(1, 100)
                msg.payload = str(payload)

                ##SUT._on_message_individual(None, None, msg)

                ##queue = SUT.topics[topic]['queue']
                ##self.assertEqual(len(queue), 1)
                ##data = queue[0]
                ##self.assertIn('dateTime', data)
                ##self.assertIsInstance(data['dateTime'], float)
                ##self.assertIn('usUnits', data)
                ##self.assertEqual(data['usUnits'], self.unit_system)
                ##self.assertIn(topic_byte, data)
                ##self.assertIsInstance(data[topic_byte], float)
                ##self.assertAlmostEqual(data[topic_byte], payload)

    def test_multiple_topics(self):
        topic_byte = b'foo1/foo2/bar'
        topic = topic_byte.decode('utf-8')
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                msg = Msg()
                msg.topic = topic
                payload = random.uniform(1, 100)
                msg.payload = str(payload)

                ##SUT._on_message_individual(None, None, msg)
                ##queue = SUT.topics[topic]['queue']
                ##self.assertEqual(len(queue), 1)
                ##data = queue[0]
                ##self.assertIn('dateTime', data)
                ##self.assertIsInstance(data['dateTime'], float)
                ##self.assertIn('usUnits', data)
                ##self.assertEqual(data['usUnits'], self.unit_system)
                ##self.assertIn(topic_byte, data)
                ##self.assertIsInstance(data[topic_byte], float)
                ##self.assertAlmostEqual(data[topic_byte], payload)

    def test_two_topics(self):
        topic_byte = b'foo/bar'
        topic = topic_byte.decode('utf-8')
        config_dict = dict(self.config_dict)
        config_dict['unit_system'] = self.unit_system_name
        config_dict['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                msg = Msg()
                msg.topic = topic
                payload = random.uniform(1, 100)
                msg.payload = str(payload)

                ##SUT._on_message_individual(None, None, msg)
                ##queue = SUT.topics[topic]['queue']
                ##self.assertEqual(len(queue), 1)
                ##data = queue[0]
                ##self.assertIn('dateTime', data)
                ##self.assertIsInstance(data['dateTime'], float)
                ##self.assertIn('usUnits', data)
                ##self.assertEqual(data['usUnits'], self.unit_system)
                ##self.assertIn(topic_byte, data)
                ##self.assertIsInstance(data[topic_byte], float)
                ##self.assertAlmostEqual(data[topic_byte], payload)

if __name__ == '__main__':
    unittest.main()
