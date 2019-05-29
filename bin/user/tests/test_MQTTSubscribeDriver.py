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

from user.MQTTSubscribe import MQTTSubscribeDriver, TopicX

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

        self.queues = []
        self.queues.append({
            'queue': deque(),
            'queue_wind': deque()
            }
        )        

    def test_queue_empty(self):
        topic = 'foo/bar'
        self.setup_queue_tests(topic)
        ##queue = deque()

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                type(mock_manager.return_value).Subscribed_topics = mock.PropertyMock(return_value = [topic])
                type(mock_manager.return_value).get_data = mock.Mock(side_effect=[None, self.queue_data])
                ##type(mock_manager.return_value).get_wind_queue = mock.Mock(return_value=deque())
                ##type(mock_manager.return_value).get_queue = mock.Mock(return_value=queue)

                SUT = MQTTSubscribeDriver(**self.config_dict)
                thread = GetLoopPacketThread(SUT)
                thread.start()

                # wait for at least one sleep cycle
                while mock_time.sleep.call_count <= 0:
                    time.sleep(1)

                ##queue.append(self.queue_data, )

                # wait for queue to be processed
                while not thread.packet:
                    time.sleep(1)

                mock_time.sleep.assert_called()
                self.assertDictEqual(thread.packet, self.queue_data)

    def test_queue(self):
        topic = 'foo/bar'
        self.setup_queue_tests(topic)
        ##queue = deque()
        ##queue.append(self.queue_data, )

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                type(mock_manager.return_value).Subscribed_topics = mock.PropertyMock(return_value = [topic])
                type(mock_manager.return_value).get_data = mock.Mock(side_effect=[self.queue_data, None])
                ##type(mock_manager.return_value).get_wind_queue = mock.Mock(return_value=deque())
                ##type(mock_manager.return_value).get_queue = mock.Mock(return_value=queue)

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

        self.queues = []
        self.queues.append({
            'queue': deque(),
            'queue_wind': deque()
            }
        )

    def test_wind_queue_empty(self):
        topic = 'foo/bar'
        self.setup_wind_queue_tests(topic)
        ##wind_queue = deque()

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                    type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
                    type(mock_CollectData.return_value).add_data = mock.Mock(return_value=self.aggregate_data)
                    type(mock_manager.return_value).Subscribed_topics = mock.PropertyMock(return_value = [topic])
                    type(mock_manager.return_value).get_data = mock.Mock(side_effect=[None, self.queue_data])
                    ##type(mock_manager.return_value).get_queue = mock.Mock(return_value=deque())
                    ##type(mock_manager.return_value).get_wind_queue = mock.Mock(return_value=wind_queue)
                    SUT = MQTTSubscribeDriver(**self.config_dict)
                    thread = GetLoopPacketThread(SUT)
                    thread.start()

                    # wait for at least one sleep cycle
                    while mock_time.sleep.call_count <= 0:
                        time.sleep(1)

                    ##wind_queue.append(self.queue_data, )

                    # wait for queue to be processed
                    while not thread.packet:
                        time.sleep(1)

                    mock_time.sleep.assert_called()
                    self.assertDictEqual(thread.packet, self.queue_data)

    def test_wind_queue(self):
        topic = 'foo/bar'
        self.setup_wind_queue_tests(topic)
        ##wind_queue = deque()
        ##wind_queue.append(self.queue_data, )

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                    type(mock_manager.return_value).Subscribed_topics = mock.PropertyMock(return_value = [topic])
                    type(mock_manager.return_value).get_data = mock.Mock(side_effect=[self.queue_data, None])
                    ##type(mock_manager.return_value).get_queue = mock.Mock(return_value=deque())
                    ##type(mock_manager.return_value).get_wind_queue = mock.Mock(return_value=wind_queue)
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

        self.queues = []
        self.queues.append({
            'queue': deque(),
            'queue_wind': deque()
            }
        )

    def test_empty_queue(self):
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)
        archive_queue = deque()

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            type(mock_manager.return_value).get_queue = mock.Mock(return_value=archive_queue)
            type(mock_manager.return_value).get_data = mock.Mock(side_effect=[None])
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
        ##archive_queue = deque()
        ##archive_queue.append(self.queue_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            ##type(mock_manager.return_value).get_queue = mock.Mock(return_value=archive_queue)
            type(mock_manager.return_value).get_data = mock.Mock(side_effect=[None])

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
        queue_list = [self.queue_data, self.queue_data]
        ##archive_queue = deque()
        ##for q in queue_list:
        ##    archive_queue.append(q)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            ##type(mock_manager.return_value).get_queue = mock.Mock(return_value=archive_queue)
            type(mock_manager.return_value).get_data = mock.Mock(side_effect=[self.queue_data, self.queue_data, None])
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