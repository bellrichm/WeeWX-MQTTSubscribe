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

import contextlib
import io

import argparse
import sys

import test_weewx_stubs
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import Configurator

class TestServiceArgParse(unittest.TestCase):
    def test_missing_args(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(dest='command')

        _ = Configurator.add_parsers(subparsers)

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                _ = parser.parse_args(['configure', 'service'])

        self.assertEqual(error.exception.code, 2)
        self.assertIn("configure service: error: the following arguments are required: --conf", stderr.getvalue())
        print("done")

class TestInitConfigurator(unittest.TestCase):
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

    def test_missing_primary_option(self):
        options = argparse.Namespace()
        options.type = None
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.enable = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = None

        mock_parser = mock.Mock()
        _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("Either 'service|driver' or '--create-example' is required.")

        print("done")

    @unittest.skip("")
    def test(self):
        options = argparse.Namespace()
        options.type = 'service'
        options.create_example = None
        options.export = 'bin/user/tests/data/output.conf'
        options.print_configspec = 'bin/user/tests/data/output.conf'
        options.enable = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = None

        mock_parser = mock.Mock()
        _ = Configurator(mock_parser, options)

        #mock_parser.error.assert_called_once_with("Either 'service|driver' or '--create-example' is required.")

        print("done")

class TestRunConfigurator(unittest.TestCase):
    '''
    These are not 'real' tests. The results are not checked. The only check that the 
    options run to completion.
    '''
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

    def test_create_example(self):
        options = argparse.Namespace()
        options.type = None
        options.create_example = 'bin/user/tests/data/output.conf'
        options.export = None
        options.print_configspec = None
        options.enable = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = 'bin/user/tests/data/output.conf'
        options.conf = None

        with mock.patch('user.MQTTSubscribe.weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

    def test_export(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = 'bin/user/tests/data/output.conf'
        options.print_configspec = None
        options.enable = None
        options.validate = None
        options.no_backup = None
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = 'bin/user/tests/data/weewx.conf'

        with mock.patch('user.MQTTSubscribe.weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

    def test_print_configspec(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = 'bin/user/tests/data/output.conf'
        options.enable = None
        options.validate = None
        options.no_backup = None
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = None

        with mock.patch('user.MQTTSubscribe.weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

    def test_validate(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.enable = None
        options.validate = True
        options.no_backup = None
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = 'bin/user/tests/data/weewx.conf'

        with mock.patch('user.MQTTSubscribe.weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

    def test_add_from(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.enable = None
        options.validate = None
        options.no_backup = True
        options.add_from = 'bin/user/tests/data/mqttsubscribe.conf'
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = 'bin/user/tests/data/output.conf'
        options.conf = 'bin/user/tests/data/weewx.conf'

        with mock.patch('user.MQTTSubscribe.weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

    def test_remove(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.enable = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = True
        options.replace_with = None
        options.update_from = None
        options.output = 'bin/user/tests/data/output.conf'
        options.conf = 'bin/user/tests/data/weewx.conf'

        with mock.patch('weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

    def test_replace_with(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.enable = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = None
        options.replace_with = 'bin/user/tests/data/mqttsubscribe.conf'
        options.update_from = None
        options.output = 'bin/user/tests/data/output.conf'
        options.conf = 'bin/user/tests/data/weewx.conf'

        with mock.patch('weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

    def test_update_from(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.enable = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = 'bin/user/tests/data/mqttsubscribe.conf'
        options.output = 'bin/user/tests/data/output.conf'
        options.conf = 'bin/user/tests/data/weewx.conf'

        with mock.patch('weecfg.save'):
            SUT = Configurator(None, options)

            SUT.run()

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestUpdateFrom('test_update_from'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
