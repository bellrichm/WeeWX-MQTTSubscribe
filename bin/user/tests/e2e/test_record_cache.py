#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import unittest
import mock

import configobj
import random
import string
from io import StringIO

import weewx.engine

def random_string(length=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])

config_dict = f"""

WEEWX_ROOT = tmp

[Station]
    altitude = 495, foot
    latitude = 0.0
    longitude = 0.0
    station_type = Simulator

[Simulator]
    driver = user.tests.e2e.simulator

[StdReport]

[StdArchive]
    archive_interval = 60
    archive_delay = 1

[DataBindings]
    [[wx_binding]]
        database = archive_sqlite
        table_name = archive
        manager = weewx.manager.DaySummaryManager
        schema = schemas.wview_extended.schema

[Databases]
    [[archive_sqlite]]
        database_name = :memory:
        database_type = SQLite

[DatabaseTypes]
    [[SQLite]]
        driver = weedb.sqlite
        # Directory in which database files are located, relative to WEEWX_ROOT
        SQLITE_ROOT = archive

[Engine]
    [[Services]]
        prep_services = weewx.engine.StdTimeSynch
        data_services = user.MQTTSubscribe.MQTTSubscribeService
        process_services = weewx.engine.StdConvert, weewx.engine.StdCalibrate, weewx.engine.StdQC, weewx.wxservices.StdWXCalculate
        xtype_services = weewx.wxxtypes.StdWXXTypes, weewx.wxxtypes.StdPressureCooker, weewx.wxxtypes.StdRainRater, weewx.wxxtypes.StdDelta
        archive_services = weewx.engine.StdArchive
        restful_services = weewx.restx.StdStationRegistry, weewx.restx.StdWunderground, weewx.restx.StdPWSweather, weewx.restx.StdCWOP, weewx.restx.StdWOW, weewx.restx.StdAWEKAS
        report_services = weewx.engine.StdReport

[MQTTSubscribeService]
    [[topics]]
        [[[message]]]
            type = individual
        [[[{random_string()}]]]
            ignore_start_time = True # at least while developing
            ignore_end_time = True # at least while developing
            adjust_start_time = 1 # at least while developing
            [[[[outTemp]]]]
                name = outTemp
                expires_after = 0

""" # noqa

class test_record_cache(unittest.TestCase):
    def test_new_loop_packet(self):
        with mock.patch('user.MQTTSubscribe.RecordCache') as mock_cache:
            max_archive_records = 0
            config = configobj.ConfigObj(StringIO(config_dict))
            config['Simulator']['max_archive_records'] = max_archive_records
            config['MQTTSubscribeService']['topics'][random_string()] = {}

            SUT = weewx.engine.StdEngine(config)
            mock_cache_instance = mock_cache.return_value

            with self.assertRaises(Exception):
                SUT.run()
                print("exception")

            mock_cache_instance.invalidate_value.assert_called()
            self.assertEqual(mock_cache_instance.invalidate_value.call_count, SUT.console.count_loop_packets)

    def test_observation_not_in_archive_record(self):
        with mock.patch('user.MQTTSubscribe.RecordCache') as mock_cache:
            max_archive_records = 1
            config = configobj.ConfigObj(StringIO(config_dict))
            config['Simulator']['max_archive_records'] = max_archive_records
            config['Simulator']['remove_fields_from_archive_record'] = 'outTemp'

            SUT = weewx.engine.StdEngine(config)
            mock_cache_instance = mock_cache.return_value
            mock_cache_instance.get_value.return_value = 0

            with self.assertRaises(Exception):
                SUT.run()
                print("exception")

            mock_cache_instance.invalidate_value.assert_called()
            self.assertEqual(mock_cache_instance.invalidate_value.call_count, SUT.console.count_loop_packets)

            mock_cache_instance.update_value.assert_not_called()

            mock_cache_instance.get_value.assert_called()
            self.assertEqual(mock_cache_instance.get_value.call_count, max_archive_records)

    def test_observation_in_archive_record(self):
        with mock.patch('user.MQTTSubscribe.RecordCache') as mock_cache:
            max_archive_records = 1
            config = configobj.ConfigObj(StringIO(config_dict))
            config['Simulator']['max_archive_records'] = max_archive_records

            SUT = weewx.engine.StdEngine(config)
            mock_cache_instance = mock_cache.return_value

            with self.assertRaises(Exception):
                SUT.run()

            mock_cache_instance.invalidate_value.assert_called()
            self.assertEqual(mock_cache_instance.invalidate_value.call_count, SUT.console.count_loop_packets)

            mock_cache_instance.update_value.assert_called()
            self.assertEqual(mock_cache_instance.update_value.call_count, max_archive_records)

            mock_cache_instance.get_value.assert_not_called()

if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    # test_suite.addTest(test_record_cache('test_observation_not_in_archive_record'))
    # test_suite.addTest(test_record_cache('test_observation_in_archive_record'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
