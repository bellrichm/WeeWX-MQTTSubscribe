

# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# need to be python 2 compatible pylint: disable=bad-option-value, super-with-arguments
# pylint: enable=bad-option-value

from __future__ import with_statement

import unittest
import mock

import configobj
import copy
import random
import time

import test_weewx_stubs
from test_weewx_stubs import random_string

import user.MQTTSubscribe

class atestInitialization(unittest.TestCase):
    def test_invalid_binding(self):
        mock_StdEngine = mock.Mock()

        binding = random_string()
        config_dict = {
            'MQTTSubscribeService': {
                'binding': binding
            }
        }

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber'):
            with self.assertRaises(ValueError) as error:
                user.MQTTSubscribe.MQTTSubscribeService(mock_StdEngine, config_dict)

            self.assertEqual(error.exception.args[0], "MQTTSubscribeService: Unknown binding: %s" % binding)

    @staticmethod
    def test_not_enable():
        mock_StdEngine = mock.Mock()

        config_dict = {
            'MQTTSubscribeService': {
                'enable': False
            }
        }

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber'):
            with mock.patch('user.MQTTSubscribe.Logger'):
                # pylint: disable=no-member
                SUT = user.MQTTSubscribe.MQTTSubscribeService(mock_StdEngine, config_dict)
                SUT.logger.info.assert_called_once()
                SUT.logger.info.assert_called_once_with("Not enabled, exiting.")

    def test_runing_as_service_and_driver_check(self):
        mock_StdEngine = mock.Mock()
        mock_StdEngine.stn_info.hardware = 'MQTTSubscribeDriver'

        config_dict = {
            'StdArchive': { 'record_generation': 'software'},
            'MQTTSubscribeService': {}
        }

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber'):
            with mock.patch('user.MQTTSubscribe.Logger'):
                # pylint: disable=no-member
                SUT = user.MQTTSubscribe.MQTTSubscribeService(mock_StdEngine, config_dict)
                self.assertEqual(SUT.logger.info.call_count, 2)
                SUT.logger.info.assert_any_call('Running as both a driver and a service.')

    def test_archive_topic_specified(self):
        mock_StdEngine = mock.Mock()
        #mock_StdEngine.stn_info.hardware = 'MQTTSubscribeDriver'
        archive_topic = random_string()

        config_dict = {
            'MQTTSubscribeService': {
                'archive_topic': archive_topic
            }
        }

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber'):
            with mock.patch('user.MQTTSubscribe.Logger'):
                with self.assertRaises(ValueError) as error:
                    user.MQTTSubscribe.MQTTSubscribeService(mock_StdEngine, config_dict)

            self.assertEqual(error.exception.args[0], "archive_topic, %s, is invalid when running as a service" % archive_topic)

class Testnew_loop_packet(unittest.TestCase):
    mock_StdEngine = mock.Mock()

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
            'outTemp': out_temp,
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
        self.config_dict['MQTTSubscribeService']['topic'] = random_string()

    @staticmethod
    def generator(test_data):
        for data in test_data:
            yield data

    def test_queue_valid(self):
        topic = random_string()
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_queue_tests(start_ts, end_period_ts)
        self.final_packet_data.update(self.target_data)
        queue = dict(
            {'name': topic}
            )

        new_loop_packet_event = test_weewx_stubs.Event(test_weewx_stubs.NEW_LOOP_PACKET,
                                                       packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_MQTTSubscribe:
            type(mock_MQTTSubscribe.return_value).queues = mock.PropertyMock(return_value=[queue])
            type(mock_MQTTSubscribe.return_value).get_accumulated_data = mock.Mock(return_value=self.target_data)
            type(mock_MQTTSubscribe.return_value).cached_fields = mock.PropertyMock(return_value=None)

            SUT = user.MQTTSubscribe.MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
            SUT.end_ts = start_ts

            SUT.new_loop_packet(new_loop_packet_event)

            self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)

            SUT.shutDown()

    def test_packet_is_in_past(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_queue_tests(start_ts, end_period_ts)
        self.final_packet_data.update(self.target_data)

        new_loop_packet_event = test_weewx_stubs.Event(test_weewx_stubs.NEW_LOOP_PACKET,
                                                       packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_MQTTSubscribe:
            with mock.patch('user.MQTTSubscribe.Logger'):
                # pylint: disable=no-member
                type(mock_MQTTSubscribe.return_value).get_accumulated_data = mock.Mock(return_value=self.target_data)
                type(mock_MQTTSubscribe.return_value).cached_fields = mock.PropertyMock(return_value=None)

                SUT = user.MQTTSubscribe.MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                SUT.end_ts = end_period_ts + 10

                SUT.new_loop_packet(new_loop_packet_event)

                SUT.logger.error.assert_called_once()

                SUT.shutDown()


class Testnew_archive_record(unittest.TestCase):
    def __init__(self, methodName):
        super(Testnew_archive_record, self).__init__(methodName)
        self.mock_StdEngine = mock.Mock()
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
            'outTemp': out_temp,
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
        self.config_dict['MQTTSubscribeService']['binding'] = 'archive'

    @staticmethod
    def generator(test_data):
        for data in test_data:
            yield data

    def test_queue_valid(self):
        topic = random_string()
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_archive_queue_tests(start_ts, end_period_ts, topic)
        self.final_record_data.update(self.target_data)
        queue = dict(
            {'name': topic}
        )

        new_loop_record_event = test_weewx_stubs.Event(test_weewx_stubs.NEW_ARCHIVE_RECORD,
                                                       record=self.record_data,
                                                       origin='hardware')

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_manager:
            type(mock_manager.return_value).queues = mock.PropertyMock(return_value=[queue])
            type(mock_manager.return_value).get_accumulated_data = mock.Mock(return_value=self.target_data)

            SUT = user.MQTTSubscribe.MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
            SUT.end_ts = start_ts

            SUT.new_archive_record(new_loop_record_event)

            self.assertDictEqual(new_loop_record_event.record, self.final_record_data)

        SUT.shutDown()

    def test_field_missing(self):
        unit_system = random.randint(1, 10)
        fieldname = random_string()
        config_dict = {}
        config_dict['StdArchive'] = { 'record_generation': 'software'}
        config_dict['MQTTSubscribeService'] = {}

        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_MQTTSubscribe:
            with mock.patch('user.MQTTSubscribe.RecordCache') as mock_cache:
                type(mock_MQTTSubscribe.return_value).cached_fields = \
                    mock.PropertyMock(return_value={fieldname:{'expires_after':random.randint(1, 10)}})
                value = round(random.uniform(10, 100), 2)
                type(mock_cache.return_value).get_value = mock.Mock(return_value=value)
                # pylint: disable=no-member
                SUT = user.MQTTSubscribe.MQTTSubscribeService(self.mock_StdEngine, config)

                record = {
                    'usUnits': unit_system,
                    'dateTime': time.time()
                }

                event = test_weewx_stubs.Event(test_weewx_stubs.NEW_ARCHIVE_RECORD, record=record)

                updated_record = copy.deepcopy(record)
                updated_record.update({fieldname: value})

                SUT.new_archive_record(event)
                SUT.cache.get_value.assert_called_once()
                self.assertEqual(record, updated_record)

    @staticmethod
    def test_field_exists():
        mock_StdEngine = mock.Mock()
        unit_system = random.randint(1, 10)
        fieldname = random_string()
        config_dict = {}
        config_dict['StdArchive'] = { 'record_generation': 'software'}
        config_dict['MQTTSubscribeService'] = {}

        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.MQTTSubscriber') as mock_MQTTSubscribe:
            with mock.patch('user.MQTTSubscribe.RecordCache'):
                # pylint: disable=no-member
                type(mock_MQTTSubscribe.return_value).cached_fields = mock.PropertyMock(return_value={fieldname:{}})
                SUT = user.MQTTSubscribe.MQTTSubscribeService(mock_StdEngine, config)

                record = {
                    'usUnits': unit_system,
                    'dateTime': time.time(),
                    fieldname: round(random.uniform(1, 100), 2)
                }

                event = test_weewx_stubs.Event(test_weewx_stubs.NEW_ARCHIVE_RECORD, record=record)

                SUT.new_archive_record(event)
                SUT.cache.update_value.assert_called_once()

if __name__ == '__main__':
    unittest.main(exit=False)
