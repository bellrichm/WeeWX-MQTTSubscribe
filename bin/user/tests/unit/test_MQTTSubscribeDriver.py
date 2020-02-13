# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest
import mock

import random
import time
import weewx

from user.MQTTSubscribe import MQTTSubscribeDriver


class TestgenLoopPackets(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def __init__(self, methodName):
        super(TestgenLoopPackets, self).__init__(methodName)
        self.queue_data = {}
        self.config_dict = {}

    def setup_queue_tests(self, topic):
        current_time = int(time.time() + 0.5)
        in_temp = random.uniform(1, 100)
        out_temp = random.uniform(1, 100)

        self.queue_data = {
            'inTemp': in_temp,
            'outTemp': out_temp,
            'usUnits': 1,
            'dateTime': current_time
        }

        self.config_dict['topic'] = topic

    @staticmethod
    def generator(test_data):
        for data in test_data:
            yield data

    def test_queue_empty(self):
        topic = 'foo/bar'
        self.setup_queue_tests(topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value=[topic])
                type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([None, self.queue_data]))

                SUT = MQTTSubscribeDriver(**self.config_dict)
                gen = SUT.genLoopPackets()
                next(gen, None)

                mock_time.sleep.assert_called_once()
                self.assertEqual(mock_manager.return_value.get_data.call_count, 2)

    def test_queue(self):
        topic = 'foo/bar'
        self.setup_queue_tests(topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value=[topic])
                type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([self.queue_data]))

                SUT = MQTTSubscribeDriver(**self.config_dict)

                gen = SUT.genLoopPackets()
                packet = next(gen)

                mock_time.sleep.assert_not_called()
                self.assertDictEqual(packet, self.queue_data)


class TestgenArchiveRecords(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def __init__(self, methodName):
        super(TestgenArchiveRecords, self).__init__(methodName)
        self.queue_data = {}
        self.config_dict = {}

    def setup_archive_queue_tests(self, archive_topic):
        current_time = int(time.time() + 0.5)
        in_temp = random.uniform(1, 100)
        out_temp = random.uniform(1, 100)

        self.queue_data = {
            'inTemp': in_temp,
            'outTemp': out_temp,
            'usUnits': 1,
            'dateTime': current_time
        }

        self.config_dict['archive_topic'] = archive_topic
        self.config_dict['topics'] = {}
        self.config_dict['topics']['foo/bar'] = {}
        self.config_dict['topics'][archive_topic] = {}

    @staticmethod
    def generator(test_data):
        for data in test_data:
            yield data

    def test_empty_queue(self):
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([None]))

            SUT = MQTTSubscribeDriver(**self.config_dict)
            gen = SUT.genArchiveRecords(0)
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
    unittest.main(exit=False)
