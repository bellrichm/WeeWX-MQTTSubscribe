#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=eval-used

from __future__ import with_statement

import unittest
import mock

import random
import string

import six
import test_weewx_stubs # needed to import AbstractMessageCallbackProvider pylint: disable=unused-import

from user.MQTTSubscribe import AbstractMessageCallbackProvider, Logger, TopicManager

# todo - mock?
def to_float(x):
    if isinstance(x, six.string_types) and x.lower() == 'none':
        x = None
    return float(x) if x is not None else None

class TestTest(unittest.TestCase):
    def test_contains_total_invalid_previous_value(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        with mock.patch('weewx.units'):
            SUT = AbstractMessageCallbackProvider(mock_logger, mock_manager)

            default_field_conversion_func = {
                'source': 'lambda x: to_float(x)',
                'compiled': eval('lambda x: to_float(x)')
            }
            orig_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
            previous_value = round(random.uniform(101, 200), 2)

            SUT.previous_values = {
                orig_name: previous_value
            }

            new_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

            fields = {
                orig_name: {
                    'contains_total': True
                }
            }

            orig_value = round(random.uniform(10, 100), 2)
            unit_system = random.randint(1, 99)

            (updated_name, updated_value) = SUT._update_data(fields, default_field_conversion_func, orig_name, orig_value, unit_system) # pylint: disable=protected-access

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
            orig_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

            new_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

            fields = {
                orig_name: {
                    'contains_total': True
                }
            }

            orig_value = round(random.uniform(10, 100), 2)
            unit_system = random.randint(1, 99)

            (updated_name, updated_value) = SUT._update_data(fields, default_field_conversion_func, orig_name, orig_value, unit_system) # pylint: disable=protected-access

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
            orig_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
            previous_value = round(random.uniform(0, 9), 2)

            SUT.previous_values = {
                orig_name: previous_value
            }

            new_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

            fields = {
                orig_name: {
                    'contains_total': True
                }
            }

            orig_value = round(random.uniform(10, 100), 2)
            unit_system = random.randint(1, 99)

            (updated_name, updated_value) = SUT._update_data(fields, default_field_conversion_func, orig_name, orig_value, unit_system) # pylint: disable=protected-access

            self.assertEqual(updated_name, orig_name)
            self.assertEqual(updated_value, orig_value - previous_value)
            self.assertEqual(SUT.previous_values[orig_name], orig_value)

    def test_converting_value(self):
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        with mock.patch('weewx.units') as mock_weewx_units:
            SUT = AbstractMessageCallbackProvider(mock_logger, mock_manager)

            default_field_conversion_func = {
                'source': 'lambda x: to_float(x)',
                'compiled': eval('lambda x: to_float(x)')
            }

            mock_weewx_units.getStandardUnitType.return_value = \
                (''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                 ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]))
            converted_value = round(random.uniform(10, 100), 2)
            mock_weewx_units.convert.return_value = (converted_value,
                                                     ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                                                     ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]))

            orig_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

            fields = {
                orig_name: {
                    'units': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),  # pylint: disable=unused-variable
                }
            }

            orig_value = round(random.uniform(10, 100), 2)
            unit_system = 99

            (updated_name, updated_value) = SUT._update_data(fields, default_field_conversion_func, orig_name, orig_value, unit_system) # pylint: disable=protected-access

            self.assertEqual(updated_name, orig_name)
            self.assertEqual(updated_value, converted_value)
            self.assertEqual(SUT.previous_values, {})

if __name__ == '__main__':
    unittest.main(exit=False)
