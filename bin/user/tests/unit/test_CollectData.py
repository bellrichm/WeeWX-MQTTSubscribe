# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import unittest

import random
import time

from user.MQTTSubscribe import CollectData


class Test_add_data(unittest.TestCase):
    wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']
    wind_field = 'windSpeed'

    def test_data_in_fields(self):
        data = {
            self.wind_field: random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }

        SUT = CollectData(self.wind_fields)
        added_data = SUT.add_data(self.wind_field, data)

        self.assertDictEqual(added_data, {})
        self.assertDictEqual(SUT.data, data)

    def test_second_data(self):
        first_data = {
            self.wind_field: random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }
        second_data = {
            self.wind_field: random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }

        SUT = CollectData(self.wind_fields)
        SUT.add_data(self.wind_field, first_data)
        added_data = SUT.add_data(self.wind_field, second_data)

        self.assertDictEqual(added_data, first_data)
        self.assertDictEqual(SUT.data, second_data)

    def test_additional_data(self):
        second_field = 'windDir'
        first_data = {
            self.wind_field: random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }
        second_data = {
            second_field: random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }

        total_data = second_data
        total_data['windSpeed'] = first_data['windSpeed']

        SUT = CollectData(self.wind_fields)
        SUT.add_data(self.wind_field, first_data)
        added_data = SUT.add_data(second_field, second_data)

        self.assertDictEqual(added_data, {})
        self.assertDictEqual(SUT.data, total_data)        


class Test_get_data(unittest.TestCase):
    wind_field = 'windSpeed'
    wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

    data = {
        wind_field: random.uniform(1, 100),
        'usUnits': 1,
        'dateTime': int(time.time() + 0.5)
    }

    def test_get_data(self):
        SUT = CollectData(self.wind_fields)
        SUT.add_data(self.wind_field, self.data)

        collected_data = SUT.get_data()

        self.assertDictEqual(collected_data, self.data)

if __name__ == '__main__':
    unittest.main(exit=False)
