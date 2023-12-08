#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access

import unittest

import configobj

from user.MQTTSubscribe import MQTTSubscribeConfiguration, CONFIG_SPEC_TEXT

class TestValidateTopicsSection(unittest.TestCase):
    def test_topic_configured_as_field(self):
        section = 'MQTTSubscribeDriver'
        topic_name = 'topic1'

        config_text = f'''
[topics]
    [[{topic_name}]]
        qos = 0
        name = foo
'''

        error_msgs = []
        warn_msgs = []

        SUT = MQTTSubscribeConfiguration(None)

        SUT._validate_topics_section(topic_name,
                        f'{section}-topics-',
                        configobj.ConfigObj(config_text.splitlines())['topics'][topic_name],
                        configobj.ConfigObj(CONFIG_SPEC_TEXT.splitlines())['MQTTSubscribe']['topics']['REPLACE_ME'],
                        MQTTSubscribeConfiguration.deprecated_options\
                            .get('MQTTSubscribe', {})\
                            .get('topics', {})\
                            .get('REPLACE_ME', {}),
                        error_msgs,
                        warn_msgs)

        self.assertEqual(warn_msgs, [])
        self.assertEqual(error_msgs, [])

    def test_topic_has_field_options(self):
        section = 'MQTTSubscribeDriver'
        topic_name = 'topic1'

        config_text = f'''
[topics]
    [[{topic_name}]]
        qos = 0
        name = foo
        [[[field1]]]
'''

        error_msgs = []
        warn_msgs = []

        SUT = MQTTSubscribeConfiguration(None)

        SUT._validate_topics_section(topic_name,
                        f'{section}-topics-',
                        configobj.ConfigObj(config_text.splitlines())['topics'][topic_name],
                        configobj.ConfigObj(CONFIG_SPEC_TEXT.splitlines())['MQTTSubscribe']['topics']['REPLACE_ME'],
                        MQTTSubscribeConfiguration.deprecated_options\
                            .get('MQTTSubscribe', {})\
                            .get('topics', {})\
                            .get('REPLACE_ME', {}),
                        error_msgs,
                        warn_msgs)

        self.assertEqual(warn_msgs, [])
        self.assertEqual(error_msgs, [f"ERROR: Unknown option: MQTTSubscribeDriver-topics-{topic_name}-name"])

    def test_topic_has_a_message_configuration(self):
        section = 'MQTTSubscribeDriver'
        topic_name = 'topic1'

        config_text = f'''
[topics]
    [[{topic_name}]]
        qos = 0
        name = foo
        [[[message]]]
'''

        error_msgs = []
        warn_msgs = []

        SUT = MQTTSubscribeConfiguration(None)

        SUT._validate_topics_section(topic_name,
                        f'{section}-topics-',
                        configobj.ConfigObj(config_text.splitlines())['topics'][topic_name],
                        configobj.ConfigObj(CONFIG_SPEC_TEXT.splitlines())['MQTTSubscribe']['topics']['REPLACE_ME'],
                        MQTTSubscribeConfiguration.deprecated_options\
                            .get('MQTTSubscribe', {})\
                            .get('topics', {})\
                            .get('REPLACE_ME', {}),
                        error_msgs,
                        warn_msgs)

        self.assertEqual(warn_msgs, [])
        self.assertEqual(error_msgs, [])

if __name__ == '__main__':
    # test_suite = unittest.TestSuite()
    # test_suite.addTest(TestValidateTopicsSection('test_topic_configured_as_field'))
    # unittest.TextTestRunner().run(test_suite)

    unittest.main(exit=False)
