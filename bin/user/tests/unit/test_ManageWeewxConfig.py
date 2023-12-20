#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import configobj
import importlib
import sys
import types

import unittest

from test_weewx_stubs import random_string
import test_weewx_stubs
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import ManageWeewxConfig

class TestObservationConfig(unittest.TestCase):
    def setUp(self):
        # reset stubs for every test
        test_weewx_stubs.setup_stubs()
        import user.MQTTSubscribe
        importlib.reload(user.MQTTSubscribe)

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

    def test_configure_observation(self):

        name = random_string(10)
        value = random_string(10)
        config_dict = {}

        config_dict = {}
        config_dict['observations'] = {}
        config_dict['observations'][name] = value

        config = configobj.ConfigObj(config_dict)

        SUT = ManageWeewxConfig()
        SUT.add_observation_to_unit_dict(config)

        self.assertEqual(len(sys.modules['weewx'].units.obs_group_dict), 3)
        self.assertIn(name, sys.modules['weewx'].units.obs_group_dict)
        self.assertEqual(value, sys.modules['weewx'].units.obs_group_dict[name])

    def test_missing_group(self):
        unit = random_string(5)
        config_dict = {}

        config_dict = {}
        config_dict['units'] = {}
        config_dict['units'][unit] = {}

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            SUT = ManageWeewxConfig()
            SUT.update_unit_config(config)

        self.assertEqual(error.exception.args[0], f"{unit} is missing a group.")

    def test_missing_unit_system(self):
        unit = random_string(5)
        group = random_string(10)
        config_dict = {}
        config_dict = {}
        config_dict['units'] = {}
        config_dict['units'][unit] = {}
        config_dict['units'][unit]['group'] = group

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            SUT = ManageWeewxConfig()
            SUT.update_unit_config(config)

        self.assertEqual(error.exception.args[0], f"{unit} is missing an unit_system.")

    def test_invalid_unit_system(self):
        unit = random_string(5)
        group = random_string(10)
        unit_system = random_string(5)
        config_dict = {}
        config_dict = {}
        config_dict['units'] = {}
        config_dict['units'][unit] = {}
        config_dict['units'][unit]['group'] = group
        config_dict['units'][unit]['unit_system'] = unit_system

        config = configobj.ConfigObj(config_dict)

        with self.assertRaises(ValueError) as error:
            SUT = ManageWeewxConfig()
            SUT.update_unit_config(config)

        self.assertEqual(error.exception.args[0], f"Invalid unit_system {unit_system} for {unit}.")

    def test_configure_default_label(self):
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'us'
        label = random_string(10)
        config_dict = {}
        config_dict = {}
        config_dict['units'] = {}
        config_dict['units'][unit] = {}
        config_dict['units'][unit]['group'] = group
        config_dict['units'][unit]['unit_system'] = unit_system
        config_dict['units'][unit]['label'] = label

        config = configobj.ConfigObj(config_dict)

        default_unit_label_dict = {}
        default_unit_label_dict[unit] = label

        SUT = ManageWeewxConfig()
        SUT.update_unit_config(config)

        self.assertDictEqual(sys.modules['weewx'].units.default_unit_label_dict, default_unit_label_dict)

    def test_configure_default_format(self):
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'us'
        format_value = random_string(10)
        config_dict = {}
        config_dict = {}
        config_dict['units'] = {}
        config_dict['units'][unit] = {}
        config_dict['units'][unit]['group'] = group
        config_dict['units'][unit]['unit_system'] = unit_system
        config_dict['units'][unit]['format'] = format_value

        config = configobj.ConfigObj(config_dict)

        default_unit_format_dict = {}
        default_unit_format_dict[unit] = format_value

        SUT = ManageWeewxConfig()
        SUT.update_unit_config(config)

        self.assertDictEqual(sys.modules['weewx'].units.default_unit_format_dict, default_unit_format_dict)

    def test_configure_conversion(self):
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'us'
        to_unit = random_string(5)
        config_dict = {}
        config_dict['units'] = {}
        config_dict['units'][unit] = {}
        config_dict['units'][unit]['group'] = group
        config_dict['units'][unit]['unit_system'] = unit_system
        config_dict['units'][unit]['conversion'] = {}
        config_dict['units'][unit]['conversion'][to_unit] = 'lambda x: x / 1'

        config = configobj.ConfigObj(config_dict)

        conversionDict = {}
        conversionDict['unit_name'] = {'foobar': lambda x: x / 1}
        conversionDict[unit] = {to_unit: lambda x: x / 1}

        SUT = ManageWeewxConfig()
        SUT.update_unit_config(config)

        self.assertEqual(len(sys.modules['weewx'].units.conversionDict), len(conversionDict))
        for key, value in conversionDict.items():
            self.assertIn(key, sys.modules['weewx'].units.conversionDict)
            self.assertEqual(len(sys.modules['weewx'].units.conversionDict[key]), len(value))
            for key2 in value:
                self.assertIn(key2, sys.modules['weewx'].units.conversionDict[key])
                self.assertIsInstance(sys.modules['weewx'].units.conversionDict[key][key2], types.FunctionType)

    def test_unit_system_us(self):
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'us'
        config_dict = {}
        config_dict['units'] = {}
        config_dict['units'][unit] = {}
        config_dict['units'][unit]['group'] = group
        config_dict['units'][unit]['unit_system'] = unit_system
        config_dict['units'][unit]['conversion'] = {}

        config = configobj.ConfigObj(config_dict)

        units = test_weewx_stubs.ListOfDicts({})
        units.extend({group: unit})

        SUT = ManageWeewxConfig()
        SUT.update_unit_config(config)

        self.assertEqual(len(sys.modules['weewx'].units.USUnits), len(units))
        for key in units:
            self.assertIn(key, sys.modules['weewx'].units.USUnits)
            self.assertEqual(units[key], sys.modules['weewx'].units.USUnits[key])

    def test_unit_system_metric(self):
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'metric'
        config_dict = {}
        config_dict['units'] = {}
        config_dict['units'][unit] = {}
        config_dict['units'][unit]['group'] = group
        config_dict['units'][unit]['unit_system'] = unit_system
        config_dict['units'][unit]['conversion'] = {}

        config = configobj.ConfigObj(config_dict)

        units = test_weewx_stubs.ListOfDicts({})
        units.extend({group: unit})

        SUT = ManageWeewxConfig()
        SUT.update_unit_config(config)

        self.assertEqual(len(sys.modules['weewx'].units.MetricUnits), len(units))
        for key in units:
            self.assertIn(key, sys.modules['weewx'].units.MetricUnits)
            self.assertEqual(units[key], sys.modules['weewx'].units.MetricUnits[key])

    def test_unit_system_metricwx(self):
        unit = random_string(5)
        group = random_string(10)
        unit_system = 'metricwx'
        config_dict = {}
        config_dict['units'] = {}
        config_dict['units'][unit] = {}
        config_dict['units'][unit]['group'] = group
        config_dict['units'][unit]['unit_system'] = unit_system
        config_dict['units'][unit]['conversion'] = {}

        config = configobj.ConfigObj(config_dict)

        units = test_weewx_stubs.ListOfDicts({})
        units.extend({group: unit})

        SUT = ManageWeewxConfig()
        SUT.update_unit_config(config)

        self.assertEqual(len(sys.modules['weewx'].units.MetricWXUnits), len(units))
        for key in units:
            self.assertIn(key, sys.modules['weewx'].units.MetricWXUnits)
            self.assertEqual(units[key], sys.modules['weewx'].units.MetricWXUnits[key])


if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestInitialization('test_connect_exception'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
