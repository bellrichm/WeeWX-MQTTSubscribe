#!/usr/bin/python
""" A simple utility that prints the topics and payloads. """

from __future__ import print_function
import argparse
import os
import random

import configobj
import paho.mqtt.client as mqtt

USAGE = """mqtt_test --help
        mqtt_test [CONFIG_FILE]
           [--type=[driver|service]]
           [--records=MAX_RECORDS]
           [--host=HOST]
           [--port=PORT]
           [--keepalive=KEEPALIVE]
           [--clientid=CLIENTID]
           [--username=USERNAME]
           [--password=PASSWORD]
           [--topics=TOPIC1,TOPIC2]
           [--quiet]

A simple utility that prints the topics and payloads.
Configuration can be read from a 'weewx.conf' file or passed in.
Command line options override any options in the file.
"""


def on_log(client, userdata, level, msg):  # (match callback signature) pylint: disable=unused-argument
    """ MQTT logging callback. """
    log_level = {
        mqtt.MQTT_LOG_INFO: 'MQTT_LOG_INFO',
        mqtt.MQTT_LOG_NOTICE: 'MQTT_LOG_NOTICE',
        mqtt.MQTT_LOG_WARNING: 'MQTT_LOG_WARNING',
        mqtt.MQTT_LOG_ERR: 'MQTT_LOG_ERR',
        mqtt.MQTT_LOG_DEBUG: 'MQTT_LOG_DEBUG'
    }

    print("%s: %s" % (log_level[level], msg))


def on_connect(client, userdata, flags, rc): # (match callback signature) pylint: disable=unused-argument
    """ MQTT on connect callback. """
    print("Connected with result code %i" % rc)
    for topic in userdata['topics']:
        client.subscribe(topic)


def on_disconnect(client, userdata, rc):  # (match callback signature) pylint: disable=unused-argument
    """ MQTT on disconnect callback. """
    print("Disconnected with result code %i" % rc)


def on_message(client, userdata, msg):  # (match callback signature) pylint: disable=unused-argument
    """ MQTT on message callback. """
    print('%s: %s' %(msg.topic, msg.payload))
    if userdata.get('max_records'):
        userdata['counter'] += 1
        if userdata['counter'] >= userdata['max_records']:
            client.disconnect()


def init_parser():
    """ Parse the command line arguments. """
    parser = argparse.ArgumentParser(usage=USAGE)
    parser.add_argument("--type", choices=["driver", "service"],
                        help="The simulation type.",
                        default="driver")
    parser.add_argument('--records', dest='max_records', type=int,
                        help='The number of MQTT records to retrieve.')
    parser.add_argument("--host",
                        help="The MQTT server.")
    parser.add_argument('--port', dest='port', type=int,
                        help='The port to connect to.')
    parser.add_argument('--keepalive', dest='keepalive', type=int,
                        help='Maximum period in seconds allowed between communications with the broker.')
    parser.add_argument("--clientid",
                        help="The clientid to connect with.")
    parser.add_argument("--username",
                        help="username for broker authentication.")
    parser.add_argument("--password",
                        help="password for broker authentication.")
    parser.add_argument("--topics",
                        help="Comma separated list of topics to subscribe to.")
    parser.add_argument("--quiet", action="store_true", dest="quiet",
                        help="Turn off the MQTT logging.")
    parser.add_argument("config_file")

    return parser

def _get_option(option, default):
    if option:
        return option
    else:
        return default

def main():
    """ The main entry point. """
    parser = init_parser()
    options = parser.parse_args()

    if options.type == 'service':
        config_type = 'MQTTSubscribeService'
    else:
        config_type = 'MQTTSubscribeDriver'

    max_records = _get_option(options.max_records, None)

    if options.config_file:
        config_path = os.path.abspath(options.config_file)
        configuration = configobj.ConfigObj(config_path, file_error=True)
        config_dict = configuration.get(config_type, {})
    else:
        config_dict = {}

    host = _get_option(options.host, config_dict.get('host', 'localhost'))
    port = _get_option(options.port, int(config_dict.get('port', 1883)))
    keepalive = _get_option(options.keepalive, int(config_dict.get('keepalive', 60)))
    clientid = _get_option(options.clientid, config_dict.get('clientid', config_type + '-' + str(random.randint(1000, 9999))))
    username = _get_option(options.username, config_dict.get('username', None))
    password = _get_option(options.password, config_dict.get('password', None))

    topics = []
    if 'topic' in config_dict:
        topics.append(config_dict['topic'])
    else:
        if 'topics' in config_dict:
            for topic in config_dict['topics']:
                topics.append(topic)

    if options.topics:
        topics = options.topics.split(',')

    print("Host is %s" % host)
    print("Port is %s" % port)
    print("Keep alive is %s" % keepalive)
    print("Client id is %s" % clientid)
    print("Username is %s" % username)
    print("Password is %s" % password)
    print("Topics are %s" % topics)

    if password is not None:
        print("Password is set")
    else:
        print("Password is not set")

    userdata = {}
    userdata['topics'] = topics
    if max_records:
        userdata['counter'] = 0
        userdata['max_records'] = max_records
    client = mqtt.Client(client_id=clientid, userdata=userdata)

    if not options.quiet:
        client.on_log = on_log

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    if username is not None and password is not None:
        client.username_pw_set(username, password)

    client.connect(host, port, keepalive)

    client.loop_forever()

main()
