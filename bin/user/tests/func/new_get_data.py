# pylint: disable=missing-docstring

import json
import unittest
import configobj

import utils

from user.MQTTSubscribe import TopicManager, Logger


class TestOne(unittest.TestCase):
    def get_tests(self, file):
        test_data = json.load(file, object_hook=utils.byteify)
        config_dict = configobj.ConfigObj(test_data['config'])['MQTTSubscribeService']
        #print(config_dict)
        testruns = test_data['testruns']
        #print(testruns)
        return config_dict, testruns

    def run_test(self, config_dict, testruns, payload):
        #print(config_dict)
        #print(messages)
        #print(result)
        #print(payload)

        logger = Logger()
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)

        on_message = utils.get_callback(payload, config_dict, manager, logger)

        for testrun in testruns:
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    utils.send_msg(utils.send_direct_msg, payload, on_message, topic, topic_info)

            records = []
            for topic in manager.subscribed_topics:
                for data in manager.get_data(topic):
                    if data:
                        records.append(data)
                    else:
                        break

            results = testrun['results']
            result = {}
            for result in results:
                if result['test'] == 'single' or result['test'] == 'both':
                    if payload in result['payloads']:
                        break

            utils.check(self, payload, records, result['records'])

        print("")

    def test_one(self):
        payload = 'individual'
        with open("bin/user/tests/func/data/new_accumulatedrain.json") as file:
            config_dict, testruns = self.get_tests(file)
            self.run_test(config_dict, testruns, payload)
            #for testrun in testruns:
            #    results = testrun['results']
            #    for result in results:
            #        if result['test'] == 'single' or result['test'] == 'both':
            #            if payload in result['payloads']:
            #                self.run_test(config_dict, testrun['messages'], result, payload)
            print(testruns)
            print("working")
        print("done")

if __name__ == '__main__':
    unittest.main(exit=False)
