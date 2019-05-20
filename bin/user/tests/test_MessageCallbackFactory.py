from __future__ import with_statement

import unittest
import mock

from user.MQTTSubscribe import MessageCallbackFactory

class TestGetDefaultCallBacks(unittest.TestCase):
    def test_get_unknown_payload_type(self):
        payload_type = 'foobar'

        SUT = MessageCallbackFactory()

        #callback = SUT.get_callback(payload_type)

        #print(callback)

    def test_get_individual_payload_type(self):
        payload_type = 'individual'

        SUT = MessageCallbackFactory()

        callback = SUT.get_callback(payload_type)
        self.assertEqual(callback, SUT._on_message_individual)

    def test_get_json_payload_type(self):
        payload_type = 'json'

        SUT = MessageCallbackFactory()

        callback = SUT.get_callback(payload_type)
        self.assertEqual(callback, SUT._on_message_json)

    def test_get_json_payload_type(self):
        payload_type = 'keyword'

        SUT = MessageCallbackFactory()

        callback = SUT.get_callback(payload_type)
        self.assertEqual(callback, SUT._on_message_keyword)

class Testadd_callback(unittest.TestCase):
    def on_message_test_callback():
        pass

    def test_add_callback(self):
        payload_type = 'foobar'

        SUT = MessageCallbackFactory()

        SUT.add_callback(payload_type, self.on_message_test_callback)

        callbacks = SUT.Callbacks
        self.assertTrue(payload_type in callbacks)
        self.assertEqual(callbacks[payload_type], self.on_message_test_callback)

if __name__ == '__main__':
    unittest.main()