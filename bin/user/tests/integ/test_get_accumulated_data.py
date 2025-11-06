#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import json
import string
import time
import unittest
import configobj

import utils

import weewx
from user.MQTTSubscribe import TopicManager, Logger

class TestAccumulatedData(unittest.TestCase):
    def runit(self, payload, file_pointer, check_results=True):
        test_id = utils.random_string()
        data_template = string.Template(file_pointer.read())
        test_data = json.loads(data_template.substitute(test_id=test_id), object_hook=utils.byteify)
        config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
        testruns = test_data['testruns']

        logger = Logger('IntegTest')
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(None, topics_dict, logger)

        unit_system_name = topics_dict.get('unit_system', 'US').strip().upper()
        if unit_system_name not in weewx.units.unit_constants:
            raise ValueError(f"MQTTSubscribe: Unknown unit system: {unit_system_name}")
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
            for queue in sorted(manager.queues, key=lambda i: i['name']):  # todo - dependent on topic names - not great
                data = manager.get_accumulated_data(queue, start_ts, end_ts, unit_system)
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
                self.assertTrue(found, f"No results for {payload}")

                utils.check(self, payload, records, result['records'])
            else:
                for record in records:
                    print(record)

class TestAccumulatedRain(TestAccumulatedData):
    # @unittest.skip("")
    def test_accumulatedrain_individual(self):
        # At WeeWX 4.6.1, the handling of 'sum' accumulators changed.
        # In prior versions if there was no data a 0 was returned. Now None isvreturned.
        with open("bin/user/tests/integ/data/accumulatedrain.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

    # @unittest.skip("")
    def test_accumulatedrain_json(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json", encoding="UTF-8") as file_pointer:
            self.runit('json', file_pointer)

    # @unittest.skip("")
    def test_accumulatedrain_keyword(self):
        with open("bin/user/tests/integ/data/accumulatedrain.json", encoding="UTF-8") as file_pointer:
            self.runit('keyword', file_pointer)

class TestBasic(TestAccumulatedData):
    # @unittest.skip("")
    def test_basic_individual(self):
        with open("bin/user/tests/integ/data/basic.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

    # @unittest.skip("")
    def test_basic_json(self):
        with open("bin/user/tests/integ/data/basic.json", encoding="UTF-8") as file_pointer:
            self.runit('json', file_pointer)

    # @unittest.skip("")
    def test_basic_keyword(self):
        with open("bin/user/tests/integ/data/basic.json", encoding="UTF-8") as file_pointer:
            self.runit('keyword', file_pointer)

class TestEmpty(TestAccumulatedData):
    # @unittest.skip("")
    def test_empty_individual(self):
        with open("bin/user/tests/integ/data/empty.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

    # @unittest.skip("")
    def test_empty_json(self):
        with open("bin/user/tests/integ/data/empty.json", encoding="UTF-8") as file_pointer:
            self.runit('json', file_pointer)

    # @unittest.skip("")
    def test_empty_keyword(self):
        with open("bin/user/tests/integ/data/empty.json", encoding="UTF-8") as file_pointer:
            self.runit('keyword', file_pointer)

class TestWindIndividualTopics(TestAccumulatedData):
    # @unittest.skip("")
    def test_wind_individual_topic(self):
        with open("bin/user/tests/integ/data/wind-individual.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

class TestWind(TestAccumulatedData):
    # @unittest.skip("")
    def test_wind_individual(self):
        with open("bin/user/tests/integ/data/wind.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

    # @unittest.skip("")
    def test_wind_json(self):
        with open("bin/user/tests/integ/data/wind.json", encoding="UTF-8") as file_pointer:
            self.runit('json', file_pointer)

    # @unittest.skip("")
    def test_wind_keyword(self):
        with open("bin/user/tests/integ/data/wind.json", encoding="UTF-8") as file_pointer:
            self.runit('keyword', file_pointer)

if __name__ == '__main__':
    unittest.main(exit=False)
