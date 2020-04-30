# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest
import mock

from collections import deque
import configobj
import copy
import datetime
import random
import string
import time

import test_weewx_stubs

from user.MQTTSubscribe import TopicManager, Logger


class TestQueueSizeCheck(unittest.TestCase):
    topic = 'foo/bar'
    config_dict = {}
    config_dict[topic] = {}
    config = configobj.ConfigObj(config_dict)

    def test_queue_max_reached(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(self.config, mock_logger)

        queue = deque()
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )  # pylint: disable=unused-variable
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        orig_queue_size = len(queue)
        max_queue = 2

        SUT._queue_size_check(queue, max_queue) # pylint: disable=protected-access
        self.assertEqual(mock_logger.error.call_count, orig_queue_size-max_queue+1)
        self.assertEqual(len(queue), max_queue-1)

    def test_queue_max_not_reached(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(self.config, mock_logger)

        queue = deque()
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )  # pylint: disable=unused-variable
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        orig_queue_size = len(queue)
        max_queue = 7

        SUT._queue_size_check(queue, max_queue) # pylint: disable=protected-access
        self.assertEqual(mock_logger.error.call_count, 0)
        self.assertEqual(len(queue), orig_queue_size)

    def test_queue_max_equal(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(self.config, mock_logger)

        queue = deque()
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )  # pylint: disable=unused-variable
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        queue.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]), )
        orig_queue_size = len(queue)
        max_queue = 4

        SUT._queue_size_check(queue, max_queue) # pylint: disable=protected-access
        self.assertEqual(mock_logger.error.call_count, orig_queue_size-max_queue+1)
        self.assertEqual(len(queue), max_queue-1)


class TestAppendData(unittest.TestCase):
    topic = 'foo/bar'
    config_dict = {}
    config_dict[topic] = {}
    config = configobj.ConfigObj(config_dict)

    def test_append_good_data(self):
        queue_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': time.time()
        }

        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(self.config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)  # pylint: disable=protected-access

        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        data = queue_element['data']
        self.assertDictEqual(data, queue_data)

    def test_append_good_data_use_server_datetime(self):
        queue_data_subset = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
        }
        queue_data = copy.deepcopy(queue_data_subset)
        queue_data['dateTime'] = time.time()

        config = copy.deepcopy(self.config)
        config['use_server_datetime'] = True

        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)  # pylint: disable=protected-access

        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        data = queue_element['data']
        self.assertGreaterEqual(data.items(), queue_data_subset.items())
        self.assertIn('dateTime', data)
        self.assertNotEqual(queue_data['dateTime'], data['dateTime'])

    def test_missing_datetime(self):
        queue_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1
        }

        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(self.config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)  # pylint: disable=protected-access

        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        data = queue_element['data']
        self.assertGreaterEqual(data.items(), queue_data.items())
        self.assertIn('dateTime', data)

    def test_missing_units(self):
        queue_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'dateTime': time.time()
        }

        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(self.config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)  # pylint: disable=protected-access

        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        data = queue_element['data']
        self.assertGreaterEqual(data.items(), queue_data.items())
        self.assertIn('usUnits', data)

    def test_dateteime_format_add_offset(self):
        # pylint: disable=too-many-locals
        queue_data_subset = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
        }
        queue_data = copy.deepcopy(queue_data_subset)

        datetime_format = "%Y-%m-%d %H:%M:%S"
        offset_format = "hhmm"

        current_epoch = int(time.time())
        offset_hour = random.randint(1, 23)
        offset_minute = random.randint(1, 59)
        offset_hour_str = str(offset_hour).rjust(2, '0')
        offset_minute_str = str(offset_minute).rjust(2, '0')
        offset_str = "%s%s" % (offset_hour_str, offset_minute_str)

        current_datetime = datetime.datetime.fromtimestamp(current_epoch).strftime(datetime_format)

        queue_data['dateTime'] = "%s+%s" % (current_datetime, offset_str)

        adjusted_epoch = current_epoch + (offset_hour * 60 + offset_minute) * 60

        config = copy.deepcopy(self.config)
        config['datetime_format'] = datetime_format
        config['offset_format'] = offset_format

        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)  # pylint: disable=protected-access

        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        data = queue_element['data']
        self.assertGreaterEqual(data.items(), queue_data_subset.items())
        self.assertIn('dateTime', data)
        self.assertEqual(adjusted_epoch, data['dateTime'])

    def test_dateteime_format_subtract_offset(self):
        # pylint: disable=too-many-locals
        queue_data_subset = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
        }
        queue_data = copy.deepcopy(queue_data_subset)

        datetime_format = "%B %d %Y %H:%M:%S"
        offset_format = "hh:mm"

        current_epoch = int(time.time())
        offset_hour = random.randint(1, 23)
        offset_minute = random.randint(1, 59)
        offset_hour_str = str(offset_hour).rjust(2, '0')
        offset_minute_str = str(offset_minute).rjust(2, '0')
        offset_str = "%s:%s" % (offset_hour_str, offset_minute_str)

        current_datetime = datetime.datetime.fromtimestamp(current_epoch).strftime(datetime_format)

        queue_data['dateTime'] = "%s -%s" % (current_datetime, offset_str)

        adjusted_epoch = current_epoch - (offset_hour * 60 + offset_minute) * 60

        config = copy.deepcopy(self.config)
        config['datetime_format'] = datetime_format
        config['offset_format'] = offset_format

        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)  # pylint: disable=protected-access

        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        data = queue_element['data']
        self.assertGreaterEqual(data.items(), queue_data_subset.items())
        self.assertIn('dateTime', data)
        self.assertEqual(adjusted_epoch, data['dateTime'])

    def test_dateteime_format_no_offset(self):
        queue_data_subset = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
        }
        queue_data = copy.deepcopy(queue_data_subset)

        datetime_format = "%Y-%m-%d %H:%M:%S"

        current_epoch = int(time.time())

        current_datetime = datetime.datetime.fromtimestamp(current_epoch).strftime(datetime_format)

        queue_data['dateTime'] = current_datetime

        adjusted_epoch = current_epoch

        config = copy.deepcopy(self.config)
        config['datetime_format'] = datetime_format

        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)  # pylint: disable=protected-access

        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        data = queue_element['data']
        self.assertGreaterEqual(data.items(), queue_data_subset.items())
        self.assertIn('dateTime', data)
        self.assertEqual(adjusted_epoch, data['dateTime'])


class TestGetQueueData(unittest.TestCase):
    topic = 'foo/bar'
    config_dict = {}
    config_dict[topic] = {}
    config = configobj.ConfigObj(config_dict)

    @staticmethod
    def create_queue_data():
        return {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': time.time()
        }

    def test_queue_empty(self):
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
            SUT = TopicManager(self.config, mock_logger)

            gen = SUT.get_data(self.topic)
            data = next(gen, None)

            self.assertIsNone(data)

    def test_queue_datetime_in_future(self):
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
            SUT = TopicManager(self.config, mock_logger)
            SUT.append_data(self.topic, self.create_queue_data())
            gen = SUT.get_data(self.topic, 0)
            data = next(gen, None)

            self.assertIsNone(data)

    def test_queue_good(self):
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
            SUT = TopicManager(self.config, mock_logger)
            elem_one = self.create_queue_data()
            elem_two = self.create_queue_data()
            elem_three = self.create_queue_data()
            SUT.append_data(self.topic, elem_one)
            SUT.append_data(self.topic, elem_two)
            SUT.append_data(self.topic, elem_three)

            elements = []
            for data in SUT.get_data(self.topic):
                elements.append(data)

            self.assertEqual(len(elements), 3)
            self.assertDictEqual(elements[0], elem_one)
            self.assertDictEqual(elements[1], elem_two)
            self.assertDictEqual(elements[2], elem_three)


class TestGetWindQueueData(unittest.TestCase):
    topic = 'foo/bar'
    config_dict = {}
    config_dict[topic] = {}
    config = configobj.ConfigObj(config_dict)

    fieldname = 'windSpeed'

    def create_queue_data(self):
        return {
            self.fieldname: random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': time.time()
        }

    def test_queue_datetime_in_future(self):
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
            SUT = TopicManager(self.config, mock_logger)
            SUT.append_data(self.topic, self.create_queue_data(), fieldname=self.fieldname)
            gen = SUT.get_data(self.topic, 0)
            data = next(gen, None)

            self.assertIsNone(data)

    def test_add_to_collector_returns_data(self):
        mock_logger = mock.Mock(spec=Logger)

        collected_data = self.create_queue_data()
        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
            type(mock_CollectData.return_value).add_data = mock.Mock(return_value=collected_data)
            SUT = TopicManager(self.config, mock_logger)
            SUT.append_data(self.topic, self.create_queue_data(), fieldname=self.fieldname)
            # ToDo - need to get the topic a better way
            # perhaps find it by searching on subscribed topic 'type'
            gen = SUT.get_data(SUT.collected_topic) 
            data = next(gen, None)

            self.assertEqual(data, collected_data)

            data = next(gen, None)
            self.assertIsNone(data)

    def test_get_from_collector_returns_data(self):
        mock_logger = mock.Mock(spec=Logger)

        collected_data = self.create_queue_data()
        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value=collected_data)
            type(mock_CollectData.return_value).add_data = mock.Mock(return_value={})
            SUT = TopicManager(self.config, mock_logger)
            SUT.append_data(self.topic, self.create_queue_data(), fieldname=self.fieldname)
            gen = SUT.get_data(self.topic)
            data = next(gen, None)

            self.assertEqual(data, collected_data)

            data = next(gen, None)
            self.assertIsNone(data)


class TestAccumulatedData(unittest.TestCase):

    topic = 'foo/bar'
    config_dict = {}
    config_dict[topic] = {}
    config = configobj.ConfigObj(config_dict)

    @staticmethod
    def create_queue_data():
        return {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': time.time()
        }

    def test_ignore_start_set(self):
        mock_logger = mock.Mock(spec=Logger)

        final_record_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': random.uniform(0, 2),
            'interval': 5,
            'dateTime': time.time()
        }

        start_ts = time.time()
        end_ts = time.time()

        config = copy.deepcopy(self.config)
        config['ignore_start_time'] = True

        with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value=False)
                mock_to_std_system.return_value = final_record_data

                SUT = TopicManager(config, mock_logger)
                SUT.append_data(self.topic, {'dateTime': start_ts})

                accumulated_data = SUT.get_accumulated_data(self.topic, 0, end_ts, 0)

                mock_Accum.assert_called_once_with(test_weewx_stubs.weeutil.weeutil.TimeSpan(start_ts, end_ts))
                self.assertDictEqual(accumulated_data, final_record_data)

    def test_ignore_end_set(self):
        mock_logger = mock.Mock(spec=Logger)

        final_record_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': random.uniform(0, 2),
            'interval': 5,
            'dateTime': time.time()
        }

        end_ts = time.time()

        config = copy.deepcopy(self.config)
        config['ignore_end_time'] = True

        with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value=False)
                mock_to_std_system.return_value = final_record_data

                SUT = TopicManager(config, mock_logger)
                SUT.append_data(self.topic, {'dateTime': end_ts})

                accumulated_data = SUT.get_accumulated_data(self.topic, 0, 0, 0)

                mock_Accum.assert_called_once_with(test_weewx_stubs.weeutil.weeutil.TimeSpan(0, end_ts))
                self.assertDictEqual(accumulated_data, final_record_data)

    def test_queue_element_before_start(self):
        mock_logger = mock.Mock(spec=Logger)
        queue_data = self.create_queue_data()

        with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                type(mock_Accum.return_value).addRecord = \
                    mock.Mock(side_effect=test_weewx_stubs.weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))

                SUT = TopicManager(self.config, mock_logger)
                SUT.append_data(self.topic, queue_data)

                mock_logger.reset_mock()
                accumulated_data = SUT.get_accumulated_data(self.topic, 0, time.time(), 0)

                self.assertDictEqual(accumulated_data, {})
                mock_logger.info.assert_called_once()
                mock_Accum.getRecord.assert_not_called()
                mock_to_std_system.assert_not_called()

    def test_queue_empty(self):
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value=True)

                SUT = TopicManager(self.config, mock_logger)

                accumulated_data = SUT.get_accumulated_data(self.topic, 0, time.time(), 0)

                self.assertDictEqual(accumulated_data, {})
                mock_Accum.assert_not_called()
                mock_Accum.addRecord.assert_not_called()
                mock_Accum.getRecord.assert_not_called()
                mock_to_std_system.assert_not_called()

    def test_queue_valid(self):
        mock_logger = mock.Mock(spec=Logger)

        final_record_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': random.uniform(0, 2),
            'interval': 5,
            'dateTime': time.time()
        }

        with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value=False)
                mock_to_std_system.return_value = final_record_data

                SUT = TopicManager(self.config, mock_logger)
                SUT.append_data(self.topic, {})

                accumulated_data = SUT.get_accumulated_data(self.topic, 0, time.time(), 0)

                self.assertDictEqual(accumulated_data, final_record_data)

if __name__ == '__main__':
    unittest.main(exit=False)
