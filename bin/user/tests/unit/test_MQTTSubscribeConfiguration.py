#
#    Copyright (c) 2023-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import unittest

import configobj

from user.MQTTSubscribe import MQTTSubscribeConfiguration, CONFIG_SPEC_TEXT

class TestDefaultConfiguration(unittest.TestCase):
    def test_default_configuration(self):
        # This test ensures that the example config contains the expected options
        self.maxDiff = None

        expected_config = '''# Replace '[MQTTSubscribe]' with '[MQTTSubscribeService]' or '[MQTTSubscribeDriver]'
# For additional information see, https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Common-Options
[MQTTSubscribe]
    # The driver to use.
    # Only used by the driver.
    driver = user.MQTTSubscribe
    
    # Turn the service on and off.
    # Default is true.
    # Only used by the service.
    enable = false
    
    # Controls if validation errors raise an exception (stopping WeeWX from starting) or only logged.
    # Default is false
    stop_on_validation_errors = true
    
    # The binding, loop or archive.
    # Default is loop.
    # Only used by the service.
    binding = loop
    
    # The MQTT server.
    # Default is localhost.
    host = localhost
    
    # Controls the MQTT logging.
    # Default is false.
    log = false
    
    # password for broker authentication.
    # Default is None.
    password = None
    
    # The port to connect to.
    # Default is 1883.
    port = 1883
    
    # username for broker authentication.
    # Default is None.
    username = None
    
    # The TLS options that are passed to tls_set method of the MQTT client.
    # For additional information see, https://eclipse.org/paho/clients/python/docs/strptime-format-codes
    [[tls]]
        # Turn tls on and off.
        # Default is true.
        enable = false
        
        # Path to the Certificate Authority certificate files that are to be treated as trusted by this client.
        ca_certs = ""
        
        # The PEM encoded client certificate and private keys.
        # Default is None
        certfile = None
        
        # The certificate requirements that the client imposes on the broker.
        # Valid values: none, optional, required
        # Default is required,
        certs_required = required
        
        # The encryption ciphers that are allowable for this connection. Specify None to use the defaults
        # Default is None.
        ciphers = None
        
        # The private keys.
        # Default is None
        keyfile = None
        
        # The version of the SSL/TLS protocol to be used.
        # Valid values: sslv2, sslv23, sslv3, tls, tlsv1, tlsv11, tlsv12.
        # Default is tlsv12.
        tls_version = tlsv12
    
    # For additional information see, https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Configuring#the-topic-name-sections
    [[topics]]
        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX.
        # For more information see, http://weewx.com/docs/customizing.htm#units
        # Default is US.
        unit_system = US
        
        # The first topic to subscribe to
        # For additional information see, https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Configuring#the-topic-name-sections
        [[[REPLACE_ME]]]
            # When set to false, the topic is not subscribed to.
            # Valid values: True, False
            # Default is True
            subscribe = True
            
            # Sets the default value for all fields in this topic.
            # Setting the value to 'true' "opts out" and the desired fields will need to set 'ignore = false'
            # Valid values: True, False.
            # Default is False.
            ignore = False
            
            # Configuration information about the MQTT message format for this topic
            [[[[message]]]]
                # The format of the MQTT payload.
                # Currently support: individual, json, keyword.
                # Must be specified.
                type = REPLACE_ME
            
            # The incoming field name from MQTT.
            # For additional information see, https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Configuring#the-field-name-sections
            # Use this template for any fields that need to be configured.
            # If no fields need to be configured, remove this section.
            [[[[REPLACE_ME]]]]
                # True if the incoming field should not be processed into WeeWX.
                # Valid values: True, False.
                # Default is  derived from the 'ignore' option at the topic level.
                ignore = False
                
                # True if the incoming data is cumulative.
                # Valid values: True, False.
                # Default is False.
                contains_total = False
                
                # The WeeWX name.
                # Default is the name from MQTT.
                name = REPLACE_ME
        
        # The second topic to subscribe to
        # Use this and the above topic section as a template to configure additional topics.
        # If no additional topics are needed, remove this section
        [[[REPLACE_ME_TOO]]]'''  # noqa: W293, E501 - Need to match example that is created

        SUT = MQTTSubscribeConfiguration(None)

        self.assertEqual(SUT.default_config.write()[5:], expected_config.split('\n'))

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
                                     MQTTSubscribeConfiguration.deprecated_options
                                     .get('MQTTSubscribe', {})
                                     .get('topics', {})
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
                                     MQTTSubscribeConfiguration.deprecated_options
                                     .get('MQTTSubscribe', {})
                                     .get('topics', {})
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
                                     MQTTSubscribeConfiguration.deprecated_options
                                     .get('MQTTSubscribe', {})
                                     .get('topics', {})
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
