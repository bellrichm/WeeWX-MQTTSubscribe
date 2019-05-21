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
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': None,
            'password': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
            'topic': None,
            'archive_topic': None,
            'message_handler': {}
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
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
            'password': None,
            'topic': None,
            'archive_topic': None,
            'message_handler': {}
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
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': None,
            'password': None,
            'topic': None,
            'archive_topic': None,
            'message_handler': {}
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
            'full_topic_fieldname': False,
            'keyword_delimiter': None,
            'keyword_separator': None,
            'host': host,
            'keepalive': keepalive,
            'port': port,
            'username': username,
            'password': password,
            'topic': None,
            'archive_topic': None,
            'message_handler': {}
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
        config_dict['message_handler'] = {}

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.MessageCallbackFactory') as mock_factory:
                SUT = MQTTSubscribe(config_dict)

                rc = random.randint(1, 10)
                SUT._on_connect(mock_client, None, None, rc,)

                self.assertEqual(mock_client.subscribe.call_count, 2)
                mock_client.subscribe.assert_any_call(topic1)
                mock_client.subscribe.assert_any_call(topic2)

if __name__ == '__main__':
    unittest.main()
