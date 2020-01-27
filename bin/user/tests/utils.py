# pylint: disable=missing-docstring

def send_individual_msgs(on_message, topics):
    for topic in topics:
        topic_info = topics[topic]
        if 'separator' in topic_info:
            print("      %s" % topic_info['separator'])
        if 'delimiter' in topic_info:
            print("      %s" % topic_info['delimiter'])
        for field in topic_info['data']:
            on_message(None, None, Msg("%s/%s" % (topic, field), topic_info['data'][field], 0, 0))

class Msg(object):
    def __init__(self, topic, payload, qos, retain):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain
