#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import print_function

import unittest

from test_get_data import TestGetData
from test_driver import TestDriver
from test_get_accumulated_data import TestAccumulatedData
from test_service import TestService

class TestGetDataExampleMessageCallbackProvider(TestGetData):
    #@unittest.skip("")
    def test_xml(self):
        with open("bin/user/tests/integ/data/example_callback_provider.json") as file_pointer:
            self.runit('xml', file_pointer, check_results=True)

class TestDriverExamoleMessageCallbackProvider(TestDriver):
    #@unittest.skip("")
    def test_xml(self):
        with open("bin/user/tests/integ/data/example_callback_provider.json") as file_pointer:
            self.runit('xml', file_pointer, check_results=True)

class TestAccunulatedDataExampleMessageCallbackProvider(TestAccumulatedData):
    #@unittest.skip("")
    def test_xml(self):
        with open("bin/user/tests/integ/data/example_callback_provider.json") as file_pointer:
            self.runit('xml', file_pointer, check_results=True)

class TestServiceExampleMessageCallbackProvider(TestService):
    #@unittest.skip("")
    def test_xml(self):
        with open("bin/user/tests/integ/data/example_callback_provider.json") as file_pointer:
            self.runit('xml', file_pointer, check_results=True)

if __name__ == '__main__':
    test_suite = unittest.TestSuite()

    test_suite.addTest(TestGetDataExampleMessageCallbackProvider('test_xml'))
    test_suite.addTest(TestDriverExamoleMessageCallbackProvider('test_xml'))
    test_suite.addTest(TestAccunulatedDataExampleMessageCallbackProvider('test_xml'))
    test_suite.addTest(TestServiceExampleMessageCallbackProvider('test_xml'))

    unittest.TextTestRunner().run(test_suite)
