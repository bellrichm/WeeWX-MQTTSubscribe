#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=eval-used

import unittest
import mock

import random
import sys

import test_weewx_stubs # needed to import AbstractMessageCallbackProvider pylint: disable=unused-import
from test_weewx_stubs import random_string
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import AbstractMessageCallbackProvider, Logger, TopicManager

# todo - mock?
def to_float(x):
    if isinstance(x, str) and x.lower() == 'none':
        x = None
    return float(x) if x is not None else None

class TestTest(unittest.TestCase):
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

    def test_contains_total_invalid_previous_value(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        with mock.patch('weewx.units'):
            SUT = AbstractMessageCallbackProvider(mock_logger, mock_manager)

            default_field_conversion_func = {
                'source': 'lambda x: to_float(x)',
                'compiled': eval('lambda x: to_float(x)')
            }
            orig_name = random_string()
            previous_value = round(random.uniform(101, 200), 2)

            SUT.previous_values = {
                orig_name: previous_value
            }

            fields = {
                orig_name: {
                    'contains_total': True
                }
            }

            orig_value = round(random.uniform(10, 100), 2)
            unit_system = random.randint(1, 99)

            (updated_name, updated_value) = SUT._update_data(orig_name, orig_value, fields, default_field_conversion_func, unit_system) # pylint: disable=protected-access

            self.assertEqual(updated_name, orig_name)
            self.assertIsNone(updated_value)
            self.assertEqual(SUT.previous_values[orig_name], orig_value)

    def test_contains_total_no_previous_value(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        with mock.patch('weewx.units'):
            SUT = AbstractMessageCallbackProvider(mock_logger, mock_manager)

            default_field_conversion_func = {
                'source': 'lambda x: to_float(x)',
                'compiled': eval('lambda x: to_float(x)')
            }
            orig_name = random_string()

            fields = {
                orig_name: {
                    'contains_total': True
                }
            }

            orig_value = round(random.uniform(10, 100), 2)
            unit_system = random.randint(1, 99)

            (updated_name, updated_value) = SUT._update_data(orig_name, orig_value, fields, default_field_conversion_func, unit_system) # pylint: disable=protected-access

            self.assertEqual(updated_name, orig_name)
            self.assertIsNone(updated_value)
            self.assertEqual(SUT.previous_values[orig_name], orig_value)

    def test_contains_total(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        with mock.patch('weewx.units'):
            SUT = AbstractMessageCallbackProvider(mock_logger, mock_manager)

            default_field_conversion_func = {
                'source': 'lambda x: to_float(x)',
                'compiled': eval('lambda x: to_float(x)')
            }
            orig_name = random_string()
            previous_value = round(random.uniform(0, 9), 2)

            SUT.previous_values = {
                orig_name: previous_value
            }

            fields = {
                orig_name: {
                    'contains_total': True
                }
            }

            orig_value = round(random.uniform(10, 100), 2)
            unit_system = random.randint(1, 99)

            (updated_name, updated_value) = SUT._update_data(orig_name, orig_value, fields, default_field_conversion_func, unit_system) # pylint: disable=protected-access

            self.assertEqual(updated_name, orig_name)
            self.assertEqual(updated_value, orig_value - previous_value)
            self.assertEqual(SUT.previous_values[orig_name], orig_value)

    def test_converting_value(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        with mock.patch('user.MQTTSubscribe.weewx.units') as mock_weewx_units:
            SUT = AbstractMessageCallbackProvider(mock_logger, mock_manager)

            default_field_conversion_func = {
                'source': 'lambda x: to_float(x)',
                'compiled': eval('lambda x: to_float(x)')
            }

            mock_weewx_units.getStandardUnitType.return_value = (random_string(), random_string())
            converted_value = round(random.uniform(10, 100), 2)
            mock_weewx_units.convert.return_value = (converted_value, random_string(), random_string())

            orig_name = random_string()

            fields = {
                orig_name: {
                    'units': random_string(),
                }
            }

            orig_value = round(random.uniform(10, 100), 2)
            unit_system = 99

            (updated_name, updated_value) = SUT._update_data(orig_name, orig_value, fields, default_field_conversion_func, unit_system) # pylint: disable=protected-access

            self.assertEqual(updated_name, orig_name)
            self.assertEqual(updated_value, converted_value)
            self.assertEqual(SUT.previous_values, {})

if __name__ == '__main__':
    unittest.main(exit=False)
