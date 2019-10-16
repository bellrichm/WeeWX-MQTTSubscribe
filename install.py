""" Installer for MTTQSubscribe driver and service.
By default, this will install and configure the service, but not enable it.

To install the service enabled, set the environment variable MQTTSubscribe_install_type to SERVICE.
For example,
MQTTSubscribe_install_type=SERVICE wee_extension --install=PATH-TO-FILE

To install only the driver, set the environment variable MQTTSubscribe_install_type to DRIVER
For example, 
MQTTSubscribe_install_type=DRIVER wee_extension --install=PATH-TO-FILE
and then run 
wee_config --reconfig

For all cases to uninstall run
wee_extension --uninstall=MQTTSubscribe
"""

import configobj
import os

from six.moves import StringIO

from weecfg.extension import ExtensionInstaller

VERSION='1.2.1-rc02'

MQTTSubscribeService_config = """
[MQTTSubscribeService]
    # This section is for the MQTTSubscribe service.

    # Turn the service on and off.
    # Default is: true
    # Only used by the service.
    enable = %s

    # The MQTT server.
    # Default is: localhost
    host = localhost

    # The port to connect to.
    # Default is: 1883
    port = 1883

    # Maximum period in seconds allowed between communications with the broker.
    # Default is: 60
    keepalive = 60

    # The binding, loop or archive.
    # Default is: loop
    # Only used by the service.
    binding = loop

    # The message handler to use
    [[message_callback]]
        # The format of the MQTT payload.
        # Currently support: individual, json, keyword
        # Must be specified.
        type = REPLACE_ME

    # The topics to subscribe to.
    [[topics]]
        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX
        # Default is: US
        unit_system = US

        [[[FIRST/REPLACE_ME]]]
        [[[SECOND/REPLACE_ME]]]
"""

def loader():
    return MQTTSubscribeServiceInstaller()

class MQTTSubscribeServiceInstaller(ExtensionInstaller):
    def __init__(self):
        try:
            install_type = os.environ['MQTTSubscribe_install_type'].upper()
        except KeyError:
            install_type = ''
        
        install_dict = {
            'version': VERSION,
            'name': 'MQTTSubscribe',
            'description': 'Augment WeeWX records or packets with data MQTT',
            'author': "Rich Bell",
            'author_email': "bellrichm@gmail.com",
            'files': [('bin/user', ['bin/user/MQTTSubscribe.py'])]
        }

        # If installing as a driver, do not configure or add service
        if install_type != 'DRIVER':
            # If did not specify service install, then configure service
            # but do not enable it
            if install_type != 'SERVICE':
                enable = 'false'
            else:
                enable = 'true'

            MQTTSubscribeService_dict = configobj.ConfigObj(StringIO(MQTTSubscribeService_config % enable))
            install_dict['config'] = MQTTSubscribeService_dict
            install_dict['data_services'] = 'user.MQTTSubscribe.MQTTSubscribeService'

        super(MQTTSubscribeServiceInstaller, self).__init__(install_dict)
