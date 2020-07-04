# pylint: disable=missing-docstring
# pylint: disable=wrong-import-order
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

from __future__ import print_function

import json
import time
import unittest
import configobj

import utils

import weewx
from user.MQTTSubscribe import TopicManager, Logger

class TestAccumulatedData(unittest.TestCase):
    def runit(self, payload, file_pointer, check_results=True):
        test_data = json.load(file_pointer, object_hook=utils.byteify)
        config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
        testruns = test_data['testruns']

        logger = Logger('IntegTest')
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)

        unit_system_name = topics_dict.get('unit_system', 'US').strip().upper()
        if unit_system_name not in weewx.units.unit_constants:
            raise ValueError("MQTTSubscribe: Unknown unit system: %s" % unit_system_name)
        unit_system = weewx.units.unit_constants[unit_system_name]

        on_message = utils.get_callback(payload, config_dict, manager, logger)
        for testrun in testruns:
            start_ts = time.time()
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    utils.send_msg(utils.send_direct_msg, payload, on_message, topic, topic_info)

            end_ts = time.time()
            records = []
            for topic in sorted(manager.subscribed_topics): # todo - dependent on topic names - not great
                data = manager.get_accumulated_data(topic, start_ts, end_ts, unit_system)
                records.append(data)

            if check_results:
                results = testrun['results']
                result = {}
                found = False
                for result in results:
                    if 'accumulate' in result['test']:
                        if payload in result['payloads']:
                            found = True
                            break
                self.assertTrue(found, "No results for %s" %payload)

                utils.check(self, payload, records, result['records'])
            else:
                for record in records:
                    print(record)

class TestAccumulatedRain(TestAccumulatedData):
    #@unittest.skip("")
    def test_accumulatedrain_individual(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_accumulatedrain_json(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_accumulatedrain_keyword(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            self.runit('keyword', file_pointer)

class TestBasic(TestAccumulatedData):
    #@unittest.skip("")
    def test_basic_individual(self):
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_basic_json(self):
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_basic_keyword(self):
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            self.runit('keyword', file_pointer)

class TestEmpty(TestAccumulatedData):
    #@unittest.skip("")
    def test_empty_individual(self):
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_empty_json(self):
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_empty_keyword(self):
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            self.runit('keyword', file_pointer)

class TestWindIndividualTopics(TestAccumulatedData):
    #@unittest.skip("")
    def test_wind_individual_topic(self):
        with open("bin/user/tests/integ/data/wind-individual.json") as file_pointer:
            self.runit('individual', file_pointer)

class TestWind(TestAccumulatedData):
    #@unittest.skip("")
    def test_wind_individual(self):
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_wind_json(self):
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_wind_keyword(self):
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            self.runit('keyword', file_pointer)

if __name__ == '__main__':
    unittest.main(exit=False)
