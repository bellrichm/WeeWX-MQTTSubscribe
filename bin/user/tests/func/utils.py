# pylint: disable=missing-docstring
# pylint: disable=fixme

import json
import sys
import time

import weeutil

PY2 = sys.version_info[0] == 2

def byteify(data, ignore_dicts=False):
    if PY2:
        # if this is a unicode string, return its string representation
        if isinstance(data, unicode): # (never called under python 3) pylint: disable=undefined-variable
            return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            byteify(key, ignore_dicts=True): byteify(value, ignore_dicts=True)
            for key, value in data.items()
        }
    # if it's anything else, return it in its original form
    return data

def on_connect(client, userdata, flags, rc): # (match callback signature) pylint: disable=unused-argument
    # https://pypi.org/project/paho-mqtt/#on-connect
    # rc:
    # 0: Connection successful
    # 1: Connection refused - incorrect protocol version
    # 2: Connection refused - invalid client identifier
    # 3: Connection refused - server unavailable
    # 4: Connection refused - bad username or password
    # 5: Connection refused - not authorised
    # 6-255: Currently unused.
    for topic in userdata['topics']:
        (result, mid) = client.subscribe(topic) # (match callback signature) pylint: disable=unused-variable
    userdata['connected_flag'] = True

def on_message(client, userdata, msg): # (match callback signature) pylint: disable=unused-argument
    userdata['msg'] = True
    #print(msg.topic)
    #print(msg.payload)

def send_mqtt_msg(publisher, topic, payload, userdata):
    userdata['msg'] = False
    mqtt_message_info = publisher(topic, payload)
    mqtt_message_info.wait_for_publish()
    while not userdata['msg']:
        #print("sleeping")
        time.sleep(1)

def send_direct_msg(publisher, topic, payload, userdata=None):
    # match function signature pylint: disable=unused-argument
    publisher(None, None, Msg(topic, payload, 0, 0))

def send_msg(sender, msg_type, publisher, topic, topic_info, userdata=None):
    # pylint: disable=too-many-arguments
    if msg_type == 'individual':
        for field in sorted(topic_info['data']): # a bit of a hack, but need a determined order
            payload = topic_info['data'][field]
            sender(publisher, "%s/%s" % (topic, field), payload, userdata)
    elif msg_type == 'json':
        payload = json.dumps(topic_info['data'])
        sender(publisher, topic, payload, userdata)
    elif msg_type == 'keyword':
        msg = ''
        for field in topic_info['data']:
            msg = "%s%s%s%s%s" % (msg, field, topic_info['delimiter'], topic_info['data'][field], topic_info['separator'])
        msg = msg[:-1]
        msg = msg.encode("utf-8")
        sender(publisher, topic, msg, userdata)

def get_callback(payload_type, config_dict, manager, logger):
    message_callback_config = config_dict.get('message_callback', {})
    message_callback_config['type'] = payload_type

    message_callback_provider_name = config_dict.get('message_callback_provider',
                                                     'user.MQTTSubscribe.MessageCallbackProvider')

    message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
    message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                logger,
                                                                manager)

    return message_callback_provider.get_callback()

def check(self, test_type, results, expected_results):
    msg = "for payload of %s" % test_type
    #print(results)
    #print(expected_results['results'])
    self.assertEqual(len(results), len(expected_results), msg)
    i = 0
    for expected_result in expected_results:
        print("testing %s %s" % (test_type, expected_result))
        for field in expected_result:
            msg = "for payload of %s and field %s in record %i" % (test_type, field, i+1)
            self.assertIn(field, results[i], msg)
            if expected_result[field] is not None:
                msg = "for payload of %s and field %s in record %i" % (test_type, field, i+1)
                if expected_result[field] == "None": # ToDo - cleanup
                    self.assertIsNone(results[i][field], msg)
                else:
                    self.assertEqual(results[i][field], expected_result[field], msg)
        i += 1

class Msg(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain
