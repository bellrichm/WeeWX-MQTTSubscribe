from __future__ import with_statement

import unittest
import mock

from collections import deque
import json
import paho.mqtt.client as mqtt
import random
import six
import string
import time
from user.MQTTSubscribe import MQTTSubscribe, MQTTSubscribeService

class Msg():
    pass

class TestInitialization(unittest.TestCase):
    def test_payload_type_json(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        unit_system = random.randint(1, 10)
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'label_map': {},
            'payload_type': 'json',
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

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        self.assertEqual(mock_client.on_message, SUT.on_message_json)

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_payload_type_individual(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        unit_system = random.randint(1, 10)
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'label_map': {},
            'payload_type': 'individual',
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

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        self.assertEqual(mock_client.on_message, SUT.on_message_individual)

    def test_payload_type_keyword(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        unit_system = random.randint(1, 10)
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'label_map': {},
            'payload_type': 'keyword',
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

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        self.assertEqual(mock_client.on_message, SUT.on_message_keyword)

        mock_client.connect.assert_called_once_with(host, port, keepalive)

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_payload_type_other(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        unit_system = random.randint(1, 10)
        host = 'host'
        port = random.randint(1000, 9999)
        keepalive = random.randint(1, 10)
        config_dict = {
            'console': False,
            'label_map': {},
            'payload_type': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
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

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        self.assertEqual(mock_client.on_message, SUT.on_message)

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_username_None(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
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

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        mock_client.username_pw_set.assert_not_called()

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_password_None(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
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

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        mock_client.username_pw_set.assert_not_called()

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_username_and_password_None(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
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

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        mock_client.username_pw_set.assert_not_called()

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_username_and_password_set(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
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

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        mock_client.username_pw_set.assert_called_once_with(username, password)

        mock_client.connect.assert_called_once_with(host, port, keepalive)

class Teston_connect(unittest.TestCase):
    queue = None
    archive_queue = None
    unit_system = random.randint(1, 10)
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
        'topic': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
        'archive_topic': None
    }

    def test_multiple_topics(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic1 = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        topic2 = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        config_dict = dict(self.config_dict)

        topics = {}
        topics[topic1] = {}
        topics[topic1]['unit_system'] = self.unit_system
        topics[topic1]['queue'] = None
        topics[topic2] = {}
        topics[topic2]['unit_system'] = self.unit_system
        topics[topic2]['queue'] = None

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        rc = random.randint(1, 10)
        SUT.on_connect(mock_client, None, None, rc,)

        self.assertEqual(mock_client.subscribe.call_count, 2)
        mock_client.subscribe.assert_any_call(topic1)
        mock_client.subscribe.assert_any_call(topic2)

class TestQueueSizeCheck(unittest.TestCase):
    mock_client = mock.Mock(spec=mqtt.Client)
    
    def test_queue_max_reached(self):
        SUT = MQTTSubscribe(self.mock_client, None, {})

        queue = deque()
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        orig_queue_size = len(queue)
        max_queue = 2

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.queue_size_check(queue, max_queue)
            self.assertEqual(mock_logerr.call_count, orig_queue_size-max_queue+1)
            self.assertEqual(len(queue), max_queue-1)

    def test_queue_max_not_reached(self):
        SUT = MQTTSubscribe(self.mock_client, None, {})

        queue = deque()
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        orig_queue_size = len(queue)
        max_queue = 7

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.queue_size_check(queue, max_queue)
            self.assertEqual(mock_logerr.call_count, 0)
            self.assertEqual(len(queue), orig_queue_size)

    def test_queue_max_equal(self):
        SUT = MQTTSubscribe(self.mock_client, None, {})

        queue = deque()
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append( ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        orig_queue_size = len(queue)
        max_queue = 4

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.queue_size_check(queue, max_queue)
            self.assertEqual(mock_logerr.call_count, orig_queue_size-max_queue+1)
            self.assertEqual(len(queue), max_queue-1)

class TestKeywordload(unittest.TestCase):
    unit_system = random.randint(1, 10)
    config_dict = {
        'console': False,
        'label_map': {},
        'payload_type': None,
        'full_topic_fieldname': False,
        'keyword_delimiter': ',',
        'keyword_separator': '=',
        'host': 'host',
        'keepalive': random.randint(1, 10),
        'port': random.randint(1, 10),
        'username': None,
        'password': None,
        'topic': None,
        'archive_topic': None
    }

    payload_dict = {
        'inTemp': round(random.uniform(1, 100), 2),
        'outTemp': round(random.uniform(1, 100), 2)
    }

    def test_payload_empty(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue']= deque()
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_keyword(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 3)

    def test_payload_bad_data(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = 'field=value'

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_keyword(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_payload_missing_delimiter(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = 'field1=1 field2=2'

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_keyword(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_payload_missing_separator(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue']= deque()
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = 'field1:1'

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_keyword(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 3)

    def test_payload_missing_datetime(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str=""
        delim=""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim=","

        msg = Msg()
        msg.topic = topic
        msg.payload = payload_str

        SUT.on_message_keyword(None, None, msg)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('dateTime', data)

    def test_payload_missing_units(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()

        payload_str=""
        delim=""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim=","

        msg = Msg()
        msg.topic = topic
        msg.payload = payload_str

        SUT.on_message_keyword(None, None, msg)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)

    def test_payload_good(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = round(time.time(), 2)
        payload_dict['usUnits'] = random.randint(1, 10)

        payload_str=""
        delim=""
        for key in payload_dict:
            payload_str = "%s%s%s=%f" %(payload_str, delim, key, payload_dict[key])
            delim=","

        msg = Msg()
        msg.topic = topic
        msg.payload = payload_str

        SUT.on_message_keyword(None, None, msg)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictEqual(data, payload_dict)

class TestJsonPayload(unittest.TestCase):
    unit_system = random.randint(1, 10)
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
        'username': None,
        'password': None,
        'topic': None,
        'archive_topic': None
    }

    payload_dict = {
        'inTemp': random.uniform(1, 100),
        'outTemp':random.uniform(1, 100)
    }

    def test_invalid_json(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_json(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        SUT = MQTTSubscribe(mock_client, None, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_json(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_missing_dateTime(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg()
        msg.topic = topic
        msg.payload = payload

        SUT.on_message_json(None, None, msg)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('dateTime', data)

    def test_missing_units(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg()
        msg.topic = topic
        msg.payload = payload

        SUT.on_message_json(None, None, msg)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)

    def test_payload_good(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        if six.PY2:
            payload = json.dumps(payload_dict)
        else:
            payload = json.dumps(payload_dict).encode("utf-8")

        msg = Msg()
        msg.topic = topic
        msg.payload = payload

        SUT.on_message_json(None, None, msg)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictEqual(data, payload_dict)

class TestIndividualPayloadSingleTopicFieldName(unittest.TestCase):
    unit_system = random.randint(1, 10)
    archive_queue = None
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
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_individual(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system  

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_individual(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_None_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        fieldname = b'bar'
        topic = 'foo/' + fieldname.decode('utf-8')
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = None

        SUT.on_message_individual(None, None, msg)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(fieldname, data)
        self.assertIsNone(data[fieldname])

    def test_single_topic(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        fieldname = b'bar'
        topic = fieldname.decode('utf-8')
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT.on_message_individual(None, None, msg)
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
        mock_client = mock.Mock(spec=mqtt.Client)
        fieldname = b'bar'
        topic = 'foo1/foo2/' + fieldname.decode('utf-8')
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT.on_message_individual(None, None, msg)
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
        mock_client = mock.Mock(spec=mqtt.Client)
        fieldname = b'bar'
        topic = 'foo/' + fieldname.decode('utf-8')
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT.on_message_individual(None, None, msg)
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
    unit_system = random.randint(1, 10)
    archive_queue = None
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
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system        

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_individual(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_individual(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_None_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic_byte = b'foo/bar'
        topic = topic_byte.decode('utf-8')
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        msg.payload = None

        SUT.on_message_individual(None, None, msg)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(topic_byte, data)
        self.assertIsNone(data[topic_byte])

    def test_single_topic(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic_byte = b'bar'
        topic = topic_byte.decode('utf-8')
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT.on_message_individual(None, None, msg)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertIn('dateTime', data)
        self.assertIsInstance(data['dateTime'], float)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)
        self.assertIn(topic_byte, data)
        self.assertIsInstance(data[topic_byte], float)
        self.assertAlmostEqual(data[topic_byte], payload)

    def test_multiple_topics(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic_byte = b'foo1/foo2/bar'
        topic = topic_byte.decode('utf-8')
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT.on_message_individual(None, None, msg)
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
        mock_client = mock.Mock(spec=mqtt.Client)
        topic_byte = b'foo/bar'
        topic = topic_byte.decode('utf-8')
        queue = deque()
        config_dict = dict(self.config_dict)
        config_dict['topic'] = topic

        topics = {}
        topics[topic] = {}
        topics[topic]['unit_system'] = self.unit_system
        topics[topic]['queue'] = queue
        topics[topic]['max_queue']= six.MAXSIZE

        SUT = MQTTSubscribe(mock_client, topics, config_dict)

        msg = Msg()
        msg.topic = topic
        payload = random.uniform(1, 100)
        msg.payload = str(payload)

        SUT.on_message_individual(None, None, msg)
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
