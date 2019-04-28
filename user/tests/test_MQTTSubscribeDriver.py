from __future__ import with_statement

import unittest
import mock

import paho.mqtt.client
import random
import time
import threading
import weewx

from user.MQTTSubscribe import MQTTSubscribeDriver

class GetLoopPacketThread(threading.Thread):
    def __init__(self, driver):
        threading.Thread.__init__(self)
        self.driver = driver
        self.packet = None

    def run(self):
        gen=self.driver.genLoopPackets()
        while not self.packet:
            self.packet=next(gen)

class TestgenLoopPackets(unittest.TestCase):
    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def test_queue_empty(self):
        current_time = int(time.time() + 0.5)
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': current_time
        }

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                SUT = MQTTSubscribeDriver(self.mock_StdEngine)
                thread = GetLoopPacketThread(SUT)
                thread.start()

                # wait for at least one sleep cycle
                while mock_time.sleep.call_count <= 0:
                    time.sleep(1)

                SUT.queue.append(queue_data, )

                # wait for queue to be processed
                while not thread.packet:
                    time.sleep(1)

                mock_time.sleep.assert_called()
                self.assertDictEqual(thread.packet, queue_data)

    def test_queue(self):
        current_time = int(time.time() + 0.5)
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': current_time
        }

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                SUT = MQTTSubscribeDriver(self.mock_StdEngine)

                SUT.queue.append(queue_data, )
                gen=SUT.genLoopPackets()
                packet=next(gen)

                mock_time.sleep.assert_not_called()
                self.assertDictEqual(packet, queue_data)

class TestgenArchiveRecords(unittest.TestCase):

    mock_StdEngine = mock.Mock(spec=weewx.engine.StdEngine)

    def test_empty_queue(self):
        current_time = int(time.time() + 0.5)
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': current_time
        }

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            SUT = MQTTSubscribeDriver(self.mock_StdEngine)
            record = None

            gen=SUT.genArchiveRecords(0)
            try:
                record=next(gen)
            except StopIteration:
                pass

            self.assertIsNone(record)

    def test_queue_element_in_future(self):
        current_time = int(time.time() + 0.5)
        inTemp = random.uniform(1, 100)
        outTemp = random.uniform(1, 100)

        queue_data = {
            'inTemp': inTemp,
            'outTemp':outTemp,
            'usUnits': 1,
            'dateTime': current_time
        }

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            SUT = MQTTSubscribeDriver(self.mock_StdEngine)
            record = None


            SUT.archive_queue.append(queue_data, )
            gen=SUT.genArchiveRecords(0)
            try:
                record=next(gen)
            except StopIteration:
                pass

            self.assertIsNone(record)

    def test_queue(self):
        queue_data = [{
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 0.5)
            },
            {
            'inTemp': random.uniform(1, 100),
            'outTemp': random.uniform(1, 100),
            'usUnits': 1,
            'dateTime': int(time.time() + 1.5)
            }]

        with mock.patch('paho.mqtt.client.Client', spec=paho.mqtt.client.Client) as mock_client:
            SUT = MQTTSubscribeDriver(self.mock_StdEngine)
            records = list()

            for q in queue_data:
                SUT.archive_queue.append(q, )

            gen=SUT.genArchiveRecords(int(time.time() + 10.5))
            try:
                while True:
                    records.append(next(gen))
            except StopIteration:
                pass

            self.assertListEqual(records, queue_data)


if __name__ == '__main__':
    unittest.main()