#
#    Copyright (c) 2020-2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

import json
import time

import configobj
import random
import string

import weeutil

def random_string(length=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])

def byteify(data, ignore_dicts=False):
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

def on_connect_v1(client, userdata, _flags, _rc):
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
        (result, mid) = client.subscribe(topic)
    userdata['connected_flag'] = True

def on_connect_v2(client, userdata, _flags, _reason_code, _properties):
    for topic in userdata['topics']:
        (result, mid) = client.subscribe(topic)
    userdata['connected_flag'] = True

def on_message(client, userdata, msg):
    userdata['msg'] = True
    # print(msg.topic)
    # print(msg.payload)

def send_mqtt_msg(publisher, topic, payload, userdata, self):
    userdata['msg'] = False
    max_msg_wait = 20
    sleep_time = 1
    time.sleep(1)
    mqtt_message_info = publisher(topic, payload)
    mqtt_message_info.wait_for_publish()
    i = 1
    time.sleep(.5)  # give it a bit of time before checking
    while not userdata['msg']:
        print(f"waiting for mqtt message {i}")
        if i > max_msg_wait:
            self.fail(f"Timed out waiting for MQTT message {i}.")
        time.sleep(sleep_time)
        i += 1
        # sleep_time += 1

def send_direct_msg(publisher, topic, payload, userdata, self):
    # match function signature pylint: disable=unused-argument
    publisher(Msg(topic, payload, 0, 0))

def send_msg(sender, msg_type, publisher, topic, topic_info, userdata=None, self=None):
    # pylint: disable=too-many-arguments
    i = 0
    if msg_type == 'individual':
        for field in sorted(topic_info['data']):  # a bit of a hack, but need a determined order
            payload = topic_info['data'][field]
            if isinstance(payload, int):
                payload = str(payload).encode("utf-8")
            sender(publisher, f"{topic}/{field}", payload, userdata, self)
            i += 1
    elif msg_type == 'json':
        payload = json.dumps(topic_info['data']).encode("utf-8")
        sender(publisher, topic, payload, userdata, self)
        i += 1
    elif msg_type == 'keyword':
        msg = ''
        for field in topic_info['data']:
            msg = f"{msg}{field}{topic_info['delimiter']}{topic_info['data'][field]}{topic_info['separator']}"
        msg = msg[:-1]
        msg = msg.encode("utf-8")
        sender(publisher, topic, msg, userdata, self)
        i += 1
    else:
        separator = '\n'
        msg = separator.join(topic_info['msg'])
        sender(publisher, topic, msg, userdata, self)

    return i

def get_callback(payload_type, config_dict, manager, logger):
    message_callback_config = config_dict.get('message_callback', configobj.ConfigObj({}))
    message_callback_config['type'] = payload_type

    message_callback_provider_name = config_dict.get('message_callback_provider',
                                                     'user.MQTTSubscribe.MessageCallbackProvider')

    message_callback_provider_class = weeutil.weeutil.get_object(message_callback_provider_name)
    message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                logger,
                                                                manager)

    return message_callback_provider.get_callback()

# A bit of a hack, ok huge, to wait until MQTTSubscribe has queued the data
# This is useful when debugging MQTTSubscribe with breakpoints
def wait_on_queue(provider, msg_count, max_waits, sleep_time):
    wait_count = 0
    while True:
        queue_count = 0
        for subscribed_topic in provider.subscriber.manager.subscribed_topics:
            topic_queue = provider.subscriber.manager._get_queue(subscribed_topic)
            queue_count = queue_count + len(topic_queue)

        wait_count += 1
        if queue_count >= msg_count or wait_count >= max_waits:
            break
        time.sleep(sleep_time)

    return wait_count

def check(self, test_type, results, expected_results):
    self.longMessage = True
    msg = f"\n\t{results}\n\t{expected_results}"
    self.assertEqual(len(results), len(expected_results), msg)
    i = 0
    for expected_result in expected_results:
        # print("testing %s %s" % (test_type, expected_result))
        msg = f"\n\t{expected_results}\n\t{results[i]}"
        self.assertEqual(len(expected_result), len(results[i]), msg)
        for field in expected_result:
            self.assertIn(field, results[i])
            if expected_result[field] is not None:
                msg = f"for payload of {test_type} and field {field} in record {i+1}\n"
                if expected_result[field] == "None":
                    msg = f"\n\t for field {field}"
                    self.assertIsNone(results[i][field], msg)
                else:
                    msg = f"\n\t for field {field}"
                    self.assertEqual(results[i][field], expected_result[field], msg)
        i += 1

class Msg:
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain
