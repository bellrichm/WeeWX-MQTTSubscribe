import unittest
import mock

import time
import paho.mqtt.client
import random
import weewx
from collections import deque

from weewx.engine import StdEngine
from user.MQTTSubscribe import MQTTSubscribe, MQTTSubscribeService

class Msg():
    pass

class TestStringMethods(unittest.TestCase):

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

        payload_dict = {
            'inTemp': random.uniform(1, 100),
            'outTemp':random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': current_time
        }
        test.queue.append(payload_dict, )

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.weewx.units.to_std_system') as mock_to_std_system:
                with mock.patch('user.MQTTSubscribe.weewx.accum.Accum') as mock_Accum:
                    mock_to_std_system.return_value = payload_dict

                    type(mock_Accum.return_value).isEmpty = mock.PropertyMock(return_value = False)
                    type(mock_Accum.return_value).getRecord = mock.Mock(return_value=payload_dict)

                    test.new_archive_record(new_archive_record_event)

                    print(mock_client)
                    print(mock_to_std_system)
                    print(mock_Accum)
        print("test 03")
        test.shutDown()


if __name__ == '__main__':
    #unittest.main()

    suite = unittest.TestLoader().loadTestsFromTestCase(TestStringMethods)
    unittest.TextTestRunner(verbosity=2).run(suite)
