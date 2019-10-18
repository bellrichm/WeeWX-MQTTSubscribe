# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest
import mock

import random
import time
import weewx

from user.MQTTSubscribe import MQTTSubscribeService

class Testnew_loop_packet(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def __init__(self, methodName):
        super(Testnew_loop_packet, self).__init__(methodName)
        self.queue_data = {}
        self.aggregate_data = {}
        self.packet_data = {}
        self.final_packet_data = {}
        self.target_data = {}
        self.config_dict = {}

    def setup_queue_tests(self, start_ts, end_period_ts):
        in_temp = random.uniform(1, 100)
        out_temp = random.uniform(1, 100)

        self.queue_data = {
            'inTemp': in_temp,
            'outTemp':out_temp,
            'usUnits': 1,
            'dateTime': start_ts
        }

        self.aggregate_data = dict(self.queue_data)

        self.packet_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        self.final_packet_data = dict(self.packet_data)

        self.target_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': self.packet_data['usUnits'],
            'interval': self.packet_data['interval'],
            'dateTime': self.packet_data['dateTime']
        }

        self.config_dict['MQTTSubscribeService'] = {}
        self.config_dict['MQTTSubscribeService']['topic'] = 'foo/bar'

    def generator(self, test_data):
        for data in test_data:
            yield data

    def test_queue_valid(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_queue_tests(start_ts, end_period_ts)
        self.final_packet_data.update(self.target_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                            packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value=[topic])
            type(mock_manager.return_value).get_accumulated_data = mock.Mock(return_value=self.target_data)

            SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
            SUT.end_ts = start_ts

            SUT.new_loop_packet(new_loop_packet_event)

            self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)

            SUT.shutDown()

    def test_packet_is_in_past(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_queue_tests(start_ts, end_period_ts)
        self.final_packet_data.update(self.target_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                            packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.Logger'):
                # pylint: disable=no-member
                type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value=[topic])
                type(mock_manager.return_value).get_accumulated_data = mock.Mock(return_value=self.target_data)

                SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                SUT.end_ts = end_period_ts + 10

                SUT.new_loop_packet(new_loop_packet_event)

                SUT.logger.logerr.assert_called_once()

                SUT.shutDown()

class Testnew_archive_record(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def __init__(self, methodName):
        super(Testnew_archive_record, self).__init__(methodName)
        self.queue_data = {}
        self.aggregate_data = {}
        self.record_data = {}
        self.target_data = {}
        self.final_record_data = {}
        self.config_dict = {}

    def setup_archive_queue_tests(self, start_ts, end_period_ts, topic):
        in_temp = random.uniform(1, 100)
        out_temp = random.uniform(1, 100)

        self.queue_data = {
            'inTemp': in_temp,
            'outTemp':out_temp,
            'usUnits': 1,
            'dateTime': start_ts
        }

        self.aggregate_data = dict(self.queue_data)

        self.record_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        self.target_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': self.record_data['usUnits'],
            'interval': self.record_data['interval'],
            'dateTime': self.record_data['dateTime']
        }

        self.final_record_data = dict(self.record_data)

        self.config_dict['MQTTSubscribeService'] = {}
        self.config_dict['MQTTSubscribeService']['topic'] = topic

    def generator(self, test_data):
        for data in test_data:
            yield data

    def test_queue_valid(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_archive_queue_tests(start_ts, end_period_ts, topic)
        self.final_record_data.update(self.target_data)

        new_loop_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                            record=self.record_data,
                                            origin='hardware')

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            type(mock_manager.return_value).subscribed_topics = mock.PropertyMock(return_value=[topic])
            type(mock_manager.return_value).get_accumulated_data = mock.Mock(return_value=self.target_data)

            SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
            SUT.end_ts = start_ts

            SUT.new_archive_record(new_loop_record_event)

            self.assertDictEqual(new_loop_record_event.record, self.final_record_data)

        SUT.shutDown()

if __name__ == '__main__':
    unittest.main()
