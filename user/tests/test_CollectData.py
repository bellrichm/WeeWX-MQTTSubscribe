from __future__ import with_statement

import unittest
import mock

import random
import time

from user.MQTTSubscribe import CollectData

class Test_add_data(unittest.TestCase):
    wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

    def test_data_not_in_fields(self):
        data = {
            'inTemp': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }

        SUT = CollectData(self.wind_fields)
        added_data = SUT.add_data(data)

        self.assertIsNone(added_data)
        self.assertDictEqual(SUT.data, {})

    def test_data_in_fields(self):
        data = {
            'windSpeed': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }

        SUT = CollectData(self.wind_fields)
        added_data = SUT.add_data(data)

        self.assertDictEqual(added_data, {})
        self.assertDictEqual(SUT.data, data)

    def test_second_data(self):
        first_data = {
            'windSpeed': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }
        second_data = {
            'windSpeed': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
        }

        SUT = CollectData(self.wind_fields)
        SUT.add_data(first_data)
        added_data = SUT.add_data(second_data)

        self.assertDictEqual(added_data, first_data)
        self.assertDictEqual(SUT.data, second_data)

        print('done')
                
class Test_get_data(unittest.TestCase):
    wind_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']

    data = {
        'windSpeed': random.uniform(1, 100),
        'usUnits': 1,
        'dateTime': int(time.time() + 0.5)
    }

    def test_get_data(self):
        SUT = CollectData(self.wind_fields)
        SUT.add_data(self.data)

        collected_data = SUT.get_data()

        self.assertDictEqual(collected_data, self.data)

if __name__ == '__main__':
    unittest.main()
