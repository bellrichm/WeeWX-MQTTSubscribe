from __future__ import with_statement

import unittest
import mock

from collections import deque
import random
import time
import threading
import weewx

from user.MQTTSubscribe import MQTTSubscribeDriver

class GetLoopPacketThread(threading.Thread):
    def __init__(self, driver):
        threading.Thread.__init__(self)
        self.driver = driver
        self.packet = None

    def run(self):
        gen=self.driver.genLoopPackets()
        while not self.packet:
            self.packet=next(gen)

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

        self.topics = {}
        self.topics[topic] = {}
        self.topics[topic]['queue'] = deque()
        self.topics[topic]['queue'].append(self.queue_data, )
        self.topics[topic]['queue_wind'] = deque()

    def test_queue_empty(self):
        topic = 'foo/bar'
        self.setup_queue_tests(topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                SUT = MQTTSubscribeDriver(**self.config_dict)
                thread = GetLoopPacketThread(SUT)
                thread.start()

                # wait for at least one sleep cycle
                while mock_time.sleep.call_count <= 0:
                    time.sleep(1)

                type(mock_manager.return_value).topics = mock.PropertyMock(return_value = self.topics)

                # wait for queue to be processed
                while not thread.packet:
                    time.sleep(1)

                mock_time.sleep.assert_called()
                self.assertDictEqual(thread.packet, self.queue_data)

    def test_queue(self):
        topic = 'foo/bar'
        self.setup_queue_tests(topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                type(mock_manager.return_value).topics = mock.PropertyMock(return_value = self.topics)

                SUT = MQTTSubscribeDriver(**self.config_dict)

                gen=SUT.genLoopPackets()
                packet=next(gen)

                mock_time.sleep.assert_not_called()
                self.assertDictEqual(packet, self.queue_data)

    def setup_wind_queue_tests(self, topic):

        self.queue_data = {
            'windSpeed': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }

        self.aggregate_data = dict(self.queue_data)

        self.config_dict = {}
        self.config_dict['topic'] = topic

        self.topics = {}
        self.topics[topic] = {}
        self.topics[topic]['queue'] = deque()
        self.topics[topic]['queue_wind'] = deque()
        self.topics[topic]['queue_wind'].append(self.queue_data, )

    def test_wind_queue_empty(self):
        topic = 'foo/bar'
        self.setup_wind_queue_tests(topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                    type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
                    type(mock_CollectData.return_value).add_data = mock.Mock(return_value=self.aggregate_data)
                    SUT = MQTTSubscribeDriver(**self.config_dict)
                    thread = GetLoopPacketThread(SUT)
                    thread.start()

                    # wait for at least one sleep cycle
                    while mock_time.sleep.call_count <= 0:
                        time.sleep(1)

                    type(mock_manager.return_value).topics = mock.PropertyMock(return_value = self.topics)

                    # wait for queue to be processed
                    while not thread.packet:
                        time.sleep(1)

                    mock_time.sleep.assert_called()
                    self.assertDictEqual(thread.packet, self.queue_data)

    def test_wind_queue(self):
        topic = 'foo/bar'
        self.setup_wind_queue_tests(topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                    type(mock_manager.return_value).topics = mock.PropertyMock(return_value = self.topics)
                    type(mock_CollectData.return_value).add_data = mock.Mock(return_value=self.aggregate_data)
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

        self.topics = {}
        self.topics[archive_topic] = {}
        self.topics[archive_topic]['queue'] = deque()
        self.topics[archive_topic]['queue'].append(self.queue_data, )
        self.topics[archive_topic]['queue_wind'] = deque()

    def test_empty_queue(self):
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            SUT = MQTTSubscribeDriver(**self.config_dict)
            record = None

            gen=SUT.genArchiveRecords(0)
            try:
                record=next(gen)
            except StopIteration:
                pass

            self.assertIsNone(record)

    def test_queue_element_in_future(self):
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            type(mock_manager.return_value).topics = mock.PropertyMock(return_value = self.topics)

            SUT = MQTTSubscribeDriver(**self.config_dict)
            record = None

            gen=SUT.genArchiveRecords(0)
            try:
                record=next(gen)
            except StopIteration:
                pass

            self.assertIsNone(record)

    def test_queue(self):
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)
        # ToDo - cleanup
        self.topics[archive_topic]['queue'] = deque()
        queue_list = [self.queue_data, self.queue_data]
        for q in queue_list:
            self.topics[archive_topic]['queue'].append(q)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            type(mock_manager.return_value).topics = mock.PropertyMock(return_value = self.topics)
            records = list()

            SUT = MQTTSubscribeDriver(**self.config_dict)

            gen=SUT.genArchiveRecords(int(time.time() + 10.5))
            try:
                while True:
                    records.append(next(gen))
            except StopIteration:
                pass

            self.assertListEqual(records, queue_list)


if __name__ == '__main__':
    unittest.main()