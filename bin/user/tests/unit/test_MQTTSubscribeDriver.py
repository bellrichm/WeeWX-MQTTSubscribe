#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import unittest
import mock

import random
import sys
import time

import test_weewx_stubs
from test_weewx_stubs import random_string
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import MQTTSubscribeDriver

class TestclosePort(unittest.TestCase):
    def setUp(self):
        # reset stubs for every test
        test_weewx_stubs.setup_stubs()

    def tearDown(self):
        # cleanup stubs
        del sys.modules['weecfg']
        del sys.modules['weeutil']
        del sys.modules['weeutil.config']
        del sys.modules['weeutil.weeutil']
        del sys.modules['weeutil.logger']
        del sys.modules['weewx']
        del sys.modules['weewx.drivers']
        del sys.modules['weewx.engine']

    @staticmethod
    def test_close_port():
        mock_engine = mock.Mock()
        stn_dict = {}
        stn_dict['topic'] = random_string()
        config_dict = {}
        config_dict['MQTTSubscribeDriver'] = stn_dict

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber'):
            SUT = MQTTSubscribeDriver(config_dict, mock_engine)
            SUT.closePort()
            SUT.subscriber.disconnect.assert_called_once()

class TestArchiveInterval(unittest.TestCase):
    def setUp(self):
        # reset stubs for every test
        test_weewx_stubs.setup_stubs()

    def tearDown(self):
        # cleanup stubs
        del sys.modules['weecfg']
        del sys.modules['weeutil']
        del sys.modules['weeutil.config']
        del sys.modules['weeutil.weeutil']
        del sys.modules['weeutil.logger']
        del sys.modules['weewx']
        del sys.modules['weewx.drivers']
        del sys.modules['weewx.engine']

    def test_no_archive_topic(self):
        mock_engine = mock.Mock()
        stn_dict = {}
        stn_dict['topic'] = random_string()
        config_dict = {}
        config_dict['MQTTSubscribeDriver'] = stn_dict

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber'):
            with self.assertRaises(NotImplementedError) as error:
                SUT = MQTTSubscribeDriver(config_dict, mock_engine)
                SUT.archive_interval

            self.assertEqual(len(error.exception.args), 0)

    def test_archive_topic(self):
        mock_engine = mock.Mock()
        topic = random_string()
        default_archive_interval = 900
        stn_dict = {}
        stn_dict['topic'] = topic
        stn_dict['archive_topic'] = topic
        stn_dict['archive_interval'] = 900
        config_dict = {}
        config_dict['MQTTSubscribeDriver'] = stn_dict

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber'):
            SUT = MQTTSubscribeDriver(config_dict, mock_engine)
            archive_interval = SUT.archive_interval
            self.assertEqual(archive_interval, default_archive_interval)

class TestgenLoopPackets(unittest.TestCase):
    mock_StdEngine = mock.Mock()

    def setUp(self):
        # reset stubs for every test
        test_weewx_stubs.setup_stubs()

    def tearDown(self):
        # cleanup stubs
        del sys.modules['weecfg']
        del sys.modules['weeutil']
        del sys.modules['weeutil.config']
        del sys.modules['weeutil.weeutil']
        del sys.modules['weeutil.logger']
        del sys.modules['weewx']
        del sys.modules['weewx.drivers']
        del sys.modules['weewx.engine']

    @classmethod
    def setUpClass(cls):
        cls.queue_data = {}
        stn_dict = {}
        cls.config_dict = {}
        cls.config_dict['MQTTSubscribeDriver'] = stn_dict

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

        self.config_dict['MQTTSubscribeDriver']['topic'] = topic

    @staticmethod
    def generator(test_data):
        for data in test_data:
            yield data

    @staticmethod
    def empty_generator():
        return
        yield  # needed to make this a generator

    def test_queue_empty(self):
        mock_engine = mock.Mock()
        topic = random_string()
        self.setup_queue_tests(topic)
        queue = dict(
            {'name': topic}
        )

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_manager_class:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_manager = mock.Mock()
                mock_manager_class.get_subscriber = mock_manager
                type(mock_manager.return_value).queues = mock.PropertyMock(return_value=[queue])
                type(mock_manager.return_value).get_data = mock.Mock(side_effect=[self.empty_generator(), self.generator([self.queue_data])])

                SUT = MQTTSubscribeDriver(self.config_dict, mock_engine)
                gen = SUT.genLoopPackets()
                next(gen, None)

                mock_time.sleep.assert_called_once()
                self.assertEqual(mock_manager.return_value.get_data.call_count, 2)

    def test_queue_returns_none(self):
        mock_engine = mock.Mock()
        topic = random_string()
        self.setup_queue_tests(topic)
        queue = dict(
            {'name': topic}
        )

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_manager_class:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_manager = mock.Mock()
                mock_manager_class.get_subscriber = mock_manager
                type(mock_manager.return_value).queues = mock.PropertyMock(return_value=[queue])
                type(mock_manager.return_value).get_data = mock.Mock(side_effect=[self.generator([None]), self.generator([self.queue_data])])

                SUT = MQTTSubscribeDriver(self.config_dict, mock_engine)
                gen = SUT.genLoopPackets()
                next(gen, None)

                mock_time.sleep.assert_called_once()
                self.assertEqual(mock_manager.return_value.get_data.call_count, 2)

    def test_topic_is_archive_topic(self):
        """ This is a big hack to attempt to test the following in genLoopPackets
                if topic == self.archive_topic:
                    continue
        """

        mock_engine = mock.Mock()
        topic = random_string()

        stn_dict = {}
        stn_dict['topic'] = topic
        stn_dict['archive_topic'] = topic
        config_dict = {}
        config_dict['MQTTSubscribeDriver'] = stn_dict

        packet = None

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_manager:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value=[topic])
                mock_time.sleep.side_effect = mock.Mock(side_effect=SystemExit())  # Hack one, use this to escape the infinit loop
                with self.assertRaises(SystemExit):
                    SUT = MQTTSubscribeDriver(config_dict, mock_engine)

                    gen = SUT.genLoopPackets()
                    packet = next(gen)

                mock_time.sleep.assert_called_once()
                self.assertIsNone(packet)  # hack two, the generator never really returns because of the side effect exception

    def test_queue(self):
        mock_engine = mock.Mock()
        topic = random_string()
        self.setup_queue_tests(topic)
        queue = dict(
            {'name': topic}
        )

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_manager_class:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_manager = mock.Mock()
                mock_manager_class.get_subscriber = mock_manager
                type(mock_manager.return_value).queues = mock.PropertyMock(return_value=[queue])
                type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([self.queue_data]))

                SUT = MQTTSubscribeDriver(self.config_dict, mock_engine)

                gen = SUT.genLoopPackets()
                packet = next(gen)

                mock_time.sleep.assert_not_called()
                self.assertDictEqual(packet, self.queue_data)

class TestgenArchiveRecords(unittest.TestCase):
    mock_StdEngine = mock.Mock()

    def setUp(self):
        # reset stubs for every test
        test_weewx_stubs.setup_stubs()

    def tearDown(self):
        # cleanup stubs
        del sys.modules['weecfg']
        del sys.modules['weeutil']
        del sys.modules['weeutil.config']
        del sys.modules['weeutil.weeutil']
        del sys.modules['weeutil.logger']
        del sys.modules['weewx']
        del sys.modules['weewx.drivers']
        del sys.modules['weewx.engine']

    @classmethod
    def setUpClass(cls):
        cls.queue_data = {}
        stn_dict = {}
        cls.config_dict = {}
        cls.config_dict['MQTTSubscribeDriver'] = stn_dict

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

        self.config_dict['MQTTSubscribeDriver']['archive_topic'] = archive_topic
        self.config_dict['MQTTSubscribeDriver']['topics'] = {}
        self.config_dict['MQTTSubscribeDriver']['topics'][random_string()] = {}
        self.config_dict['MQTTSubscribeDriver']['topics'][archive_topic] = {}

    @staticmethod
    def generator(test_data):
        for data in test_data:
            yield data

    @staticmethod
    def empty_generator():
        return
        yield  # needed to make this a generator

    def test_empty_queue(self):
        mock_engine = mock.Mock()
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_manager:
            type(mock_manager.return_value).get_data = mock.Mock(return_value=self.empty_generator())

            SUT = MQTTSubscribeDriver(self.config_dict, mock_engine)
            gen = SUT.genArchiveRecords(0)
            data = next(gen, None)

            self.assertIsNone(data)

    def test_queuereturns_none(self):
        mock_engine = mock.Mock()
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_manager:
            type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([None]))

            SUT = MQTTSubscribeDriver(self.config_dict, mock_engine)
            gen = SUT.genArchiveRecords(0)
            data = next(gen, None)

            self.assertIsNone(data)

    def test_archive_topic_not_set(self):
        mock_engine = mock.Mock()
        stn_dict = {}
        stn_dict['topics'] = {}
        config_dict = {}
        config_dict['MQTTSubscribeDriver'] = stn_dict

        records = []

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber'):
            with self.assertRaises(NotImplementedError) as error:
                SUT = MQTTSubscribeDriver(config_dict, mock_engine)

                for record in SUT.genArchiveRecords(int(time.time() + 10.5)):
                    records.append(record)

            self.assertEqual(len(error.exception.args), 0)

    def test_queue(self):
        mock_engine = mock.Mock()
        archive_topic = 'archive'
        self.setup_archive_queue_tests(archive_topic)
        queue_list = [self.queue_data, self.queue_data]
        queue = dict(
            {'name': archive_topic}
        )

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_manager_class:
            mock_manager = mock.Mock()
            mock_manager_class.get_subscriber = mock_manager
            type(mock_manager.return_value).queues = mock.PropertyMock(return_value=[queue])
            type(mock_manager.return_value).get_data = mock.Mock(return_value=self.generator([self.queue_data, self.queue_data, None]))
            records = []

            SUT = MQTTSubscribeDriver(self.config_dict, mock_engine)

            for record in SUT.genArchiveRecords(int(time.time() - 10.5)):
                records.append(record)

            self.assertListEqual(records, queue_list)

if __name__ == '__main__':
    unittest.main(exit=False)
