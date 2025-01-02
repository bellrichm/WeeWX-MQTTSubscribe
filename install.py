#
#    Copyright (c) 2020-2024 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
""" Installer for MTTQSubscribe driver and service. """

from io import StringIO

import configobj

from weecfg.extension import ExtensionInstaller

VERSION = '3.0.1-rc01'

MQTTSUBSCRIBE_CONFIG = """

[MQTTSubscribeDriver]
    # This section is for the MQTTSubscribe driver.

    # The driver to use.
    # Only used by the driver.
    driver = user.MQTTSubscribe

    # Controls if validation errors raise an exception (stopping WeeWX from starting) or only logged.
    # Default is false
    stop_on_validation_errors = true    

[MQTTSubscribeService]
    # This section is for the MQTTSubscribe service.

    # Turn the service on and off.
    # Default is: true
    # Only used by the service.
    enable = false

    # Controls if validation errors raise an exception (stopping WeeWX from starting) or only logged.
    # Default is false
    stop_on_validation_errors = true
    
"""


def loader():
    """ Load and return the extension installer. """
    return MQTTSubscribeServiceInstaller()


class MQTTSubscribeServiceInstaller(ExtensionInstaller):
    """ The extension installer. """
    def __init__(self):
        install_dict = {
            'version': VERSION,
            'name': 'MQTTSubscribe',
            'description': 'Source WeeWX data from MQTT.',
            'author': "Rich Bell",
            'author_email': "bellrichm@gmail.com",
            'files': [('bin/user', ['bin/user/MQTTSubscribe.py'])]
        }

        MQTTSubscribe_dict = configobj.ConfigObj(StringIO(MQTTSUBSCRIBE_CONFIG))  # pylint: disable = invalid-name
        install_dict['config'] = MQTTSubscribe_dict
        install_dict['data_services'] = 'user.MQTTSubscribe.MQTTSubscribeService'

        super().__init__(install_dict)
