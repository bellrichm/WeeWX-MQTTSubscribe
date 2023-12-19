#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import random
import sys
import time

import unittest

import test_weewx_stubs
from test_weewx_stubs import random_string
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()
from user.MQTTSubscribe import RecordCache

class Test_clear_cache(unittest.TestCase):
    def test_cache_is_cleared(self):
        unit_system = random.randint(1, 10)
        SUT = RecordCache()

        key = random_string()
        value = round(random.uniform(1, 100), 2)
        timestamp = time.time()
        SUT.update_value(key, value, unit_system, timestamp)

        SUT.clear_cache()
        self.assertEqual(SUT.cached_values, {})

class Test_update_value(unittest.TestCase):
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

    def test_value_is_updated(self):
        unit_system = random.randint(1, 10)
        SUT = RecordCache()

        key = random_string()
        value = round(random.uniform(1, 100), 2)
        timestamp = time.time()

        SUT.update_value(key, value, unit_system, timestamp)
        self.assertIn(key, SUT.cached_values)
        self.assertEqual(SUT.cached_values[key]['value'], value)
        self.assertEqual(SUT.cached_values[key]['timestamp'], timestamp)

    def test_mismatch_unit_system(self):
        unit_system = random.randint(1, 10)
        SUT = RecordCache()

        key = random_string()

        SUT.update_value(key, unit_system, round(random.uniform(1, 100), 2), time.time())

        value = round(random.uniform(1, 100), 2)
        timestamp = time.time()

        unit_system_mismatch = random.randint(11, 20)
        self.assertRaises(ValueError,
                          SUT.update_value, key, value, unit_system_mismatch, timestamp)

class Test_get_value(unittest.TestCase):
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

    def test_key_not_in_cache(self):
        SUT = RecordCache()

        value = SUT.get_value(random_string(), 0, None)

        self.assertIsNone(value)

    def test_get_data_expiration_is_none(self):
        unit_system = random.randint(1, 10)
        SUT = RecordCache()

        key = random_string()
        value = round(random.uniform(1, 100), 2)
        SUT.update_value(key, value, unit_system, time.time())

        cached_value = SUT.get_value(key, None, None)
        self.assertEqual(cached_value, value)

    def test_get_data_is_not_expired(self):
        unit_system = random.randint(1, 10)
        SUT = RecordCache()
        key = random_string()
        value = round(random.uniform(1, 100), 2)
        timestamp = time.time()
        SUT.update_value(key, value, unit_system, timestamp)

        cached_value = SUT.get_value(key, timestamp, 1)
        self.assertEqual(cached_value, value)

    def test_get_data_is_expired(self):
        unit_system = random.randint(1, 10)
        SUT = RecordCache()
        key = random_string()
        value = round(random.uniform(1, 100), 2)
        timestamp = time.time()
        SUT.update_value(key, value, unit_system, timestamp)

        cached_value = SUT.get_value(key, timestamp + 1, 0)
        self.assertIsNone(cached_value)

class Test_update_timestamp(unittest.TestCase):
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

    def test_key_does_not_exist(self):
        # somewhat silly test
        unit_system = random.randint(1, 10)
        SUT = RecordCache()
        key = random_string()
        value = round(random.uniform(1, 100), 2)
        SUT.update_value(key, value, unit_system, time.time())

        nonexisting_key = random_string()
        SUT.update_timestamp(nonexisting_key, time.time())
        self.assertNotIn(nonexisting_key, SUT.cached_values)

    def test_key_exists(self):
        unit_system = random.randint(1, 10)
        SUT = RecordCache()
        key = random_string()
        value = round(random.uniform(1, 100), 2)
        SUT.update_value(key, value, unit_system, 0)

        new_time = time.time()
        SUT.update_timestamp(key, new_time)
        self.assertEqual(SUT.cached_values[key]['timestamp'], new_time)

class Test_remove_value(unittest.TestCase):
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

    def test_key_does_not_exist(self):
        # somewhat silly test
        unit_system = random.randint(1, 10)
        SUT = RecordCache()
        key = random_string()
        value = round(random.uniform(1, 100), 2)
        SUT.update_value(key, value, unit_system, time.time())

        nonexisting_key = random_string()
        SUT.remove_value(nonexisting_key)
        self.assertNotIn(nonexisting_key, SUT.cached_values)

    def test_key_exists(self):
        unit_system = random.randint(1, 10)
        SUT = RecordCache()
        key = random_string()
        value = round(random.uniform(1, 100), 2)
        SUT.update_value(key, value, unit_system, time.time())

        SUT.remove_value(key)
        self.assertNotIn(key, SUT.cached_values)

if __name__ == '__main__':
    unittest.main(exit=False)
