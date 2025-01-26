#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
'''
Stubs of paho mqtt code used by MQTTSubscribe.
'''

import paho
import paho.mqtt
import paho.mqtt.client

import random

class Msg:
    '''
    A helper class to create an MQTT message.
    '''
    # pylint: disable=too-few-public-methods
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain

class ClientStub:
    '''
    Stub the paho mqtt Client class.
    Used to test WeeWX/MQTTSubscribe without needeing mqtt.
    Methods below are the ones used by MQTTSubscribe.
    '''
    # pylint: disable=missing-function-docstring
    # pylint: disable=unused-argument
    on_message = None

    def __init__(self,
                 callback_api_version=None,
                 protocol=None,
                 client_id = None,
                 userdata=None,
                 clean_session=None):

        self.userdata = userdata
        print("In init")

    def reconnect_delay_set(self,
                            min_delay=None,
                            max_delay=None):
        print("In reconnect_delay_set")

    def connect(self,
                _host,
                _port,
                _keepalive):
        print("In connect")

    def subscribe(self, topic, qos):
        print("In Subscribe")
        self.topic = topic
        return (0, 0)

    def loop_start(self):
        print("In loop_start")

        reason_code = paho.mqtt.reasoncodes.ReasonCode(paho.mqtt.packettypes.PacketTypes.CONNACK, identifier=0)
        self.on_connect(self, self.userdata, 0, reason_code, 0)
        print("Connected")

        # ToDo: temporarily try calling the message callback, this will need to be moved
        print(self.on_message)
        payload = "0.0".encode('UTF-8')
        msg = Msg(self.topic, "0.0".encode('UTF-8'), 0, 0)
        self.on_message(self, self.userdata, msg)

paho.mqtt.client.Client = ClientStub
