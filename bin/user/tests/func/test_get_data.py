"""
An example/prototype of functional test.
Tests 'everything' needed for calls to get_data and get_accumulated_data of the TopicManager class.
Calls the on_message callback directly, so no dependency on MQTT.
"""
# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from __future__ import with_statement

import utils
import unittest

import configobj
import json

from user.MQTTSubscribe import TopicManager, Logger

class TestIndividualPayload(unittest.TestCase):
    def get_data_test(self, testtype, testruns, config_dict):
        #if skip
        #    return

        if testtype == 'individual':
            msg_def = utils.INDIVIDUAL_PAYLOAD
        elif testtype == 'json':
            msg_def = utils.JSON_PAYLOAD
        elif testtype == 'keyword':
            msg_def = utils.KEYWORD_PAYLOAD
        logger = Logger()
        topics_dict = config_dict.get('topics', {})
        manager = TopicManager(topics_dict, logger)

        on_message = utils.setup(msg_def, config_dict, manager, logger)

        for testrun in testruns:
            for topics in testrun['payload']:
                msg_def['on_message'](on_message, topics)

            records = []
            for topic in manager.subscribed_topics:
                for data in manager.get_data(topic):
                    if data:
                        records.append(data)
                    else:
                        break

            utils.check(self, testtype, records, testrun['results']['records'])

    #@unittest.skip("")
    def test_get_data_individual0(self):
        with open("bin/user/tests/func/data/first.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            # TODO Skip
            for testtype in testx_data['types']:
                self.get_data_test(testtype, testx_data['data'], config_dict)

    #@unittest.skip("")
    def test_get_data_individual1(self):
        with open("bin/user/tests/func/data/firstxi.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            # TODO Skip
            for testtype in testx_data['types']:
                self.get_data_test(testtype, testx_data['data'], config_dict)

    #@unittest.skip("")
    def test_get_data_individual1b(self):
        with open("bin/user/tests/func/data/firstx.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            # TODO Skip
            for testtype in testx_data['types']:
                self.get_data_test(testtype, testx_data['data'], config_dict)


    #@unittest.skip("")
    def test_get_data_individual(self):
        with open("bin/user/tests/func/data/accumulatedrain.json") as fp:
            testx_data = json.load(fp, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])['MQTTSubscribeService']
            # TODO Skip
            for testtype in testx_data['types']:
                self.get_data_test(testtype, testx_data['data'], config_dict)

if __name__ == '__main__':
    unittest.main(exit=False)
