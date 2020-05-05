# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest

import random
import time

import mock

import test_weewx_stubs # used to set up stubs - pylint: disable=unused-import

from user.MQTTSubscribe import CollectData


class Test_add_data(unittest.TestCase):
    wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']
    wind_field = 'windSpeed'

    def test_data_in_fields(self):
        units = 1
        data = {
            self.wind_field: random.uniform(1, 100),
            'dateTime': int(time.time() + 0.5)
        }

        with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
            SUT = CollectData(self.wind_fields, units)
            mock_to_std_system.return_value = data
            added_data = SUT.add_data(self.wind_field, data)

            self.assertDictEqual(added_data, {})
            self.assertDictEqual(SUT.data, data)

    def test_second_data(self):
        units = 1
        first_data = {
            self.wind_field: random.uniform(1, 100),
            'usUnits': units,
            'dateTime': int(time.time() + 0.5)
        }
        second_data = {
            self.wind_field: random.uniform(1, 100),
            'dateTime': int(time.time() + 0.5)
        }

        with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
            SUT = CollectData(self.wind_fields, units)
            mock_to_std_system.return_value = first_data
            SUT.add_data(self.wind_field, first_data)
            mock_to_std_system.return_value = second_data
            added_data = SUT.add_data(self.wind_field, second_data)

            self.assertDictEqual(added_data, first_data)
            self.assertDictEqual(SUT.data, second_data)

    def test_additional_data(self):
        second_field = 'windDir'
        units = 1
        first_data = {
            self.wind_field: random.uniform(1, 100),
            'usUnits': units,
            'dateTime': int(time.time() + 0.5)
        }
        second_data = {
            second_field: random.uniform(1, 100),
            'usUnits': units,
            'dateTime': int(time.time() + 0.5)
        }

        total_data = second_data
        total_data['windSpeed'] = first_data['windSpeed']
        del total_data['usUnits']

        with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:

            SUT = CollectData(self.wind_fields, units)
            mock_to_std_system.return_value = first_data
            SUT.add_data(self.wind_field, first_data)
            mock_to_std_system.return_value = second_data
            added_data = SUT.add_data(second_field, second_data)

        self.assertDictEqual(added_data, {})
        self.assertDictEqual(SUT.data, total_data)

class Test_get_data(unittest.TestCase):
    wind_field = 'windSpeed'
    wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

    units = 1
    data = {
        wind_field: random.uniform(1, 100),
        'usUnits': 1,
        'dateTime': int(time.time() + 0.5)
    }

    def test_get_data(self):
        with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:

            SUT = CollectData(self.wind_fields, self.units)
            mock_to_std_system.return_value = self.data
            SUT.add_data(self.wind_field, self.data)

            collected_data = SUT.get_data()

            self.assertDictEqual(collected_data, self.data)

if __name__ == '__main__':
    unittest.main(exit=False)
