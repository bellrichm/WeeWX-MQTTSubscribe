#!/usr/bin/python
""" A simple utility that reads messages from a file and publishes each line to MQTT. """
from __future__ import print_function
import time
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc): # (match callback signature) pylint: disable=unused-argument
    """ The on_connect callback. """
    # https://pypi.org/project/paho-mqtt/#on-connect
    # rc:
    # 0: Connection successful
    # 1: Connection refused - incorrect protocol version
    # 2: Connection refused - invalid client identifier
    # 3: Connection refused - server unavailable
    # 4: Connection refused - bad username or password
    # 5: Connection refused - not authorised
    # 6-255: Currently unused.
    print("Connected with result code %i" % rc)
    print("Connected flags %s" % str(flags))

def on_disconnect(client, userdata, rc): # (match callback signature) pylint: disable=unused-argument
    """ The on_connect callback. """
    # https://pypi.org/project/paho-mqtt/#on-connect
    # rc:
    # 0: Connection successful
    print("Disconnected with result code %i" % rc)

def on_publish(client, userdata, mid): # (match callback signature) pylint: disable=unused-argument
    """ The on_publish callback. """
    print("Published: %s" %mid)

def main():
    """ The main entry point. """
    host = "localhost"
    port = 1883
    keepalive = 60
    client_id = "client_id"
    topic = "test"
    filename = "tmp/messages.txt"
    prompt_to_send = False

    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.connect(host, port, keepalive)
    client.loop_start()

    with open(filename) as file_object:
        message = file_object.readline().rstrip()
        while message:
            publish_time = int(time.time() + 0.5)
            message = message.replace("{DATETIME}", str(publish_time))
            mqtt_message_info = client.publish(topic, message)
            mqtt_message_info.wait_for_publish()
            print("Sent: %s has return code %i" %(mqtt_message_info.mid, mqtt_message_info.rc))
            message = file_object.readline().rstrip()
            if message:
                if prompt_to_send:
                    print("press enter to send next message.")
                    raw_input()

    client.disconnect()

main()
