# pylint: disable=missing-docstring

import json
import sys

import weeutil

PY2 = sys.version_info[0] == 2

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
    self.assertEqual(len(records), len(test['records']), msg)
    i = 0
    for recordx in test['records']:
        for field in recordx:
            self.assertIn(field, records[i], msg)
            if recordx[field]:
                self.assertEqual(records[i][field], recordx[field], msg)
        i = +1

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
