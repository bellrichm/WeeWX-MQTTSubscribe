# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring

from __future__ import with_statement

import unittest
import mock

import random
import string

from user.MQTTSubscribe import AbstractMessageCallbackProvider, Logger, TopicManager

class TestTest(unittest.TestCase):
    def test_test(self):
        print("start")
        mock_logger = mock.Mock(spec=Logger)
        mock_manager = mock.Mock(spec=TopicManager)

        with mock.patch('weewx.units') as mock_weewx_units:
            SUT = AbstractMessageCallbackProvider(mock_logger, mock_manager)

            mock_weewx_units.getStandardUnitType.return_value = ('foo', 'bar')
            converted_value = round(random.uniform(10, 100), 2)
            mock_weewx_units.convert.return_value = (converted_value, 'foo', 'bar')

            orig_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable
            previous_value = round(random.uniform(0, 9), 2)

            SUT.previous_values = {
                orig_name: previous_value
            }

            new_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])  # pylint: disable=unused-variable

            fields = {
                orig_name: {
                    'units': ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),  # pylint: disable=unused-variable
                    'contains_total': True,
                    'name': new_name
                }
            }

            orig_value = round(random.uniform(10, 100), 2)
            unit_system = 99

            (updated_name, updated_value) = SUT._update_data(fields, orig_name, orig_value, unit_system) # pylint: disable=protected-access

            print("%s %f" % (updated_name, updated_value))
            print("%s %f" % (orig_name, orig_value))
            print("%f" % (converted_value))
            self.assertEqual(updated_name, new_name)
            self.assertEqual(updated_value, converted_value - previous_value)
            self.assertEqual(SUT.previous_values[orig_name], converted_value)

            print("done")

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestInitialization('test_connect_exception'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
