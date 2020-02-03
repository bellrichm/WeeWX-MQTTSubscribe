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

def send_msg(msgtype, on_message, topics):
    if msgtype == 'individual':
        for topic in topics:
            topic_info = topics[topic]
            topic = "%s/#" % topic
            for field in sorted(topic_info['data']): # a bit of a hack, but need a determined order
                on_message(None, None, Msg("%s/%s" % (topic, field), topic_info['data'][field], 0, 0))
    elif msgtype == 'json':
        for topic in topics:
            topic_info = topics[topic]
            payload = json.dumps(topic_info['data'])
            on_message(None, None, Msg(topic, payload, 0, 0))
    elif msgtype == 'keyword':
        for topic in topics:
            topic_info = topics[topic]
            payload = ''
            data = topic_info['data']
            for field in data:
                payload = "%s%s%s%s%s" % (payload, field, topic_info['delimiter'], data[field], topic_info['separator'])

            payload = payload[:-1]
            payload = payload.encode("utf-8")
            on_message(None, None, Msg(topic, payload, 0, 0))

def send_msg2(msg_type, client, topic, topic_info, userdata):
    if msg_type == 'individual':
        for field in sorted(topic_info['data']): # a bit of a hack, but need a determined order
            userdata['msg'] = False
            mqtt_message_info = client.publish("%s/%s" % (topic, field), topic_info['data'][field])
            mqtt_message_info.wait_for_publish()
            while not userdata['msg']:
                #print("sleeping")
                time.sleep(1)
    elif msg_type == 'json':
        payload = json.dumps(topic_info['data'])
        userdata['msg'] = False
        mqtt_message_info = client.publish(topic, payload)
        mqtt_message_info.wait_for_publish()
        while not userdata['msg']:
            #print("sleeping")
            time.sleep(1)
    elif msg_type == 'keyword':
        msg = ''
        data = topic_info['data']
        for field in data:
            msg = "%s%s%s%s%s" % (msg, field, topic_info['delimiter'], data[field], topic_info['separator'])
        msg = msg[:-1]
        msg = msg.encode("utf-8")
        userdata['msg'] = False
        mqtt_message_info = client.publish(topic, msg)
        mqtt_message_info.wait_for_publish()
        while not userdata['msg']:
            #print("sleeping")
            time.sleep(1)

def setup(payload_type, config_dict, manager, logger):

    message_callback_config = config_dict.get('message_callback', None)
    if message_callback_config is None:
        raise ValueError("[[message_callback]] is required.")

    message_callback_config['type'] = payload_type

    message_callback_provider_name = config_dict.get('message_callback_provider',
                                                     'user.MQTTSubscribe.MessageCallbackProvider')

    message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
    message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                logger,
                                                                manager)

    return message_callback_provider.get_callback()

def check(self, test_type, records, test):
    msg = "for payload of %s" % test_type
    #print(records)
    #print(test['records'])
    self.assertEqual(len(records), len(test), msg)
    i = 0
    for recordx in test:
        print("testing %s %s" % (test_type, recordx))
        for field in recordx:
            msg = "for payload of %s and field %s in record %i" % (test_type, field, i+1)
            self.assertIn(field, records[i], msg)
            if recordx[field] is not None:
                msg = "for payload of %s and field %s in record %i" % (test_type, field, i+1)
                if recordx[field] == "None": # ToDo - cleanup
                    self.assertIsNone(records[i][field], msg)
                else:
                    self.assertEqual(records[i][field], recordx[field], msg)
        i += 1

class Msg(object):
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain
