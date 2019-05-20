from __future__ import with_statement

import unittest
import mock

from user.MQTTSubscribe import MessageCallbackFactory


class Testadd_callback(unittest.TestCase):
    def on_message_test_callback():
        pass

    def test_callback(self):
        payload_type = 'foobar'

        SUT = MessageCallbackFactory()

        SUT.add_callback(payload_type, self.on_message_test_callback)

        print(SUT.Callbacks)


if __name__ == '__main__':
    unittest.main()