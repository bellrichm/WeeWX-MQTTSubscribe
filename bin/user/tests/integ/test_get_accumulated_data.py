# pylint: disable=missing-docstring
# pylint: disable=wrong-import-order
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

import json
import time
import unittest
import configobj

import utils

from user.MQTTSubscribe import TopicManager, Logger

class TestOne(unittest.TestCase):
    def runit(self, config_dict, testruns, payload):
        logger = Logger()
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)

        on_message = utils.get_callback(payload, config_dict, manager, logger)
        for testrun in testruns:
            start_ts = time.time()
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    utils.send_msg(utils.send_direct_msg, payload, on_message, topic, topic_info)
                #utils.send_msg(utils.send_direct_msg, test_type, on_message, topics)
            end_ts = time.time()

            results = testrun['results']
            result = {}
            for result in results:
                if 'accumulate' in result['test']:
                    if payload in result['payloads']:
                        break

            records = []
            for topic in sorted(manager.subscribed_topics): # todo - dependent on topic names - not great
                data = manager.get_accumulated_data(topic, start_ts, end_ts, result['units'])
                records.append(data)

            utils.check(self, payload, records, result['records'])

    #@unittest.skip("")
    def test_accumulatedrain_individual(self):
        payload = 'individual'
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_accumulatedrain_json(self):
        payload = 'json'
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_accumulatedrain_keyword(self):
        payload = 'keyword'
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_basic_individual(self):
        payload = 'individual'
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_basic_json(self):
        payload = 'json'
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_basic_keyword(self):
        payload = 'keyword'
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_empty_individual(self):
        payload = 'individual'
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_empty_json(self):
        payload = 'json'
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_empty_keyword(self):
        payload = 'keyword'
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_wind_individual_topic(self):
        payload = 'individual'
        with open("bin/user/tests/integ/data/wind-individual.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_wind_individual(self):
        payload = 'individual'
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_wind_json(self):
        payload = 'json'
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

    #@unittest.skip("")
    def test_wind_keyword(self):
        payload = 'keyword'
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            test_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
            testruns = test_data['testruns']
            self.runit(config_dict, testruns, payload)

if __name__ == '__main__':
    unittest.main(exit=False)
