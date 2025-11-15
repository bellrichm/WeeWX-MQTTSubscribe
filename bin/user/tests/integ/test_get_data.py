#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import json
import string
import unittest
import configobj

import utils

from user.MQTTSubscribe import TopicManager, Logger

class TestGetData(unittest.TestCase):
    def runit(self, payload, file_pointer, check_results=True):
        test_id = utils.random_string()
        data_template = string.Template(file_pointer.read())
        test_data = json.loads(data_template.substitute(test_id=test_id), object_hook=utils.byteify)
        config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
        testruns = test_data['testruns']

        logger = Logger({'mode': 'IntegTest'})
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(None, topics_dict, logger)

        on_message = utils.get_callback(payload, config_dict, manager, logger)

        for testrun in testruns:
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    utils.send_msg(utils.send_direct_msg, payload, on_message, topic, topic_info)

            records = []
            for queue in manager.queues:
                for data in manager.get_data(queue):
                    if data:
                        records.append(data)
                    else:
                        break

            if check_results:
                results = testrun['results']
                result = {}
                found = False
                for result in results:
                    if 'single' in result['test']:
                        if payload in result['payloads']:
                            found = True
                            break
                self.assertTrue(found, f"No results for {payload}")

                utils.check(self, payload, records, result['records'])
            else:
                for record in records:
                    print(record)

class TestAccumulatedRain(TestGetData):
    # @unittest.skip("")
    def test_accumulatedrain_individual(self):
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

class TestBasic(TestGetData):
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

class TestEmpty(TestGetData):
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

class TestIndividualWindTopics(TestGetData):
    # @unittest.skip("")
    def test_wind_individual_topic(self):
        with open("bin/user/tests/integ/data/wind-individual.json", encoding="UTF-8") as file_pointer:
            self.runit('individual', file_pointer)

class TestWind(TestGetData):
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
