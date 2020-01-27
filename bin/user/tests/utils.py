# pylint: disable=missing-docstring

import json

def send_individual_msgs(on_message, topics):
    for topic in topics:
        topic_info = topics[topic]
        for field in topic_info['data']:
            on_message(None, None, Msg("%s/%s" % (topic, field), topic_info['data'][field], 0, 0))

def send_json_msgs(on_message, topics):
    for topic in topics:
        topic_info = topics[topic]
        payload = json.dumps(topic_info['data'])
        print(payload)
        on_message(None, None, payload)

def send_keyword_msgs(on_message, topics):
    for topic in topics:
        topic_info = topics[topic]
        if 'separator' in topic_info:
            print("      %s" % topic_info['separator'])
        if 'delimiter' in topic_info:
            print("      %s" % topic_info['delimiter'])
        payload = ''
        data = topic_info['data']
        for field in data:
            payload = "%s%s%s%s%s" % (payload, field, topic_info['delimiter'], data[field], topic_info['separator'])

        payload = payload[:-1]
        print(payload)
        on_message(None, None, payload)

class Msg(object):
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain
