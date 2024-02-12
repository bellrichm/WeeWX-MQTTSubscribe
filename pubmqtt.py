#!/usr/bin/python
#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
""" A simple utility that reads messages from a file and publishes each line to MQTT. """
import argparse
import random
import time
import paho.mqtt.client as mqtt

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
    parser = argparse.ArgumentParser(usage=USAGE)
    parser.add_argument("--host", dest='host', default='localhost',
                        help="The MQTT server.")
    parser.add_argument('--port', dest='port', type=int, default=1883,
                        help='The port to connect to.')
    parser.add_argument('--keepalive', dest='keepalive', type=int, default=60,
                        help='Maximum period in seconds allowed between communications with the broker.')
    parser.add_argument("--client-id", dest='client_id', default='clientid',
                        help="The clientid to connect with.")
    parser.add_argument("--topic", dest='topic', default='debug-topic',
                        help="The topic to publish to.")
    parser.add_argument("--qos", default=0, type=int,
                        help="QOS desired. Currently one specified for all topics")
    parser.add_argument("--file", dest='file', default='tmp/messages.txt',
                        help="The file containing the messages to publish.")
    parser.add_argument("--interval", dest='interval', type=int, default=0,
                        help="The minimum time between publishing messages.")
    parser.add_argument("--min-interval", dest='min_interval', type=int, default=0,
                        help="When using a random interval, the minimum time between publishing messages.")
    parser.add_argument("--max-interval", dest='max_interval', type=int, default=0,
                        help="When using a random interval, the 'maximum' time between publishing messages.")
    parser.add_argument("--prompt", action="store_true", dest="prompt_to_send",
                        help="Prompt to publish the next message.")

    return parser


def on_connect(_client, _userdata, flags, rc):
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
    print(f"Connected with result code {int(rc)}")
    print(f"Connected flags {str(flags)}")


def on_disconnect(_client, _userdata, rc):
    """ The on_connect callback. """
    # https://pypi.org/project/paho-mqtt/#on-discconnect
    # The rc parameter indicates the disconnection state.
    # If MQTT_ERR_SUCCESS (0), the callback was called in response to a disconnect() call. If any other value the disconnection was unexpected,
    # such as might be caused by a network error.
    print(f"Disconnected with result code {int(rc)}")

def on_publish(_client, _userdata, mid):
    """ The on_publish callback. """
    print(f"Published: {mid}")

def on_log(_client, _userdata, _level, msg):
    """ The on_log callback. """
    print(f"MQTT log {msg}")

def main():
    # pylint: disable=too-many-locals
    """ The main entry point. """
    parser = init_parser()
    options = parser.parse_args()

    host = options.host
    port = options.port
    keepalive = options.keepalive
    client_id = options.client_id
    topic = options.topic
    qos = options.qos
    filename = options.file
    interval = options.interval
    min_interval = options.min_interval
    max_interval = options.max_interval
    prompt_to_send = options.prompt_to_send

    try:
        callback_api_version = mqtt.CallbackAPIVersion.VERSION1
        client = mqtt.Client(callback_api_version=callback_api_version, # (only available in v2) pylint: disable=unexpected-keyword-arg
                                client_id=client_id)
    except AttributeError:
        client = mqtt.Client(client_id=client_id) # (v1 signature) pylint: disable=no-value-for-parameter

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.on_log = on_log
    client.connect(host, port, keepalive)
    client.loop_start()

    publish_time = 0

    with open(filename, encoding='UTF-8') as file_object:
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
                input()
            mqtt_message_info = client.publish(topic, message, qos=qos)
            print(f"Publish: {mqtt_message_info.mid} has return code {int(mqtt_message_info.rc)}, {mqtt.error_string(mqtt_message_info.rc)}")

            if mqtt_message_info.rc != mqtt.MQTT_ERR_SUCCESS:
                raise ValueError(mqtt.error_string(mqtt_message_info.rc))

            if not mqtt_message_info.is_published():
                print("Waiting for publish.")
                mqtt_message_info.wait_for_publish()

            message = file_object.readline().rstrip()

    client.disconnect()
    print("Done")

main()
