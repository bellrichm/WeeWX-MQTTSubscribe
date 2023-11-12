#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import unittest
import mock

from collections import deque
import configobj
import copy
import datetime
import random
import time

import test_weewx_stubs
from test_weewx_stubs import random_string

from user.MQTTSubscribe import TopicManager, Logger

class TestInit(unittest.TestCase):
    def test_missing_topic(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            TopicManager(None, config, mock_logger)

        self.assertEqual(error.exception.args[0], "At least one topic must be configured.")

    def test_invalid_unit_system_default(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}

        topic = random_string()
        unit_system_name = random_string()
        config_dict[topic] = {}
        config_dict['unit_system'] = unit_system_name

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            TopicManager(None, config, mock_logger)

        self.assertEqual(error.exception.args[0], f"MQTTSubscribe: Unknown unit system: {unit_system_name.upper()}")

    def test_invalid_unit_system_topic(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}

        topic = random_string()
        unit_system_name = random_string()
        config_dict[topic] = {}
        config_dict[topic]['unit_system'] = unit_system_name

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            TopicManager(None, config, mock_logger)

        self.assertEqual(error.exception.args[0], f"MQTTSubscribe: Unknown unit system: {unit_system_name.upper()}")

    def test_invalid_units(self):
        mock_logger = mock.Mock(spec=Logger)

        config_dict = {}

        topic = random_string()
        field = random_string()
        config_dict[topic] = {}
        config_dict[topic][field] = {}
        config_dict[topic][field]['units'] = random_string()
        field_dict = {}
        field_dict['name'] = field
        field_dict['use_topic_as_field_name'] = False
        field_dict['ignore'] = False
        field_dict['contains_total'] = False
        field_dict['conversion_type'] = 'float'

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            TopicManager(None, config, mock_logger)

        self.assertEqual(error.exception.args[0], f"For {field} invalid units, {config_dict[topic][field]['units']}.")

class TestConfigureMessage(unittest.TestCase):
    def test_default_message_configuration(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()

        config_dict = {}
        config_dict['message'] = {}
        config_dict['message']['type'] = random_string(10)
        config_dict['message']['flatten_delimiter'] = random_string(5)
        config_dict['message']['keyword_delimiter'] = random_string(5)
        config_dict['message']['keyword_separator'] = random_string(5)
        config_dict[topic] = {}

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertIn(SUT.message_config_name, SUT.subscribed_topics[topic])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['type'],
                         config_dict['message']['type'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['flatten_delimiter'],
                         config_dict['message']['flatten_delimiter'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['keyword_delimiter'],
                         config_dict['message']['keyword_delimiter'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['keyword_separator'],
                         config_dict['message']['keyword_separator'])

    def test_override_default(self):
        mock_logger = mock.Mock(spec=Logger)
        topic = random_string()
        config_key = random_string(10)

        config_dict = {}
        config_dict['message'] = {}
        config_dict['message']['type'] = random_string(10)
        config_dict['message']['flatten_delimiter'] = random_string(5)
        config_dict['message']['keyword_delimiter'] = random_string(5)
        config_dict['message']['keyword_separator'] = random_string(5)
        config_dict['message'][config_key] = random_string()

        config_dict[topic] = {}
        config_dict[topic]['message'] = {}
        config_dict[topic]['message']['type'] = random_string(10)
        config_dict[topic]['message']['flatten_delimiter'] = random_string(5)
        config_dict[topic]['message']['keyword_delimiter'] = random_string(5)
        config_dict[topic]['message']['keyword_separator'] = random_string(5)

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertIn(SUT.message_config_name, SUT.subscribed_topics[topic])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['type'],
                         config_dict[topic]['message']['type'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['flatten_delimiter'],
                         config_dict[topic]['message']['flatten_delimiter'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['keyword_delimiter'],
                         config_dict[topic]['message']['keyword_delimiter'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['keyword_separator'],
                         config_dict[topic]['message']['keyword_separator'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name][config_key],
                         config_dict['message'][config_key])

    def test_no_default_setting(self):
        mock_logger = mock.Mock(spec=Logger)
        topic = random_string()
        config_key = random_string(10)

        config_dict = {}
        config_dict['message'] = {}
        config_dict['message']['type'] = random_string(10)
        config_dict['message']['flatten_delimiter'] = random_string(5)
        config_dict['message']['keyword_delimiter'] = random_string(5)
        config_dict['message']['keyword_separator'] = random_string(5)

        config_dict[topic] = {}
        config_dict[topic]['message'] = {}
        config_dict[topic]['message']['type'] = random_string(10)
        config_dict[topic]['message']['flatten_delimiter'] = random_string(5)
        config_dict[topic]['message']['keyword_delimiter'] = random_string(5)
        config_dict[topic]['message']['keyword_separator'] = random_string(5)
        config_dict[topic]['message'][config_key] = random_string()

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertIn(SUT.message_config_name, SUT.subscribed_topics[topic])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['type'],
                         config_dict[topic]['message']['type'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['flatten_delimiter'],
                         config_dict[topic]['message']['flatten_delimiter'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['keyword_delimiter'],
                         config_dict[topic]['message']['keyword_delimiter'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name]['keyword_separator'],
                         config_dict[topic]['message']['keyword_separator'])
        self.assertEqual(SUT.subscribed_topics[topic][SUT.message_config_name][config_key],
                         config_dict[topic]['message'][config_key])

    def test_topic_named_message(self):
        mock_logger = mock.Mock(spec=Logger)
        topic = random_string()

        config_dict = {}
        config_dict['message'] = {}
        config_dict['message']['flatten_delimiter'] = random_string(5)
        config_dict['message']['keyword_delimiter'] = random_string(5)
        config_dict['message']['keyword_separator'] = random_string(5)

        config_dict[topic] = {}

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertIn('message', SUT.subscribed_topics)
        self.assertIn(SUT.message_config_name, SUT.subscribed_topics['message'])
        self.assertNotIn('type', SUT.subscribed_topics['message'])

    #def test_field_named_message(self):
    def test_one(self):
        mock_logger = mock.Mock(spec=Logger)
        topic = random_string()
        config_key = random_string(10)

        config_dict = {}
        #config_dict['message'] = {}
        #config_dict['message']['type'] = random_string(10)
        #config_dict['message']['flatten_delimiter'] = random_string(5)
        #config_dict['message']['keyword_delimiter'] = random_string(5)
        #config_dict['message']['keyword_separator'] = random_string(5)

        config_dict[topic] = {}
        config_dict[topic]['message'] = {}
        #config_dict[topic]['message']['type'] = random_string(10)
        config_dict[topic]['message']['flatten_delimiter'] = random_string(5)
        config_dict[topic]['message']['keyword_delimiter'] = random_string(5)
        config_dict[topic]['message']['keyword_separator'] = random_string(5)
        config_dict[topic]['message'][config_key] = random_string()

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertIn('message', SUT.subscribed_topics[topic]['fields'])
        self.assertNotIn('message', SUT.subscribed_topics[topic])

class TestConfigureFields(unittest.TestCase):
    def test_no_field_configuration(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        configured_field = {}
        configured_field[topic] = {}
        configured_field[topic]['name'] = topic
        configured_field[topic]['contains_total'] = True
        #configured_field[topic]['ignore'] = False
        #configured_field[topic]['conversion_func'] = {}
        #configured_field[topic]['conversion_func']['source'] = 'lambda x: to_float(x)'
        configured_field[topic]['conversion_type'] = 'float'
        configured_field[topic]['conversion_error_to_none'] = False
        config_dict = {}

        config_dict[topic] = {'contains_total': True}

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertIn(topic, SUT.subscribed_topics[topic]['fields'])
        # ToDo - figure out a more robust check
        self.assertGreaterEqual(SUT.subscribed_topics[topic]['fields'][topic].items(), configured_field[topic].items())
        self.assertEqual(SUT.subscribed_topics[topic]['fields'][topic]['conversion_func']['source'], 'lambda x: to_float(x)')

    def test_global_defaults(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}
        config_dict['ignore'] = 'true'
        config_dict['ignore_msg_id_field'] = 'true'
        config_dict['contains_total'] = 'true'
        config_dict['conversion_type'] = 'int'

        config_dict[topic] = {}

        fieldname = random_string()
        config_dict[topic][fieldname] = {}

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertTrue(SUT.subscribed_topics[topic]['fields'][fieldname]['ignore'])
        self.assertEqual(SUT.subscribed_topics[topic]['ignore_msg_id_field'], [fieldname])
        self.assertTrue(SUT.subscribed_topics[topic]['fields'][fieldname]['contains_total'])
        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['conversion_func']['source'], 'lambda x: to_int(x)')

    def test_topic_defaults(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}

        config_dict[topic] = {}
        config_dict[topic]['ignore'] = 'true'
        config_dict[topic]['ignore_msg_id_field'] = 'true'
        config_dict[topic]['contains_total'] = 'true'
        config_dict[topic]['conversion_type'] = 'int'

        fieldname = random_string()
        config_dict[topic][fieldname] = {}

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertTrue(SUT.subscribed_topics[topic]['fields'][fieldname]['ignore'])
        self.assertEqual(SUT.subscribed_topics[topic]['ignore_msg_id_field'], [fieldname])
        self.assertTrue(SUT.subscribed_topics[topic]['fields'][fieldname]['contains_total'])
        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['conversion_func']['source'], 'lambda x: to_int(x)')

    def test_configure_field(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}

        config_dict[topic] = {}

        fieldname = random_string()
        config_dict[topic][fieldname] = {}
        config_dict[topic][fieldname]['ignore'] = 'true'
        config_dict[topic][fieldname]['ignore_msg_id_field'] = 'true'
        config_dict[topic][fieldname]['contains_total'] = 'true'
        config_dict[topic][fieldname]['conversion_type'] = 'int'
        weewx_name = 'barfoo'
        config_dict[topic][fieldname]['name'] = weewx_name
        config_dict[topic][fieldname]['expires_after'] = 'none'
        unit_name = 'unit_name'
        config_dict[topic][fieldname]['units'] = unit_name

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertTrue(SUT.subscribed_topics[topic]['fields'][fieldname]['ignore'])
        self.assertEqual(SUT.subscribed_topics[topic]['ignore_msg_id_field'], [fieldname])
        self.assertTrue(SUT.subscribed_topics[topic]['fields'][fieldname]['contains_total'])
        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['conversion_func']['source'], 'lambda x: to_int(x)')
        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['name'], weewx_name)
        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['units'], unit_name)
        self.assertIsNone(SUT.cached_fields[weewx_name]['expires_after'])

    def test_configure_subfields(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}

        config_dict[topic] = {}

        fieldname = random_string()
        config_dict[topic][fieldname] = {}
        config_dict[topic][fieldname]['ignore'] = 'true'
        config_dict[topic][fieldname]['ignore_msg_id_field'] = 'true'
        config_dict[topic][fieldname]['contains_total'] = 'true'
        config_dict[topic][fieldname]['conversion_type'] = 'int'
        weewx_name = 'barfoo'
        config_dict[topic][fieldname]['name'] = weewx_name
        config_dict[topic][fieldname]['expires_after'] = 'none'
        unit_name = 'unit_name'
        config_dict[topic][fieldname]['units'] = unit_name
        config_dict[topic][fieldname]['subfields'] = {}
        subfield_name = 'subfield1'
        config_dict[topic][fieldname]['subfields'][subfield_name] = {}

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertIn(fieldname, SUT.subscribed_topics[topic]['fields'])

        self.assertTrue(SUT.subscribed_topics[topic]['fields'][subfield_name]['ignore'])
        self.assertEqual(SUT.subscribed_topics[topic]['ignore_msg_id_field'], [subfield_name])
        self.assertTrue(SUT.subscribed_topics[topic]['fields'][subfield_name]['contains_total'])
        self.assertEqual(SUT.subscribed_topics[topic]['fields'][subfield_name]['conversion_func']['source'], 'lambda x: to_int(x)')
        self.assertEqual(SUT.subscribed_topics[topic]['fields'][subfield_name]['units'], unit_name)
        self.assertIsNone(SUT.cached_fields[weewx_name]['expires_after'])

    def test_field_conversion_type_bool(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}

        config_dict[topic] = {}
        config_dict[topic]['conversion_type'] = 'int'

        fieldname = random_string()
        config_dict[topic][fieldname] = {}

        config_dict[topic][fieldname]['conversion_type'] = 'bool'

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['conversion_func']['source'], 'lambda x: to_bool(x)')

    def test_field_conversion_type_float(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}

        config_dict[topic] = {}
        config_dict[topic]['conversion_type'] = 'float'

        fieldname = random_string()
        config_dict[topic][fieldname] = {}

        config_dict[topic][fieldname]['conversion_type'] = 'float'

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['conversion_func']['source'], 'lambda x: to_float(x)')

    def test_field_conversion_type_int(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}

        config_dict[topic] = {}

        fieldname = random_string()
        config_dict[topic][fieldname] = {}

        config_dict[topic][fieldname]['conversion_type'] = 'int'

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['conversion_func']['source'], 'lambda x: to_int(x)')

    def test_field_conversion_type_unknown(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}

        config_dict[topic] = {}

        fieldname = random_string()
        config_dict[topic][fieldname] = {}

        config_dict[topic][fieldname]['conversion_type'] = 'unknown'

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['conversion_func']['source'], 'lambda x: x')

    # todo - issue 126, remove? rename?
    def test_field_conversion_type_unknown2(self):
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}

        config_dict[topic] = {}
        config_dict[topic]['conversion_type'] = 'int'

        fieldname = random_string()
        config_dict[topic][fieldname] = {}

        config_dict[topic][fieldname]['conversion_type'] = 'bool'
        config_dict[topic][fieldname]['conversion_func'] = 'lambda x: "foo"'

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertEqual(SUT.subscribed_topics[topic]['fields'][fieldname]['conversion_func']['source'], 'lambda x: "foo"')


    def test_filter_out_message(self):
        mock_logger = mock.Mock(spec=Logger)

        value_count = random.randint(1, 5)

        topic = random_string()
        config_dict = {}

        config_dict[topic] = {}

        fieldname = random_string()
        config_dict[topic][fieldname] = {}
        config_dict[topic][fieldname]['filter_out_message_when'] = []
        filters = {fieldname: []}
        i = 0
        while i < value_count:
            config_dict[topic][fieldname]['filter_out_message_when'].append(i)
            filters[fieldname].append(float(i))
            i += 1

        config = configobj.ConfigObj(config_dict)

        SUT = TopicManager(None, config, mock_logger)

        self.assertEqual(SUT.subscribed_topics[topic]['filters'], filters)

class TestQueueSizeCheck(unittest.TestCase):
    topic = random_string()
    config_dict = {}
    config_dict[topic] = {}
    config = configobj.ConfigObj(config_dict)

    def test_queue_max_reached(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(None, self.config, mock_logger)

        queue = deque()
        queue.append(random_string(), )
        queue.append(random_string(), )
        queue.append(random_string(), )
        queue.append(random_string(), )
        orig_queue_size = len(queue)
        max_queue = 2

        SUT._queue_size_check(queue, max_queue) # pylint: disable=protected-access
        self.assertEqual(mock_logger.error.call_count, orig_queue_size-max_queue+1)
        self.assertEqual(len(queue), max_queue-1)

    def test_queue_max_not_reached(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(None, self.config, mock_logger)

        queue = deque()
        queue.append(random_string(), )
        queue.append(random_string(), )
        queue.append(random_string(), )
        queue.append(random_string(), )
        orig_queue_size = len(queue)
        max_queue = 7

        SUT._queue_size_check(queue, max_queue) # pylint: disable=protected-access
        self.assertEqual(mock_logger.error.call_count, 0)
        self.assertEqual(len(queue), orig_queue_size)

    def test_queue_max_equal(self):
        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(None, self.config, mock_logger)

        queue = deque()
        queue.append(random_string(), )
        queue.append(random_string(), )
        queue.append(random_string(), )
        queue.append(random_string(), )
        orig_queue_size = len(queue)
        max_queue = 4

        SUT._queue_size_check(queue, max_queue) # pylint: disable=protected-access
        self.assertEqual(mock_logger.error.call_count, orig_queue_size-max_queue+1)
        self.assertEqual(len(queue), max_queue-1)


class TestAppendData(unittest.TestCase):
    topic = random_string()
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

        SUT = TopicManager(None, self.config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)['data']  # pylint: disable=protected-access

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

        SUT = TopicManager(None, config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)['data']  # pylint: disable=protected-access

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

        SUT = TopicManager(None, self.config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)['data']  # pylint: disable=protected-access

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

        SUT = TopicManager(None, self.config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)['data']  # pylint: disable=protected-access

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
        offset_str = f"{offset_hour_str}{offset_minute_str}"

        current_datetime = datetime.datetime.fromtimestamp(current_epoch).strftime(datetime_format)

        queue_data['dateTime'] = f"{current_datetime}+{offset_str}"

        adjusted_epoch = current_epoch + (offset_hour * 60 + offset_minute) * 60

        config = copy.deepcopy(self.config)
        config['datetime_format'] = datetime_format
        config['offset_format'] = offset_format

        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(None, config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)['data']  # pylint: disable=protected-access

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
        offset_str = f"{offset_hour_str}:{offset_minute_str}"

        current_datetime = datetime.datetime.fromtimestamp(current_epoch).strftime(datetime_format)

        queue_data['dateTime'] = f"{current_datetime} -{offset_str}"

        adjusted_epoch = current_epoch - (offset_hour * 60 + offset_minute) * 60

        config = copy.deepcopy(self.config)
        config['datetime_format'] = datetime_format
        config['offset_format'] = offset_format

        mock_logger = mock.Mock(spec=Logger)

        SUT = TopicManager(None, config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)['data']  # pylint: disable=protected-access

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

        SUT = TopicManager(None, config, mock_logger)

        SUT.append_data(self.topic, queue_data)
        queue = SUT._get_queue(self.topic)['data']  # pylint: disable=protected-access

        self.assertEqual(len(queue), 1)
        queue_element = queue.popleft()
        data = queue_element['data']
        self.assertGreaterEqual(data.items(), queue_data_subset.items())
        self.assertIn('dateTime', data)
        self.assertEqual(adjusted_epoch, data['dateTime'])


class TestGetQueueData(unittest.TestCase):
    topic = random_string()
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
            SUT = TopicManager(None, self.config, mock_logger)

            gen = SUT.get_data(SUT.subscribed_topics[self.topic]['queue'])
            data = next(gen, None)

            self.assertIsNone(data)

    def test_queue_datetime_in_future(self):
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
            SUT = TopicManager(None, self.config, mock_logger)
            SUT.append_data(self.topic, self.create_queue_data())
            gen = SUT.get_data(SUT.subscribed_topics[self.topic]['queue'], 0)
            data = next(gen, None)

            self.assertIsNone(data)

    def test_queue_good(self):
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
            SUT = TopicManager(None, self.config, mock_logger)
            elem_one = self.create_queue_data()
            elem_two = self.create_queue_data()
            elem_three = self.create_queue_data()
            SUT.append_data(self.topic, elem_one)
            SUT.append_data(self.topic, elem_two)
            SUT.append_data(self.topic, elem_three)

            elements = []
            for data in SUT.get_data(SUT.subscribed_topics[self.topic]['queue']):
                elements.append(data)

            self.assertEqual(len(elements), 3)
            self.assertDictEqual(elements[0], elem_one)
            self.assertDictEqual(elements[1], elem_two)
            self.assertDictEqual(elements[2], elem_three)

    def test_wind_queue_good(self):
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).add_data = mock.Mock(return_value={})
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})

            SUT = TopicManager(None, self.config, mock_logger)

            collector_topic = ""
            for topic, detail in SUT.subscribed_topics.items():
                if detail['queue']['type'] == 'collector':
                    collector_topic = topic
                    break

            fieldname = 'windSpeed'
            data = {
                fieldname: random.uniform(1, 100),
                'usUnits': 1,
                'dateTime': time.time()
            }

            SUT.append_data(collector_topic, data, fieldname)

            elements = []
            for data in SUT.get_data(SUT.subscribed_topics[collector_topic]['queue']):
                elements.append(data)

            self.assertEqual(len(elements), 0)

class TestGetWindQueueData(unittest.TestCase):
    topic = random_string()
    config_dict = {}
    config_dict['collect_wind_across_loops'] = False
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
            SUT = TopicManager(None, self.config, mock_logger)
            SUT.append_data(self.topic, self.create_queue_data(), fieldname=self.fieldname)

            gen = SUT.get_data(SUT.subscribed_topics[self.topic]['queue'], 0)
            data = next(gen, None)

            self.assertIsNone(data)

    def test_add_to_collector_returns_data(self):
        mock_logger = mock.Mock(spec=Logger)

        collected_data = self.create_queue_data()
        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
            type(mock_CollectData.return_value).add_data = mock.Mock(return_value=collected_data)
            SUT = TopicManager(None, self.config, mock_logger)
            SUT.append_data(self.topic, self.create_queue_data(), fieldname=self.fieldname)
            # ToDo - need to get the topic a better way
            # perhaps find it by searching on subscribed topic 'type'
            gen = SUT.get_data(SUT.subscribed_topics[SUT.collected_topic]['queue'])
            data = next(gen, None)

            self.assertEqual(data, collected_data)

            data = next(gen, None)
            self.assertIsNone(data)

    def test_get_from_collector_returns_data(self):
        mock_logger = mock.Mock(spec=Logger)

        collected_data = self.create_queue_data()
        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            type(mock_CollectData.return_value).get_data = mock.Mock(return_value=collected_data)
            SUT = TopicManager(None, self.config, mock_logger)

            gen = SUT.get_data(SUT.subscribed_topics[self.topic]['queue'], 0)
            data = next(gen, None)

            self.assertEqual(data, collected_data)

            data = next(gen, None)
            self.assertIsNone(data)

    @staticmethod
    def test_get_from_collector_not_called():
        mock_logger = mock.Mock(spec=Logger)

        topic = random_string()
        config_dict = {}
        config_dict[topic] = {}
        config = configobj.ConfigObj(config_dict)

        with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
            SUT = TopicManager(None, config, mock_logger)

            gen = SUT.get_data(SUT.subscribed_topics[topic]['queue'], 0)
            next(gen, None)

            mock_CollectData.get_data.assert_not_called()

class TestAccumulatedData(unittest.TestCase):

    topic = random_string()
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
        adjust_start_time = 1

        config = copy.deepcopy(self.config)
        config['ignore_start_time'] = True

        with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value=False)
                mock_to_std_system.return_value = final_record_data

                SUT = TopicManager(None, config, mock_logger)
                SUT.append_data(self.topic, {'dateTime': start_ts})

                accumulated_data = SUT.get_accumulated_data(SUT.subscribed_topics[self.topic]['queue'], 0, end_ts, 0)

                mock_Accum.assert_called_once_with(test_weewx_stubs.weeutil.weeutil.TimeSpan(start_ts - adjust_start_time, end_ts))
                self.assertDictEqual(accumulated_data, final_record_data)

    def test_ignore_start_set_and_adjusted(self):
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
        adjust_start_time = random.randint(2, 9)

        config = copy.deepcopy(self.config)
        config['ignore_start_time'] = True
        config['adjust_start_time'] = adjust_start_time

        with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value=False)
                mock_to_std_system.return_value = final_record_data

                SUT = TopicManager(None, config, mock_logger)
                SUT.append_data(self.topic, {'dateTime': start_ts})


                accumulated_data = SUT.get_accumulated_data(SUT.subscribed_topics[self.topic]['queue'], 0, end_ts, 0)

                mock_Accum.assert_called_once_with(test_weewx_stubs.weeutil.weeutil.TimeSpan(start_ts - adjust_start_time, end_ts))
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

                SUT = TopicManager(None, config, mock_logger)
                SUT.append_data(self.topic, {'dateTime': end_ts})


                accumulated_data = SUT.get_accumulated_data(SUT.subscribed_topics[self.topic]['queue'], 0, 0, 0)

                mock_Accum.assert_called_once_with(test_weewx_stubs.weeutil.weeutil.TimeSpan(0, end_ts))
                self.assertDictEqual(accumulated_data, final_record_data)

    def test_queue_element_before_start(self):
        mock_logger = mock.Mock(spec=Logger)
        queue_data = self.create_queue_data()

        with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                type(mock_Accum.return_value).addRecord = \
                    mock.Mock(side_effect=test_weewx_stubs.weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))

                SUT = TopicManager(None, self.config, mock_logger)
                SUT.append_data(self.topic, queue_data)

                mock_logger.reset_mock()
                accumulated_data = SUT.get_accumulated_data(SUT.subscribed_topics[self.topic]['queue'], 0, time.time(), 0)

                self.assertDictEqual(accumulated_data, {})
                mock_logger.info.assert_called_once()
                mock_Accum.getRecord.assert_not_called()
                mock_to_std_system.assert_not_called()

    def test_queue_empty(self):
        mock_logger = mock.Mock(spec=Logger)

        with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value=True)

                SUT = TopicManager(None, self.config, mock_logger)

                accumulated_data = SUT.get_accumulated_data(SUT.subscribed_topics[self.topic]['queue'], 0, time.time(), 0)

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

                SUT = TopicManager(None, self.config, mock_logger)
                SUT.append_data(self.topic, {})

                accumulated_data = SUT.get_accumulated_data(SUT.subscribed_topics[self.topic]['queue'], 0, time.time(), 0)

                self.assertDictEqual(accumulated_data, final_record_data)

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestConfigureFields('test_use_topic_as_fieldname'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
