from __future__ import with_statement

import unittest
import mock

from collections import deque
import configobj
import random
import six
import time
import threading
import weewx

from user.MQTTSubscribe import MQTTSubscribeDriver

class TestgenLoopPackets(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def setup_queue_tests(self, topic):
        current_time = int(time.time() + 0.5)
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        self.queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': current_time
        }

        self.config_dict = {}
        self.config_dict['topic'] = topic

    def generator(self, test_data):
        for data in test_data:
            yield data

    def test_queue_empty(self):
        topic = 'foo/bar'
        self.setup_queue_tests(topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value = [topic])
                type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([None, self.queue_data]))

                SUT = MQTTSubscribeDriver(**self.config_dict)
                gen = SUT.genLoopPackets()
                data = next(gen, None)

                mock_time.sleep.assert_called_once()
                self.assertEqual(mock_manager.return_value.get_data.call_count, 2)

    def test_queue(self):
        topic = 'foo/bar'
        self.setup_queue_tests(topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value = [topic])
                type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([self.queue_data]))

                SUT = MQTTSubscribeDriver(**self.config_dict)

                gen=SUT.genLoopPackets()
                packet=next(gen)

                mock_time.sleep.assert_not_called()
                self.assertDictEqual(packet, self.queue_data)

class TestgenArchiveRecords(unittest.TestCase):

    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def setup_archive_queue_tests(self, archive_topic):
        current_time = int(time.time() + 0.5)
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        self.queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': current_time
        }

        self.config_dict = {}
        self.config_dict['archive_topic'] = archive_topic
        self.config_dict['topics'] = {}
        self.config_dict['topics']['foo/bar'] = {}
        self.config_dict['topics'][archive_topic] = {}

    def generator(self, test_data):
        for data in test_data:
            yield data

    def test_empty_queue(self):
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([None]))

            SUT = MQTTSubscribeDriver(**self.config_dict)
            gen=SUT.genArchiveRecords(0)
            data = next(gen, None)

            self.assertIsNone(data)

    def test_queue(self):
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)
        queue_list = [self.queue_data, self.queue_data]

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([self.queue_data, self.queue_data, None]))
            records = list()

            SUT = MQTTSubscribeDriver(**self.config_dict)

            for record in SUT.genArchiveRecords(int(time.time() + 10.5)):
                records.append(record)

            self.assertListEqual(records, queue_list)

if __name__ == '__main__':
    unittest.main()