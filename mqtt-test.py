#!/usr/bin/python

import configobj
import optparse
import os
import paho.mqtt.client as mqtt
import random

usage = """mqtt-test --help
       mqtt-test [CONFIG_FILE]
           [--type=[driver|service]]
           [--host=HOST]
           [--port=PORT]
           [--keepalive=KEEPALIVE]
           [--clientid=CLIENTID]
           [--username=USERNAME]
           [--password=PASSWORD]
           [--topics=TOPIC1,TOPIC2]
           [--quiet]


A simple utility that prints the topis and payloads.
Configuration can be read from a 'weewx.conf' file or passed in.
Command line options override any options in the file.
"""

def on_log(client, userdata, level, msg):
    log_level = {
        mqtt.MQTT_LOG_INFO: 'MQTT_LOG_INFO',
        mqtt.MQTT_LOG_NOTICE: 'MQTT_LOG_NOTICE',
        mqtt.MQTT_LOG_WARNING: 'MQTT_LOG_WARNING',
        mqtt.MQTT_LOG_ERR: 'MQTT_LOG_ERR',
        mqtt.MQTT_LOG_DEBUG: 'MQTT_LOG_DEBUG'
    }

    print("%s: %s" % (log_level[level], msg))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for topic in userdata['topics']:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    print('%s: %s\n' %(msg.topic, msg.payload))

def init_parser():
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("--type", choices=["driver", "service"],
                    help="The simulation type.",
                    default="driver")
    parser.add_option("--host",
                    help="The MQTT server.")
    parser.add_option('--port', dest='port', type=int,
                        help='The port to connect to.')
    parser.add_option('--keepalive', dest='keepalive', type=int,
                        help='Maximum period in seconds allowed between communications with the broker.')
    parser.add_option("--clientid",
                    help="The clientid to connect with.")
    parser.add_option("--username",
                    help="username for broker authentication.")
    parser.add_option("--password",
                    help="password for broker authentication.")
    parser.add_option("--topics",
                    help="Comma separated list of topics to subscribe to.")
    parser.add_option("--quiet", action="store_true", dest="quiet",
                    help="Turn off the MQTT logging.")

    return parser

def get_option(option, default):
    if option:
        return option
    else:
        return default

def main():
    parser = init_parser()
    (options, args) = parser.parse_args()

    if options.type == 'service':
        config_type = 'MQTTSubscribeService'
    else:
        config_type = 'MQTTSubscribeDriver'

    if args:
        config_path = os.path.abspath(args[0])
        configuration = configobj.ConfigObj(config_path, file_error=True)
        config_dict = configuration.get(config_type, {})
    else:
        config_dict = {}
        
    host = get_option(options.host, config_dict.get('host', 'localhost'))
    port = get_option(options.port, int(config_dict.get('port', 1883)))
    keepalive = get_option(options.keepalive, int(config_dict.get('keepalive', 60)))
    clientid = get_option(options.clientid, config_dict.get('clientid', config_type + '-' + str(random.randint(1000, 9999))))
    username = get_option(options.username, config_dict.get('username', None))
    password = get_option(options.password, config_dict.get('password', None))

    if 'topic' in config_dict:
        topics = config_dict['topic']
    else:
        default_topics = []
        for topic in config_dict['topics']:
            default_topics.append(topic)

    topics = get_option(options.topics, default_topics)

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
    client = mqtt.Client(client_id=clientid, userdata=userdata)

    if not options.quiet:
      client.on_log = on_log

    client.on_connect = on_connect
    client.on_message = on_message

    if username is not None and password is not None:
        self.client.username_pw_set(username, password)

    client.connect(host, port, keepalive)

    client.loop_forever()

main()