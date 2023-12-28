#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position

import unittest
import mock

import argparse
import time

import test_weewx_stubs
# setup stubs before importing MQTTSubscribe
test_weewx_stubs.setup_stubs()

from user.MQTTSubscribe import Simulator

class TestRunSimulator(unittest.TestCase):
    def test_simulate_service_archive(self):
        data = {}
        data['dateTime'] = 0

        frequency = 10

        now = time.time()
        current_time = int(now + 0.5)
        end_period_ts = (int(current_time / frequency) + 1) * frequency
        sleep_amount = end_period_ts - current_time

        options = argparse.Namespace()
        options.type = 'service'
        options.binding = 'archive'
        options.record_count = len(data)
        options.console = None
        options.conf = None

        options.verbose = None
        options.log_file = None
        options.units = 'US'
        options.frequency = frequency

        with mock.patch('user.MQTTSubscribe.MQTTSubscribeService'):
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_time.time.return_value = now

                SUT = Simulator(None, options)

                mock_engine = mock.Mock()
                SUT.engine = mock_engine

                SUT.simulate_service_archive()

        mock_time.sleep.assert_called_once_with(sleep_amount)
        mock_engine.dispatchEvent.assert_called_once()

    def test_simulate_service_packet(self):
        data = {}
        data['dateTime'] = 0

        frequency = 10

        now = time.time()
        current_time = int(now + 0.5)
        end_period_ts = (int(current_time / frequency) + 1) * frequency
        sleep_amount = end_period_ts - current_time

        options = argparse.Namespace()
        options.type = 'service'
        options.binding = 'loop'
        options.record_count = len(data)
        options.console = None
        options.conf = None

        options.verbose = None
        options.log_file = None
        options.units = 'US'
        options.frequency = frequency

        with mock.patch('user.MQTTSubscribe.MQTTSubscribeService'):
            with mock.patch('user.MQTTSubscribe.time') as mock_time:
                mock_time.time.return_value = now

                SUT = Simulator(None, options)

                mock_engine = mock.Mock()
                SUT.engine = mock_engine

                SUT.simulate_service_packet()

        mock_time.sleep.assert_called_once_with(sleep_amount)
        mock_engine.dispatchEvent.assert_called_once()

    def test_simulate_driver_archive(self):
        data = {}
        data['dateTime'] = 0

        archive_delay = 5
        archive_interval = 60
        now = time.time()

        current_time = int(now + 0.5)
        end_period_ts = (int(current_time / archive_interval) + 1) * archive_interval
        end_delay_ts = end_period_ts + archive_delay
        sleep_amount = end_delay_ts - current_time

        options = argparse.Namespace()
        options.type = 'driver'
        options.binding = 'archive'
        options.record_count = len(data)
        options.console = None
        options.conf = None
        options.verbose = None
        options.log_file = None

        options.archive_delay = archive_delay
        options.archive_interval = archive_interval

        SUT = Simulator(None, options)

        with mock.patch('user.MQTTSubscribe.time') as mock_time:
            mock_time.time.return_value = now

            mock_driver = mock.Mock()
            mock_driver.genArchiveRecords.return_value = [data]

            SUT.simulate_driver_archive(mock_driver)

        mock_time.sleep.assert_called_once_with(sleep_amount)
        mock_driver.genArchiveRecords.assert_called_once_with(end_period_ts)

    def test_simulate_driver_loop(self):
        data = {}
        data['dateTime'] = 0

        options = argparse.Namespace()
        options.type = 'driver'
        options.binding = 'loop'
        options.record_count = len(data)
        options.console = None
        options.conf = None
        options.verbose = None
        options.log_file = None

        options.archive_delay = None
        options.archive_interval = None

        SUT = Simulator(None, options)

        mock_driver = mock.Mock()
        mock_driver.genLoopPackets.return_value = [data]

        SUT.simulate_driver_packet(mock_driver)

        mock_driver.genLoopPackets.assert_called_once()

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestRunSimulator('test_simulate_service_archive'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
