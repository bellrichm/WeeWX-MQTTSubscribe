#!/usr/bin/python
""" A simple utility that reads messages from a file and publishes each line to MQTT. """
from __future__ import print_function
import optparse
import random
import sys
import time
import paho.mqtt.client as mqtt

# Stole from six module. Added to eliminate dependency on six when running under WeeWX 3.x
PY2 = sys.version_info[0] == 2

USAGE = """pubmqtt --help
        mqtt_test
           [--host=HOST]
           [--port=PORT]
           [--keepalive=KEEPALIVE]
           [--client-id=CLIENT_ID]
           [--topic=TOPIC]
           [--file=FILE]
           [--interval=INTERVAL]
           [--min-interval=MIN_INTERVAL]
           [--max-interval=MAX_INTERVAL]
           [--prompt]

A simple utility that reads messages from a file and publishes each line to MQTT. """


def init_parser():
    """ Parse the command line arguments. """
    parser = optparse.OptionParser(usage=USAGE)
    parser.add_option("--host", dest='host', default='localhost',
                      help="The MQTT server.")
    parser.add_option('--port', dest='port', type=int, default=1883,
                      help='The port to connect to.')
    parser.add_option('--keepalive', dest='keepalive', type=int, default=60,
                      help='Maximum period in seconds allowed between communications with the broker.')
    parser.add_option("--client-id", dest='client_id', default='clientid',
                      help="The clientid to connect with.")
    parser.add_option("--topic", dest='topic', default='test-topic',
                      help="The topic to subscribe to.")
    parser.add_option("--file", dest='file', default='tmp/messages.txt',
                      help="The file containing the messages to publish.")
    parser.add_option("--interval", dest='interval', type=int, default=0,
                      help="The minimum time between publishing messages.")
    parser.add_option("--min-interval", dest='min_interval', type=int, default=0,
                      help="When using a random interval, the minimum time between publishing messages.")
    parser.add_option("--max-interval", dest='max_interval', type=int, default=0,
                      help="When using a random interval, the 'maximum' time between publishing messages.")
    parser.add_option("--prompt", action="store_true", dest="prompt_to_send",
                      help="Prompt to publish the next message.")

    return parser


def on_connect(client, userdata, flags, rc):  # (match callback signature) pylint: disable=unused-argument
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


def on_disconnect(client, userdata, rc):  # (match callback signature) pylint: disable=unused-argument
    """ The on_connect callback. """
    # https://pypi.org/project/paho-mqtt/#on-connect
    # rc:
    # 0: Connection successful
    print("Disconnected with result code %i" % rc)


def on_publish(client, userdata, mid):  # (match callback signature) pylint: disable=unused-argument
    """ The on_publish callback. """
    print("Published: %s" % mid)


def main():
    """ The main entry point. """
    parser = init_parser()
    (options, args) = parser.parse_args() # (match callback signature) pylint: disable=unused-variable

    host = options.host
    port = options.port
    keepalive = options.keepalive
    client_id = options.client_id
    topic = options.topic
    filename = options.file
    interval = options.interval
    min_interval = options.min_interval
    max_interval = options.max_interval
    prompt_to_send = options.prompt_to_send

    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.connect(host, port, keepalive)
    client.loop_start()

    publish_time = 0

    with open(filename) as file_object:
        message = file_object.readline().rstrip()
        while message:
            interval = random.randint(min_interval, max_interval)
            current_time = int(time.time() + 0.5)
            used_time = current_time - publish_time
            if used_time < interval:
                time.sleep(interval - used_time)

            publish_time = int(time.time() + 0.5)
            message = message.replace("{DATETIME}", str(publish_time))
            if prompt_to_send:
                print("press enter to send next message.")
                if PY2:
                    raw_input() # (only a python 3 error) pylint: disable=undefined-variable
                else:
                    input()
            mqtt_message_info = client.publish(topic, message)
            mqtt_message_info.wait_for_publish()
            print("Sent: %s has return code %i" % (mqtt_message_info.mid, mqtt_message_info.rc))
            message = file_object.readline().rstrip()

    client.disconnect()

main()
