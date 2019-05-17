from __future__ import with_statement

import unittest
import mock

import paho.mqtt.client
import random
import time
import weewx

import user.MQTTSubscribe
from user.MQTTSubscribe import MQTTSubscribe, MQTTSubscribeService

class Testnew_loop_packet(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def test_queue_empty(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        packet_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        final_packet_data = dict(packet_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=packet_data)

        config_dict = {}
        config_dict['MQTTSubscribeService'] = {}
        config_dict['MQTTSubscribeService']['topic'] = 'foo/bar'

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                    SUT = MQTTSubscribeService(self.mock_StdEngine, config_dict)
                    SUT.end_ts = start_ts

                    SUT.new_loop_packet(new_loop_packet_event)

                    self.assertDictEqual(new_loop_packet_event.packet, final_packet_data)
                    mock_Accum.addRecord.assert_not_called()
                    mock_Accum.getRecord.assert_not_called()
                    mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_element_before_start(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': start_ts
        }

        packet_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        final_packet_data = dict(packet_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=packet_data)

        topic = 'foo/bar'
        config_dict = {}
        config_dict['MQTTSubscribeService'] = {}
        config_dict['MQTTSubscribeService']['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                    SUT = MQTTSubscribeService(self.mock_StdEngine, config_dict)
                    #TODO - mock manger, not mqtt
                    SUT.manager.topics[topic]['queue'].append(queue_data, )
                    SUT.end_ts = start_ts

                    with mock.patch('user.MQTTSubscribe.loginf') as mock_loginf:
                        SUT.new_loop_packet(new_loop_packet_event)

                        self.assertDictEqual(new_loop_packet_event.packet, final_packet_data)
                        mock_loginf.assert_called_once()
                        mock_Accum.getRecord.assert_not_called()
                        mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_element_after_end(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': end_period_ts + 300
        }

        packet_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        final_packet_data = dict(packet_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=packet_data)

        topic = 'foo/bar'
        config_dict = {}
        config_dict['MQTTSubscribeService'] = {}
        config_dict['MQTTSubscribeService']['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:

                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    SUT = MQTTSubscribeService(self.mock_StdEngine, config_dict)
                    #TODO - mock manger, not mqtt
                    SUT.manager.topics[topic]['queue'].append(queue_data, )
                    SUT.end_ts = start_ts

                    SUT.new_loop_packet(new_loop_packet_event)

                    self.assertDictEqual(new_loop_packet_event.packet, final_packet_data)
                    mock_Accum.addRecord.assert_not_called()
                    mock_Accum.getRecord.assert_not_called()
                    mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_valid(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': current_time
        }

        packet_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        aggregate_data = dict(queue_data)

        target_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': packet_data['usUnits'],
            'interval': packet_data['interval'],
            'dateTime': packet_data['dateTime']
        }

        final_packet_data = dict(packet_data)
        final_packet_data.update(target_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=packet_data)

        topic = 'foo/bar'
        config_dict = {}
        config_dict['MQTTSubscribeService'] = {}
        config_dict['MQTTSubscribeService']['topic'] = 'foo/bar'

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    mock_to_std_system.return_value = target_data
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = False)
                    type(mock_Accum.return_value).getRecord = mock.Mock(return_value=aggregate_data)
                    SUT = MQTTSubscribeService(self.mock_StdEngine, config_dict)
                    #TODO - mock manger, not mqtt                    
                    SUT.manager.topics[topic]['queue'].append(queue_data, )
                    SUT.end_ts = start_ts

                    SUT.new_loop_packet(new_loop_packet_event)

                    self.assertDictEqual(new_loop_packet_event.packet, final_packet_data)

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

    def test_wind_queue_empty(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        topic = 'foo/bar'

        self.setup_wind_queue_tests(start_ts, end_period_ts, topic)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
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

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                        type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                        type(mock_CollectData.return_value).add_data = mock.Mock(return_value={})
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value=self.aggregate_data)
                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        #TODO - mock manger, not mqtt
                        SUT.manager.topics[topic]['queue_wind'].append(self.queue_data, )
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

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                        type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                        type(mock_CollectData.return_value).add_data = mock.Mock(return_value=self.aggregate_data)
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})                            
                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        #TODO - mock manger, not mqtt
                        SUT.manager.topics[topic]['queue_wind'].append(self.queue_data, )
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

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        #TODO - mock manger, not mqtt
                        SUT.manager.topics[topic]['queue_wind'].append(self.queue_data, )
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

        target_data = {
            'windSpeed': random.uniform(1, 100),
            'usUnits': self.packet_data['usUnits'],
            'interval': self.packet_data['interval'],
            'dateTime': self.packet_data['dateTime']
        }

        self.final_packet_data.update(target_data)

        new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=self.packet_data)

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        mock_to_std_system.return_value = target_data
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = False)
                        type(mock_Accum.return_value).getRecord = mock.Mock(return_value=self.aggregate_data)
                        type(mock_CollectData.return_value).add_data = mock.Mock(return_value={})
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value=self.aggregate_data)
                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        #TODO - mock manger, not mqtt
                        SUT.manager.topics[topic]['queue_wind'].append(self.queue_data, )
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

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    with mock.patch('user.MQTTSubscribe.CollectData') as mock_CollectData:
                        mock_to_std_system.return_value = target_data
                        type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = False)
                        type(mock_Accum.return_value).getRecord = mock.Mock(return_value=self.aggregate_data)
                        type(mock_CollectData.return_value).add_data = mock.Mock(return_value=self.aggregate_data)
                        type(mock_CollectData.return_value).get_data = mock.Mock(return_value={})
                        SUT = MQTTSubscribeService(self.mock_StdEngine, self.config_dict)
                        #TODO - mock manger, not mqtt
                        SUT.manager.topics[topic]['queue_wind'].append(self.queue_data, )
                        SUT.end_ts = start_ts

                        SUT.new_loop_packet(new_loop_packet_event)

                        self.assertDictEqual(new_loop_packet_event.packet, self.final_packet_data)

        SUT.shutDown()


class Testnew_archive_record(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def test_queue_empty(self):

        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        record_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        final_record_data = dict(record_data)

        new_loop_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                    record=record_data,
                                                    origin='hardware')

        config_dict = {}
        config_dict['MQTTSubscribeService'] = {}
        config_dict['MQTTSubscribeService']['topic'] = 'foo/bar'

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                    SUT = MQTTSubscribeService(self.mock_StdEngine, config_dict)
                    SUT.end_ts = start_ts

                    SUT.new_archive_record(new_loop_record_event)

                    self.assertDictEqual(new_loop_record_event.record, final_record_data)
                    mock_Accum.addRecord.assert_not_called()
                    mock_Accum.getRecord.assert_not_called()
                    mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_element_before_start(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': start_ts
        }

        record_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        final_record_data = dict(record_data)

        new_loop_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                    record=record_data,
                                                    origin='hardware')

        topic = 'foo/bar'
        config_dict = {}
        config_dict['MQTTSubscribeService'] = {}
        config_dict['MQTTSubscribeService']['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    type(mock_Accum.return_value).addRecord = mock.Mock(side_effect=weewx.accum.OutOfSpan("Attempt to add out-of-interval record"))
                    SUT = MQTTSubscribeService(self.mock_StdEngine, config_dict)
                    #TODO - mock manger, not mqtt
                    SUT.manager.topics[topic]['queue'].append(queue_data, )
                    SUT.end_ts = start_ts

                    with mock.patch('user.MQTTSubscribe.loginf') as mock_loginf:
                        SUT.new_archive_record(new_loop_record_event)

                        self.assertDictEqual(new_loop_record_event.record, final_record_data)
                        mock_loginf.assert_called_once()
                        mock_Accum.getRecord.assert_not_called()
                        mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_element_after_end(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': end_period_ts + 300
        }

        record_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        final_record_data = dict(record_data)

        new_loop_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                    record=record_data,
                                                    origin='hardware')

        topic = 'foo/bar'
        config_dict = {}
        config_dict['MQTTSubscribeService'] = {}
        config_dict['MQTTSubscribeService']['topic'] = topic
        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = True)
                    SUT = MQTTSubscribeService(self.mock_StdEngine, config_dict)
                    #TODO - mock manger, not mqtt
                    SUT.manager.topics[topic]['queue'].append(queue_data, )
                    SUT.end_ts = start_ts

                    SUT.new_archive_record(new_loop_record_event)

                    self.assertDictEqual(new_loop_record_event.record, final_record_data)
                    mock_Accum.addRecord.assert_not_called()
                    mock_Accum.getRecord.assert_not_called()
                    mock_to_std_system.assert_not_called()

        SUT.shutDown()

    def test_queue_valid(self):
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300
        start_ts = end_period_ts - 300
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': current_time
        }

        record_data = {
            'usUnits': 1,
            'interval': 5,
            'dateTime': end_period_ts
        }

        aggregate_data = dict(queue_data)

        target_data = {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': record_data['usUnits'],
            'interval': record_data['interval'],
            'dateTime': record_data['dateTime']
        }

        final_record_data = dict(record_data)
        final_record_data.update(target_data)

        new_loop_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                    record=record_data,
                                                    origin='hardware')

        topic = 'foo/bar'
        config_dict = {}
        config_dict['MQTTSubscribeService'] = {}
        config_dict['MQTTSubscribeService']['topic'] = topic

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    mock_to_std_system.return_value = target_data
                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = False)
                    type(mock_Accum.return_value).getRecord = mock.Mock(return_value=aggregate_data)
                    SUT = MQTTSubscribeService(self.mock_StdEngine, config_dict)
                    #TODO - mock manger, not mqtt
                    SUT.manager.topics[topic]['queue'].append(queue_data, )

                    SUT.end_ts = start_ts

                    SUT.new_archive_record(new_loop_record_event)

                    self.assertDictEqual(new_loop_record_event.record, final_record_data)

        SUT.shutDown()


if __name__ == '__main__':
    unittest.main()