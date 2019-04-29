from __future__ import with_statement

import unittest
import mock

from collections import deque
import json
import paho.mqtt.client as mqtt
import random
import string
import time
from user.MQTTSubscribe import MQTTSubscribe, MQTTSubscribeService

class Msg():
    pass

class TestInitialization(unittest.TestCase):
    def test_payload_type_json(self):
        console = False
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        label_map = {}
        unit_system = random.randint(1, 10)
        payload_type = 'json'
        full_topic_fieldname = False
        host = 'host'
        keepalive = random.randint(1, 10)
        port = random.randint(1, 10)
        username = None
        password = None
        topic = None
        archive_topic = None

        SUT = MQTTSubscribe(console, mock_client, queue, archive_queue, label_map, unit_system, payload_type, full_topic_fieldname,
                            host, keepalive, port, username, password, topic, archive_topic
                            )

        self.assertEqual(mock_client.on_message, SUT.on_message_json)

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_payload_type_individual(self):
        console = False
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        label_map = {}
        unit_system = random.randint(1, 10)
        payload_type = 'individual'
        full_topic_fieldname = False
        host = 'host'
        keepalive = random.randint(1, 10)
        port = random.randint(1, 10)
        username = None
        password = None
        topic = None
        archive_topic = None

        SUT = MQTTSubscribe(console, mock_client, queue, archive_queue, label_map, unit_system, payload_type, full_topic_fieldname,
                            host, keepalive, port, username, password, topic, archive_topic
                            )

        self.assertEqual(mock_client.on_message, SUT.on_message_individual)

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_payload_type_other(self):
        console = False
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        label_map = {}
        unit_system = random.randint(1, 10)
        payload_type = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        full_topic_fieldname = False
        host = 'host'
        keepalive = random.randint(1, 10)
        port = random.randint(1, 10)
        username = None
        password = None
        topic = None
        archive_topic = None

        SUT = MQTTSubscribe(console, mock_client, queue, archive_queue, label_map, unit_system, payload_type, full_topic_fieldname,
                            host, keepalive, port, username, password, topic, archive_topic
                            )

        self.assertEquals(mock_client.on_message, SUT.on_message)

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_username_None(self):
        console = False
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        label_map = {}
        unit_system = random.randint(1, 10)
        payload_type = None
        full_topic_fieldname = False
        host = 'host'
        keepalive = random.randint(1, 10)
        port = random.randint(1, 10)
        username = None
        password = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        topic = None
        archive_topic = None

        SUT = MQTTSubscribe(console, mock_client, queue, archive_queue, label_map, unit_system, payload_type, full_topic_fieldname,
                            host, keepalive, port, username, password, topic, archive_topic
                            )

        mock_client.username_pw_set.assert_not_called()

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_password_None(self):
        console = False
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        label_map = {}
        unit_system = random.randint(1, 10)
        payload_type = None
        full_topic_fieldname = False
        host = 'host'
        keepalive = random.randint(1, 10)
        port = random.randint(1, 10)
        username = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        password = None
        topic = None
        archive_topic = None

        SUT = MQTTSubscribe(console, mock_client, queue, archive_queue, label_map, unit_system, payload_type, full_topic_fieldname,
                            host, keepalive, port, username, password, topic, archive_topic
                            )

        mock_client.username_pw_set.assert_not_called()

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_username_and_password_None(self):
        console = False
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        label_map = {}
        unit_system = random.randint(1, 10)
        payload_type = None
        full_topic_fieldname = False
        host = 'host'
        keepalive = random.randint(1, 10)
        port = random.randint(1, 10)
        username = None
        password = None
        topic = None
        archive_topic = None

        SUT = MQTTSubscribe(console, mock_client, queue, archive_queue, label_map, unit_system, payload_type, full_topic_fieldname,
                            host, keepalive, port, username, password, topic, archive_topic
                            )

        mock_client.username_pw_set.assert_not_called()

        mock_client.connect.assert_called_once_with(host, port, keepalive)

    def test_username_and_password_set(self):
        console = False
        mock_client = mock.Mock(spec=mqtt.Client)
        queue = None
        archive_queue = None
        label_map = {}
        unit_system = random.randint(1, 10)
        payload_type = None
        full_topic_fieldname = False
        host = 'host'
        keepalive = random.randint(1, 10)
        port = random.randint(1, 10)
        username = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        password = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        topic = None
        archive_topic = None

        SUT = MQTTSubscribe(console, mock_client, queue, archive_queue, label_map, unit_system, payload_type, full_topic_fieldname,
                            host, keepalive, port, username, password, topic, archive_topic
                            )

        mock_client.username_pw_set.assert_called_once_with(username, password)

        mock_client.connect.assert_called_once_with(host, port, keepalive)

class Teston_connect(unittest.TestCase):
    console = False
    queue = None
    archive_queue = None
    label_map = {}
    unit_system = random.randint(1, 10)
    payload_type = None
    full_topic_fieldname = False
    host = 'host'
    keepalive = random.randint(1, 10)
    port = random.randint(1, 10)
    username = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    password = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

    def test_archive_topic_set(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        archive_topic = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        SUT = MQTTSubscribe(self.console, mock_client, self.queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, self.topic, archive_topic
                            )

        rc = random.randint(1, 10)
        SUT.on_connect(mock_client, None, None, rc,)

        self.assertEqual(mock_client.subscribe.call_count, 2)
        mock_client.subscribe.assert_called_with(archive_topic)

    def test_archive_topic_not_set(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        archive_topic = None
        SUT = MQTTSubscribe(self.console, mock_client, self.queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, self.topic, archive_topic
                            )

        rc = random.randint(1, 10)
        SUT.on_connect(mock_client, None, None, rc,)

        self.assertEqual(mock_client.subscribe.call_count, 1)

class TestKeywordload(unittest.TestCase):
    pass

class TestJsonPayload(unittest.TestCase):
    console = False
    label_map = {}
    unit_system = random.randint(1, 10)
    payload_type = None
    full_topic_fieldname = False
    host = 'host'
    keepalive = random.randint(1, 10)
    port = random.randint(1, 10)
    username = None
    password = None

    payload_dict = {
        'inTemp': random.uniform(1, 100),
        'outTemp':random.uniform(1, 100)
    }

    def test_invalid_json(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        archive_topic = 'foo/archive'
        archive_queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, archive_topic
                            )

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
        archive_topic = 'foo/archive'
        archive_queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, archive_topic
                            )

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
        archive_topic = 'foo/archive'
        archive_queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, archive_topic
                            )

        payload_dict = dict(self.payload_dict)
        payload_dict['usUnits'] = random.randint(1, 10)

        msg = Msg()
        msg.topic = topic
        msg.payload = json.dumps(payload_dict)

        SUT.on_message_json(None, None, msg)
        self.assertEqual(len(archive_queue), 0)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('dateTime', data)

    def test_missing_units(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        archive_topic = 'foo/archive'
        archive_queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, archive_topic
                            )

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()

        msg = Msg()
        msg.topic = topic
        msg.payload = json.dumps(payload_dict)

        SUT.on_message_json(None, None, msg)
        self.assertEqual(len(archive_queue), 0)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictContainsSubset(payload_dict, data)
        self.assertIn('usUnits', data)
        self.assertEqual(data['usUnits'], self.unit_system)

    def test_archive_queue(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        archive_topic = 'foo/archive'
        archive_queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, archive_topic
                            )

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        msg = Msg()
        msg.topic = archive_topic
        msg.payload = json.dumps(payload_dict)

        SUT.on_message_json(None, None, msg)
        self.assertEqual(len(archive_queue), 1)
        self.assertEqual(len(queue), 0)
        data = archive_queue[0]
        self.assertDictEqual(data, payload_dict)

    def test_normal_queue(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()
        archive_topic = 'foo/archive'
        archive_queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, archive_topic
                            )

        payload_dict = dict(self.payload_dict)
        payload_dict['dateTime'] = time.time()
        payload_dict['usUnits'] = random.randint(1, 10)

        msg = Msg()
        msg.topic = topic
        msg.payload = json.dumps(payload_dict)

        SUT.on_message_json(None, None, msg)
        self.assertEqual(len(archive_queue), 0)
        self.assertEqual(len(queue), 1)
        data = queue[0]
        self.assertDictEqual(data, payload_dict)

class TestIndividualPayloadSingleTopicFieldName(unittest.TestCase):
    console = False
    archive_queue = None
    label_map = {}
    unit_system = random.randint(1, 10)
    payload_type = None
    full_topic_fieldname = False
    host = 'host'
    keepalive = random.randint(1, 10)
    port = random.randint(1, 10)
    username = None
    password = None
    archive_topic = None

    def test_bad_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

        msg = Msg()
        msg.topic = topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_individual(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

        msg = Msg()
        msg.topic = topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_individual(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_None_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        fieldname = 'bar'
        topic = 'foo/' + fieldname
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

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
        fieldname = 'bar'
        topic = fieldname
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

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
        fieldname = 'bar'
        topic = 'foo1/foo2/' + fieldname
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

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
        fieldname = 'bar'
        topic = 'foo/' + fieldname
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

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
    console = False
    archive_queue = None
    label_map = {}
    unit_system = random.randint(1, 10)
    payload_type = None
    full_topic_fieldname = True
    host = 'host'
    keepalive = random.randint(1, 10)
    port = random.randint(1, 10)
    username = None
    password = None
    archive_topic = None

    def test_bad_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

        msg = Msg()
        msg.topic = topic
        msg.payload = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_individual(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_empty_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

        msg = Msg()
        msg.topic = topic
        msg.payload = ''

        with mock.patch('user.MQTTSubscribe.logerr') as mock_logerr:
            SUT.on_message_individual(None, None, msg)
            self.assertEqual(mock_logerr.call_count, 2)

    def test_None_payload(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

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
        self.assertIn(topic, data)
        self.assertIsNone(data[topic])

    def test_single_topic(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'bar'
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

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
        self.assertIn(topic, data)
        self.assertIsInstance(data[topic], float)
        self.assertAlmostEqual(data[topic], payload)

    def test_multiple_topics(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo1/foo2/bar'
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

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
        self.assertIn(topic, data)
        self.assertIsInstance(data[topic], float)
        self.assertAlmostEqual(data[topic], payload)

    def test_two_topics(self):
        mock_client = mock.Mock(spec=mqtt.Client)
        topic = 'foo/bar'
        queue = deque()

        SUT = MQTTSubscribe(self.console, mock_client, queue, self.archive_queue, self.label_map, self.unit_system, self.payload_type, self.full_topic_fieldname,
                            self.host, self.keepalive, self.port, self.username, self.password, topic, self.archive_topic
                            )

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
        self.assertIn(topic, data)
        self.assertIsInstance(data[topic], float)
        self.assertAlmostEqual(data[topic], payload)

if __name__ == '__main__':
    unittest.main()
