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
from test_weewx_stubs import random_string
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import Configurator

class TestEnableArgParse(unittest.TestCase):
    def test_driver_enable(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(dest='command')

        _ = Configurator.add_parsers(subparsers)

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                _ = parser.parse_args(['configure', 'driver', '--conf', random_string(), '--enable', 'true'])

        self.assertEqual(error.exception.code, 2)
        self.assertIn("error: unrecognized arguments: --enable", stderr.getvalue())

    #@unittest.skip("Not sure what to do with this test.")
    def test_service_enable(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(dest='command')

        _ = Configurator.add_parsers(subparsers)

        _ = parser.parse_args(['configure', 'service', '--conf', random_string(), '--enable', 'true'])


class TestConfArgParse(unittest.TestCase):
    def test_create_example_conf(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(dest='command')

        _ = Configurator.add_parsers(subparsers)

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                _ = parser.parse_args(['configure', '--create-example', '--conf', 'foo'])

        self.assertEqual(error.exception.code, 2)
        self.assertIn("--create-example: expected one argument", stderr.getvalue())

    def test_service_missing_conf(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(dest='command')

        _ = Configurator.add_parsers(subparsers)

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                _ = parser.parse_args(['configure', 'service'])

        self.assertEqual(error.exception.code, 2)
        self.assertIn("configure service: error: the following arguments are required: --conf", stderr.getvalue())

    def test_driver_missing_conf(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(dest='command')

        _ = Configurator.add_parsers(subparsers)

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                _ = parser.parse_args(['configure', 'driver'])

        self.assertEqual(error.exception.code, 2)
        self.assertIn("configure driver: error: the following arguments are required: --conf", stderr.getvalue())

class TestMutuallyExclusiveOptions(unittest.TestCase):
    def __init__(self, args):
        self.options = None
        super().__init__(args)

    def run_mutually_exclusive(self, mutually_exclusive, error_msg):
        self.options.extend(mutually_exclusive)

        parser = argparse.ArgumentParser()

        _ = Configurator.add_common_options(parser)

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                _ = parser.parse_args(self.options)

        self.assertEqual(error.exception.code, 2)
        self.assertIn(error_msg, stderr.getvalue())

class TestMutuallyExclusiveExportOptions(TestMutuallyExclusiveOptions):
    def setUp(self):
        self.options = ['--conf', random_string()]

    def test_export_mutually_exclusive_with_print_configspec(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--print-configspec', random_string()],
            "error: argument --print-configspec: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_validate(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--validate'],
            "error: argument --validate: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_add_from(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--add-from', random_string()],
            "error: argument --add-from: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_remove(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--remove'],
            "error: argument --remove: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --export"
        )

    def test_export_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--export', random_string(), '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --export"
        )

class TestMutuallyExclusivePrintConfigSpecOptions(TestMutuallyExclusiveOptions):
    def setUp(self):
        self.options = ['--conf', random_string()]

    def test_print_configspec_mutually_exclusive_with_validate(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--validate'],
            "error: argument --validate: not allowed with argument --print-configspec"
        )

    def test_print_configspec_mutually_exclusive_with_add_from(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--add-from', random_string()],
            "error: argument --add-from: not allowed with argument --print-configspec"
        )

    def test_print_configspec_mutually_exclusive_with_remove(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--remove'],
            "error: argument --remove: not allowed with argument --print-configspec"
        )

    def test_print_configspec_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --print-configspec"
        )

    def test_print_configspec_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--print-configspec', random_string(), '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --print-configspec"
        )

class TestMutuallyExclusiveValidateOptions(TestMutuallyExclusiveOptions):
    def setUp(self):
        self.options = ['--conf', random_string()]

    def test_validate_mutually_exclusive_with_add_from(self):
        self.run_mutually_exclusive(
            ['--validate', random_string(), '--add-from', random_string()],
            "error: argument --add-from: not allowed with argument --validate"
        )

    def test_validate_mutually_exclusive_with_remove(self):
        self.run_mutually_exclusive(
            ['--validate', '--remove'],
            "error: argument --remove: not allowed with argument --validate"
        )

    def test_validate_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--validate', '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --validate"
        )

    def test_validate_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--validate', '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --validate"
        )

class TestMutuallyExclusiveAddFromeOptions(TestMutuallyExclusiveOptions):
    def setUp(self):
        self.options = ['--conf', random_string()]

    def test_add_from_mutually_exclusive_with_remove(self):
        self.run_mutually_exclusive(
            ['--add-from', random_string(), '--remove'],
            "error: argument --remove: not allowed with argument --add-from"
        )

    def test_add_from_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--add-from', random_string(), '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --add-from"
        )

    def test_add_from_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--add-from', random_string(), '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --add-from"
        )

class TestMutuallyExclusiveRemoveOptions(TestMutuallyExclusiveOptions):
    def setUp(self):
        self.options = ['--conf', random_string()]

    def test_remove_mutually_exclusive_with_replace_with(self):
        self.run_mutually_exclusive(
            ['--remove', '--replace-with', random_string()],
            "error: argument --replace-with: not allowed with argument --remove"
        )

    def test_remove_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--remove', '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --remove"
        )

class TestMutuallyExclusiveReplaceWithOptions(TestMutuallyExclusiveOptions):
    def setUp(self):
        self.options = ['--conf', random_string()]

    def test_replace_with_mutually_exclusive_with_update_from(self):
        self.run_mutually_exclusive(
            ['--replace-with', random_string(), '--update-from', random_string()],
            "error: argument --update-from: not allowed with argument --replace-with"
        )

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

    def test_output_mutually_exclusive_with_export(self):
        options = argparse.Namespace()
        options.type = random_string()
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
        options.output = 'bin/user/tests/data/output.conf'
        options.conf = 'bin/user/tests/data/weewx.conf'

        mock_parser = mock.Mock()
        mock_parser.error = mock.Mock(side_effect=Exception("done"))
        with self.assertRaises(Exception):
            _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("'--output' is mutually exclusive with '--export'")

    def test_output_mutually_exclusive_with_print_configspec(self):
        options = argparse.Namespace()
        options.type = random_string()
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
        options.output = 'bin/user/tests/data/output.conf'
        options.conf = 'bin/user/tests/data/weewx.conf'

        mock_parser = mock.Mock()
        mock_parser.error = mock.Mock(side_effect=Exception("done"))
        with self.assertRaises(Exception):
            _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("'--output' is mutually exclusive with '--print-configspec'")

    def test_output_mutually_exclusive_with_validate(self):
        options = argparse.Namespace()
        options.type = random_string()
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
        options.output = 'bin/user/tests/data/output.conf'
        options.conf = 'bin/user/tests/data/weewx.conf'

        mock_parser = mock.Mock()
        mock_parser.error = mock.Mock(side_effect=Exception("done"))
        with self.assertRaises(Exception):
            _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("'--output' is mutually exclusive with '--validate'")

    def test_enable_mutually_exclusive_with_export(self):
        options = argparse.Namespace()
        options.type = 'service'
        options.create_example = None
        options.export = 'bin/user/tests/data/output.conf'
        options.print_configspec = None
        options.enable = True
        options.validate = None
        options.no_backup = None
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = None

        mock_parser = mock.Mock()
        mock_parser.error = mock.Mock(side_effect=Exception("done"))
        with self.assertRaises(Exception):
            _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("'--enable' is mutually exclusive with '--export'")

    def test_enable_mutually_exclusive_with_print_configspec(self):
        options = argparse.Namespace()
        options.type = 'service'
        options.create_example = None
        options.export = None
        options.print_configspec = 'bin/user/tests/data/output.conf'
        options.enable = True
        options.validate = None
        options.no_backup = None
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = 'bin/user/tests/data/weewx.conf'

        mock_parser = mock.Mock()
        mock_parser.error = mock.Mock(side_effect=Exception("done"))
        with self.assertRaises(Exception):
            _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("'--enable' is mutually exclusive with '--print-configspec'")

    def test_enable_mutually_exclusive_with_validate(self):
        options = argparse.Namespace()
        options.type = 'service'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.enable = True
        options.validate = True
        options.no_backup = None
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = 'bin/user/tests/data/weewx.conf'

        mock_parser = mock.Mock()
        mock_parser.error = mock.Mock(side_effect=Exception("done"))
        with self.assertRaises(Exception):
            _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("'--enable' is mutually exclusive with '--validate'")

    def test_no_backup_mutually_exclusive_with_export(self):
        options = argparse.Namespace()
        options.type = random_string()
        options.create_example = None
        options.export = 'bin/user/tests/data/output.conf'
        options.print_configspec = None
        options.enable = None
        options.validate = None
        options.no_backup = True
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = 'bin/user/tests/data/weewx.conf'

        mock_parser = mock.Mock()
        mock_parser.error = mock.Mock(side_effect=Exception("done"))
        with self.assertRaises(Exception):
            _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("'--no-backup' is mutually exclusive with '--export'")

    def test_no_backup_mutually_exclusive_with_print_configspec(self):
        options = argparse.Namespace()
        options.type = random_string()
        options.create_example = None
        options.export = None
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
        mock_parser.error = mock.Mock(side_effect=Exception("done"))
        with self.assertRaises(Exception):
            _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("'--no-backup' is mutually exclusive with '--print-configspec'")

    def test_no_backup_mutually_exclusive_with_validate(self):
        options = argparse.Namespace()
        options.type = random_string()
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.enable = None
        options.validate = True
        options.no_backup = True
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = None
        options.output = None
        options.conf = 'bin/user/tests/data/weewx.conf'

        mock_parser = mock.Mock()
        mock_parser.error = mock.Mock(side_effect=Exception("done"))
        with self.assertRaises(Exception):
            _ = Configurator(mock_parser, options)

        mock_parser.error.assert_called_once_with("'--no-backup' is mutually exclusive with '--validate'")

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

        SUT = Configurator(None, options)

        SUT.run()

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestUpdateFrom('test_update_from'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
