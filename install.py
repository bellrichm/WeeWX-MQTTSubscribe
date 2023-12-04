#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
""" Installer for MTTQSubscribe driver and service. """

import os

from io import StringIO

import configobj

from weecfg.extension import ExtensionInstaller

VERSION = '3.0.0-rc02'

MQTTSUBSCRIBESERVICE_CONFIG = """
[MQTTSubscribeService]
    # This section is for the MQTTSubscribe service.

    # Turn the service on and off.
    # Default is: true
    # Only used by the service.
    enable = false

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

        MQTTSubscribeService_dict = configobj.ConfigObj(StringIO(MQTTSUBSCRIBESERVICE_CONFIG))  # pylint: disable = invalid-name
        install_dict['config'] = MQTTSubscribeService_dict
        install_dict['data_services'] = 'user.MQTTSubscribe.MQTTSubscribeService'

        super().__init__(install_dict)
