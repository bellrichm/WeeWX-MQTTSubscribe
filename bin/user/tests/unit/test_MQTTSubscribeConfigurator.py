#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=wrong-import-order

import unittest
import mock

import argparse

from user.MQTTSubscribe import Configurator

class TestUpdateConfig(unittest.TestCase):
    #@unittest.skip("Need to figure out what to do about mocking WeeWX functions")
    def test_add_from(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.validate = None
        options.no_backup = True
        options.add_from = 'bin/user/tests/unit/data/mqttsubscribe.conf'
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = 'bin/user/tests/unit/data/output.conf'
        options.conf = 'bin/user/tests/unit/data/weewx.conf'

        with mock.patch('weeutil.config.conditional_merge'):
            with mock.patch('weecfg.save'):
                SUT = Configurator(None, options)

                SUT.run()

    #@unittest.skip("Need to figure out what to do about mocking WeeWX functions")
    def test_remove(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = True
        options.replace_with = None
        options.update_from = None
        options.output = 'bin/user/tests/unit/data/output.conf'
        options.conf = 'bin/user/tests/unit/data/weewx.conf'

        with mock.patch('weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

    #@unittest.skip("Need to figure out what to do about mocking WeeWX functions")
    def test_replace_with(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = None
        options.replace_with = 'bin/user/tests/unit/data/mqttsubscribe.conf'
        options.update_from = None
        options.output = 'bin/user/tests/unit/data/output.conf'
        options.conf = 'bin/user/tests/unit/data/weewx.conf'

        with mock.patch('weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

    #@unittest.skip("Need to figure out what to do about mocking WeeWX functions")
    def test_update_from(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = 'bin/user/tests/unit/data/mqttsubscribe.conf'
        options.output = 'bin/user/tests/unit/data/output.conf'
        options.conf = 'bin/user/tests/unit/data/weewx.conf'

        with mock.patch('weeutil.config.merge_config'):
            with mock.patch('weecfg.save'):
                SUT = Configurator(None, options)

                SUT.run()

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestUpdateFrom('test_update_from'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
