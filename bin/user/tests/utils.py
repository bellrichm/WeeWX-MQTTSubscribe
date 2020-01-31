# pylint: disable=missing-docstring

import json
import sys

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
