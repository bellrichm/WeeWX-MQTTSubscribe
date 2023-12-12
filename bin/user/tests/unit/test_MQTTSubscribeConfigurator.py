#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access

import unittest

import argparse

from user.MQTTSubscribe import Configurator

class TestUpdateFrom(unittest.TestCase):
    def test_update_from(self):
        options = argparse.Namespace()
        options.type = 'driver'
        options.create_example = None
        options.export = None
        options.print_configspec = None
        options.validate = None
        options.no_backup = None
        options.add_from = None
        options.remove = None
        options.replace_with = None
        options.update_from = 'bin/user/tests/unit/data/mqttsubscribe.conf'
        options.output = 'bin/user/tests/unit/data/output.conf'
        options.conf = 'bin/user/tests/unit/data/weewx.conf'

        SUT = Configurator(None, options)

        SUT.run()

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestUpdateFrom('test_update_from'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
