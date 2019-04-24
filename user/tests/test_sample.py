import unittest
import mock

import time
import paho.mqtt.client as mqtt
import weewx
from collections import deque

from weewx.engine import StdEngine
from user.MQTTSubscribe import MQTTSubscribe, MQTTSubscribeService

class Msg():
    pass

class TestStringMethods(unittest.TestCase):

    def test_first(self):
        #print("test 01")
        m = mock.Mock(spec=mqtt.Client)
        queue = deque()
        test = MQTTSubscribe(
            m,
            queue,
            None,
            {},
            1,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None
        )
        self.assertEquals(m.on_message, test.on_message)

        msg = Msg()
        msg.topic = 'weather/foo'
        msg.payload = 'bar'
        data = test.on_message_individual(
            None,
            None,
            msg
        )
        #print("test 02")

    def test_second(self):
        print("test 01")
        m = mock.Mock(spec=StdEngine)
        test = MQTTSubscribeService(
            m,
            {}
        )
        print("test 02")
        current_time = int(time.time() + 0.5)
        end_period_ts = (int(current_time / 300) + 1) * 300

        data = {}
        data['dateTime'] = end_period_ts
        data['usUnits'] = 1
        data['interval'] = 5
        new_archive_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                    record=data,
                                                    origin='hardware')

        test.new_archive_record(new_archive_record_event)
        print("test 03")
        test.shutDown()


if __name__ == '__main__':
    #unittest.main()

    suite = unittest.TestLoader().loadTestsFromTestCase(TestStringMethods)
    unittest.TextTestRunner(verbosity=2).run(suite)
