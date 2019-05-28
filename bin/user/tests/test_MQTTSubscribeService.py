from __future__ import with_statement

import unittest
import mock

from collections import deque
import configobj
import random
import six
import time
import weewx

import user.MQTTSubscribe
from user.MQTTSubscribe import MQTTSubscribe, MQTTSubscribeService, TopicX

class Testnew_loop_packet(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def setup_queue_tests(self, start_ts, end_period_ts, topic):
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        self.queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
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

        self.config_dict = {}
        self.config_dict['MQTTSubscribeService'] = {}
        self.config_dict['MQTTSubscribeService']['topic'] = 'foo/bar'

        ## self.topics = {}
        ## self.topics[topic] = {}
        ## self.topics[topic]['queue'] = deque()
        ## self.topics[topic]['queue'].append(self.queue_data, )
        ## self.topics[topic]['queue_wind'] = deque()

        self.topics = {}
        self.topics[topic] = {}
        self.topics[topic]['unit_system'] = 'US'
        self.topics[topic]['max_queue'] = six.MAXSIZE
        self.topic_config = configobj.ConfigObj(self.topics)
        self.topics2 = TopicX(self.topic_config)
        self.topics2.get_queue(topic).append(self.queue_data, )

        self.queues = []
        self.queues.append({
            'queue': deque(),
            'queue_wind': deque()
            }
        )

    def test_queue_empty(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_queue_tests(start_ts, end_period_ts, topic)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                    SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                    SUT.end_ts = start_ts

                    SUT.new_loop_packet(new_loop_packet_event)

                    self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)
                    mock_Accum.addRecord.assert_not_called()
                    mock_Accum.getRecord.assert_not_called()
                    mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_element_before_start(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_queue_tests(start_ts, end_period_ts, topic)
        self.queues[0]['queue'].append(self.queue_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                    ## type(mock_manager.return_value).topics2 = mock.PropertyMock(return_value = self.topics2)
                    type(mock_manager.return_value).Queues = mock.PropertyMock(return_value = self.queues)
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))

                    SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                    SUT.end_ts = start_ts

                    with mock.patch('user.MQTTSubscribe.loginf') as mock_loginf:
                        SUT.new_loop_packet(new_loop_packet_event)

                        self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)
                        mock_loginf.assert_called_once()
                        mock_Accum.getRecord.assert_not_called()
                        mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_element_after_end(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_queue_tests(start_ts, end_period_ts, topic)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)

                    SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                    SUT.end_ts = start_ts

                    SUT.new_loop_packet(new_loop_packet_event)

                    self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)
                    mock_Accum.addRecord.assert_not_called()
                    mock_Accum.getRecord.assert_not_called()
                    mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_valid(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_queue_tests(start_ts, end_period_ts, topic)
        self.final_packet_data.update(self.target_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    mock_to_std_system.return_value = self.target_data
                    type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                    ## type(mock_manager.return_value).topics2 = mock.PropertyMock(return_value = self.topics2)
                    type(mock_manager.return_value).Queues = mock.PropertyMock(return_value = self.queues)
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = False)
                    type(mock_Accum.return_value).getRecord = mock.Mock(return_value=self.aggregate_data)

                    SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                    SUT.end_ts = start_ts

                    SUT.new_loop_packet(new_loop_packet_event)

                    self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)

        SUT.shutDown()

    def setup_wind_queue_tests(self, start_ts, end_period_ts, topic):
        self.queue_data = {
            'windSpeed': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': start_ts
        }

        self.packet_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        self.aggregate_data = dict(self.queue_data)

        self.final_packet_data = dict(self.packet_data)

        self.config_dict = {}
        self.config_dict['MQTTSubscribeService'] = {}
        self.config_dict['MQTTSubscribeService']['topic'] = topic

        ##self.topics = {}
        ## self.topics[topic] = {}
        ## self.topics[topic]['queue'] = deque()
        ## self.topics[topic]['queue_wind'] = deque()
        ## self.topics[topic]['queue_wind'].append(self.queue_data, )
                
        self.topics = {}
        self.topics[topic] = {}
        self.topics[topic]['unit_system'] = 'US'
        self.topics[topic]['max_queue'] = six.MAXSIZE
        self.topic_config = configobj.ConfigObj(self.topics)
        self.topics2 = TopicX(self.topic_config)
        self.topics2.get_wind_queue(topic).append(self.queue_data, )

        self.queues = []
        self.queues.append({
            'queue': deque(),
            'queue_wind': deque()
            }
        )

    def test_wind_queue_empty(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        topic = 'foo/bar'

        self.setup_wind_queue_tests(start_ts, end_period_ts, topic)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                        type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        SUT.end_ts = start_ts

                        SUT.new_loop_packet(new_loop_packet_event)

                        self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)
                        mock_Accum.addRecord.assert_not_called()
                        mock_Accum.getRecord.assert_not_called()
                        mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_wind_queue_element_before_start_single(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        topic = 'foo/bar'

        self.setup_wind_queue_tests(start_ts, end_period_ts, topic)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                        ## type(mock_manager.return_value).topics2 = mock.PropertyMock(return_value = self.topics2)
                        type(mock_manager.return_value).Queues = mock.PropertyMock(return_value = self.queues)
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                        type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                        type(mock_CollectData.return_value).add_data = mock.Mock(return_value={})
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value=self.aggregate_data)

                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        SUT.end_ts = start_ts

                        with mock.patch('user.MQTTSubscribe.loginf') as mock_loginf:
                            SUT.new_loop_packet(new_loop_packet_event)

                            self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)
                            mock_loginf.assert_called_once()
                            mock_Accum.getRecord.assert_not_called()
                            mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_wind_queue_element_before_start_multiple(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        topic = 'foo/bar'

        self.setup_wind_queue_tests(start_ts, end_period_ts, topic)
	self.queues[0]['queue_wind'].append(self.queue_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                        ## type(mock_manager.return_value).topics2 = mock.PropertyMock(return_value = self.topics2)
                        type(mock_manager.return_value).Queues = mock.PropertyMock(return_value = self.queues)                        
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                        type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                        type(mock_CollectData.return_value).add_data = mock.Mock(return_value=self.aggregate_data)
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})

                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        SUT.end_ts = start_ts

                        with mock.patch('user.MQTTSubscribe.loginf') as mock_loginf:
                            SUT.new_loop_packet(new_loop_packet_event)

                            self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)
                            mock_loginf.assert_called_once()
                            mock_Accum.getRecord.assert_not_called()
                            mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_wind_queue_element_after_end(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        topic = 'foo/bar'

        self.setup_wind_queue_tests(start_ts, end_period_ts, topic)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})

                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        SUT.end_ts = start_ts

                        SUT.new_loop_packet(new_loop_packet_event)

                        self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)
                        mock_Accum.addRecord.assert_not_called()
                        mock_Accum.getRecord.assert_not_called()
                        mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_wind_queue_single_valid(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        windSpeed = random.uniform(1, 100)
        topic = 'foo/bar'

        self.setup_wind_queue_tests(start_ts, end_period_ts, topic)
        self.queues[0]['queue_wind'].append(self.queue_data)

        target_data = {
            'windSpeed': random.uniform(1, 100),
            'usUnits': self.packet_data['usUnits'],
            'interval': self.packet_data['interval'],
            'dateTime': self.packet_data['dateTime']
        }

        self.final_packet_data.update(target_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        mock_to_std_system.return_value = target_data
                        type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                        ## type(mock_manager.return_value).topics2 = mock.PropertyMock(return_value = self.topics2)
                        type(mock_manager.return_value).Queues = mock.PropertyMock(return_value = self.queues)
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = False)
                        type(mock_Accum.return_value).getRecord = mock.Mock(return_value=self.aggregate_data)
                        type(mock_CollectData.return_value).add_data = mock.Mock(return_value={})
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value=self.aggregate_data)

                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        SUT.end_ts = start_ts

                        SUT.new_loop_packet(new_loop_packet_event)

                        self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)

        SUT.shutDown()

    def test_wind_queue_multiple_valid(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        windSpeed = random.uniform(1, 100)
        topic = 'foo/bar'

        self.setup_wind_queue_tests(start_ts, end_period_ts, topic)

        target_data = {
            'windSpeed': random.uniform(1, 100),
            'usUnits': self.packet_data['usUnits'],
            'interval': self.packet_data['interval'],
            'dateTime': self.packet_data['dateTime']
        }

        self.final_packet_data.update(target_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        mock_to_std_system.return_value = target_data
                        type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                        ##type(mock_manager.return_value).topics2 = mock.PropertyMock(return_value = self.topics2)
                        type(mock_manager.return_value).Queues = mock.PropertyMock(return_value = self.queues)
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = False)
                        type(mock_Accum.return_value).getRecord = mock.Mock(return_value=self.aggregate_data)
                        type(mock_CollectData.return_value).add_data = mock.Mock(return_value=self.aggregate_data)
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})

                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        SUT.end_ts = start_ts

                        SUT.new_loop_packet(new_loop_packet_event)

                        self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)

        SUT.shutDown()


class Testnew_archive_record(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def setup_archive_queue_tests(self, start_ts, end_period_ts, topic):
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        self.queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
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

        self.config_dict = {}
        self.config_dict['MQTTSubscribeService'] = {}
        self.config_dict['MQTTSubscribeService']['topic'] = topic

        ## self.topics = {}
        ## self.topics[topic] = {}
        ## self.topics[topic]['queue'] = deque()
        ## self.topics[topic]['queue'].append(self.queue_data, )
        ## self.topics[topic]['queue_wind'] = deque()

        self.topics = {}
        self.topics[topic] = {}
        self.topics[topic]['unit_system'] = 'US'
        self.topics[topic]['max_queue'] = six.MAXSIZE
        self.topic_config = configobj.ConfigObj(self.topics)
        self.topics2 = TopicX(self.topic_config)
        self.topics2.get_queue(topic).append(self.queue_data, )

        self.queues = []
        self.queues.append({
            'queue': deque(),
            'queue_wind': deque()
            }
        )

    def test_queue_empty(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_archive_queue_tests(start_ts, end_period_ts, topic)

        new_loop_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                    record=self.record_data,
                                                    origin='hardware')


        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))

                    SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                    SUT.end_ts = start_ts

                    SUT.new_archive_record(new_loop_record_event)

                    self.assertDictEqual(new_loop_record_event.record, self.final_record_data)
                    mock_Accum.addRecord.assert_not_called()
                    mock_Accum.getRecord.assert_not_called()
                    mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_element_before_start(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_archive_queue_tests(start_ts, end_period_ts, topic)
        self.queues[0]['queue'].append(self.queue_data)

        new_loop_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                    record=self.record_data,
                                                    origin='hardware')

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                    ## type(mock_manager.return_value).topics2 = mock.PropertyMock(return_value = self.topics2)
                    type(mock_manager.return_value).Queues = mock.PropertyMock(return_value = self.queues)
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))

                    SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                    SUT.end_ts = start_ts

                    with mock.patch('user.MQTTSubscribe.loginf') as mock_loginf:
                        SUT.new_archive_record(new_loop_record_event)

                        self.assertDictEqual(new_loop_record_event.record, self.final_record_data)
                        mock_loginf.assert_called_once()
                        mock_Accum.getRecord.assert_not_called()
                        mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_element_after_end(self):
        topic = 'foo/bar'
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        self.setup_archive_queue_tests(start_ts, end_period_ts, topic)

        new_loop_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                    record=self.record_data,
                                                    origin='hardware')

        with mock.patch('user.MQTTSubscribe.MQTTSubscribe') as mock_manager:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)

                    SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                    SUT.end_ts = start_ts

                    SUT.new_archive_record(new_loop_record_event)

                    self.assertDictEqual(new_loop_record_event.record, self.final_record_data)
                    mock_Accum.addRecord.assert_not_called()
                    mock_Accum.getRecord.assert_not_called()
                    mock_to_std_system.assert_not_called()

        SUT.shutDown()

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
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    mock_to_std_system.return_value = self.target_data
                    type(mock_manager.return_value).Topics = mock.PropertyMock(return_value = self.topics)
                    ## type(mock_manager.return_value).topics2 = mock.PropertyMock(return_value = self.topics2)
                    type(mock_manager.return_value).Queues = mock.PropertyMock(return_value = self.queues)
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = False)
                    type(mock_Accum.return_value).getRecord = mock.Mock(return_value=self.aggregate_data)

                    SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                    SUT.end_ts = start_ts

                    SUT.new_archive_record(new_loop_record_event)

                    self.assertDictEqual(new_loop_record_event.record, self.final_record_data)

        SUT.shutDown()


if __name__ == '__main__':
    unittest.main()