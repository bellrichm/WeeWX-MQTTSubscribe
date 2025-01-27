#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

# Set up the stubs for paho mqtt
# These need to done very early. Definitely before importing MQTTSubscribe
import mqttstubs # pylint: disable=unused-import

import unittest
import mock

import configobj
import random
import string
from io import StringIO

import user.MQTTSubscribe
import weewx.engine

def random_string(length=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)]) # pylint: disable=unused-variable

config_dict = \
f"""

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
        report_services = weewx.engine.StdPrint, weewx.engine.StdReport        

[MQTTSubscribeService]
    [[topics]]
        [[[message]]]
            type = individual
        [[[{random_string()}]]]
            ignore_start_time = True # at least while developing 
            ignore_end_time = True # at least while developing
            adjust_start_time = 1 # at least while developing

"""

class test_all(unittest.TestCase):
    def test_one(self):
        mock_StdEngine = mock.Mock()

        SUT = user.MQTTSubscribe.MQTTSubscribeService(mock_StdEngine, configobj.ConfigObj(StringIO(config_dict)))

        SUT.shutDown()

    def test_two(self):
        SUT = weewx.engine.StdEngine(configobj.ConfigObj(StringIO(config_dict)))

        SUT.run()

        #SUT.shutDown()

if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    #test_suite.addTest(test_all('test_one'))
    test_suite.addTest(test_all('test_two'))
    unittest.TextTestRunner().run(test_suite)

    #unittest.main(exit=False)
    print("done")
