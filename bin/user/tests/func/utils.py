# pylint: disable=missing-docstring
# pylint: disable=fixme

import json
import sys

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

def send_individual_msgs(on_message, topics):
    for topic in topics:
        topic_info = topics[topic]
        for field in sorted(topic_info['data']): # a bit of a hack, but need a determined order
            on_message(None, None, Msg("%s/%s" % (topic, field), topic_info['data'][field], 0, 0))

def send_json_msgs(on_message, topics):
    for topic in topics:
        topic_info = topics[topic]
        payload = json.dumps(topic_info['data'])
        on_message(None, None, Msg(topic, payload, 0, 0))

def send_keyword_msgs(on_message, topics):
    for topic in topics:
        topic_info = topics[topic]
        payload = ''
        data = topic_info['data']
        for field in data:
            payload = "%s%s%s%s%s" % (payload, field, topic_info['delimiter'], data[field], topic_info['separator'])

        payload = payload[:-1]
        payload = payload.encode("utf-8")
        on_message(None, None, Msg(topic, payload, 0, 0))

def setup(test, config_dict, record, manager, logger):
    if test['type'] == 'individual':
        msg_def = INDIVIDUAL_PAYLOAD
    elif test['type'] == 'json':
        msg_def = JSON_PAYLOAD
    elif test['type'] == 'keyword':
        msg_def = KEYWORD_PAYLOAD

    message_callback_config = config_dict.get('message_callback', None)
    if message_callback_config is None:
        raise ValueError("[[message_callback]] is required.")

    message_callback_config['type'] = msg_def['payload_type']

    message_callback_provider_name = config_dict.get('message_callback_provider',
                                                     'user.MQTTSubscribe.MessageCallbackProvider')

    message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
    message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                logger,
                                                                manager)

    on_message = message_callback_provider.get_callback()
    for topics in record:
        msg_def['on_message'](on_message, topics)

def check(self, records, test):
    msg = "for payload of %s" % test['type']
    #print(records)
    #print(test)
    self.assertEqual(len(records), len(test['records']), msg)
    i = 0
    for recordx in test['records']:
        print("testing %s %s" % (test['type'], recordx))
        for field in recordx:
            msg = "for payload of %s and field %s in record %i" % (test['type'], field, i+1)
            self.assertIn(field, records[i], msg)
            if recordx[field]:
                msg = "for payload of %s and field %s in record %i" % (test['type'], field, i+1)
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

INDIVIDUAL_PAYLOAD = {
    'payload_type': 'individual',
    'on_message': send_individual_msgs
}

JSON_PAYLOAD = {
    'payload_type': 'json',
    'on_message': send_json_msgs
}

KEYWORD_PAYLOAD = {
    'payload_type': 'keyword',
    'on_message': send_keyword_msgs
}
