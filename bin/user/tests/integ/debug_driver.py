# pylint: disable=missing-docstring

import unittest

from test_driver import TestDriver

class DebugAccumulated(TestDriver):
    #@unittest.skip("")
    def debug_individual(self):
        with open("bin/user/tests/integ/data/debug.json") as file_pointer:
            self.runit('individual', file_pointer)

    @unittest.skip("")
    def debug_json(self):
        with open("bin/user/tests/integ/data/debug.json") as file_pointer:
            self.runit('json', file_pointer)

    @unittest.skip("")
    def debug_keyword(self):
        with open("bin/user/tests/integ/data/debug.json") as file_pointer:
            self.runit('keyword', file_pointer)

if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(DebugAccumulated('debug_individual'))
    test_suite.addTest(DebugAccumulated('debug_json'))
    test_suite.addTest(DebugAccumulated('debug_keyword'))
    unittest.TextTestRunner().run(test_suite)
