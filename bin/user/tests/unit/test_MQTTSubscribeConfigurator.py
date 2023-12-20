#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position

import unittest
import mock

import argparse
import sys

import test_weewx_stubs
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import Configurator

class TestUpdateConfig(unittest.TestCase):
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

    @unittest.skip("This is really not a unit test, it is testing weeutil.config.conditional_merge")
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

        expected_config = '''[MQTTSubscribeDriver]
    [[topic]]
        [[[field-1]]]
            name = rename-1a
        [[[field-2]]]
        [[[field-3]]]'''

        with mock.patch('user.MQTTSubscribe.weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

        config_items = []
        SUT.config_dict.filename = None
        for item in SUT.config_dict.write():
            config_items.append(item.decode('utf-8'))

        self.assertEqual(config_items, expected_config.split('\n'))

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

        SUT.config_dict.filename = None

        self.assertEqual(SUT. config_dict.write(), [])

    @unittest.skip("This tests uses weeutil.config.deep_copy")
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

        expected_config = '''[MQTTSubscribeDriver]
    [[topic]]
        [[[field-1]]]
            name = rename-1b
        [[[field-3]]]'''

        with mock.patch('weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

        config_items = []
        SUT.config_dict.filename = None
        for item in SUT.config_dict.write():
            config_items.append(item.decode('utf-8'))

        self.assertEqual(config_items, expected_config.split('\n'))

    @unittest.skip("This is really not a unit test, it is testing weeutil.config.merge_config")
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

        expected_config = '''[MQTTSubscribeDriver]
    [[topic]]
        [[[field-1]]]
            name = rename-1b
        [[[field-2]]]
        [[[field-3]]]'''

        with mock.patch('weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

        config_items = []
        SUT.config_dict.filename = None
        for item in SUT.config_dict.write():
            config_items.append(item.decode('utf-8'))

        self.assertEqual(config_items, expected_config.split('\n'))

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestUpdateFrom('test_update_from'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
