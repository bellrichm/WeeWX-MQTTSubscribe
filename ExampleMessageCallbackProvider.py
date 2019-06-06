"""


Configuration:
[MQTTSubscribeService] or [MQTTSubscribeDriver]

    # The message callback provider.
    message_callback_provider = user.ExampleMessageCallbackProvider.MessageCallbackProvider

    # Configuration for the message callback.
    [[message_callback]]
        # The delimiter between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is: ,
        keyword_delimiter = ,

        # The separator between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is: =
        keyword_separator = =

        # Mapping to WeeWX names.
        [[[label_map]]]
            temp1 = extraTemp1
"""

class MessageCallbackProvider:
    def __init__(self, config, logger, topic_manager):
        self.logger = logger
        self.topic_manager = topic_manager
        self.keyword_delimiter = config.get('keyword_delimiter', ',')
        self.keyword_separator = config.get('keyword_separator', '=')
        self.label_map = config.get('label_map', {})

    def get_callback(self):
        return self._on_message

    def _on_message(self, client, userdata, msg):
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            topic = msg.topic
            self.logger.logdbg("MQTTSubscribe", "MessageCallbackProvider For %s received: %s" %(msg.topic, msg.payload))

            fields = msg.payload.split(self.keyword_delimiter)
            data = {}
            for field in fields:
                eq_index = field.find(self.keyword_separator)
                # Ignore all fields that do not have the separator
                if eq_index == -1:
                    self.logger.logerr("MQTTSubscribe", "MessageCallbackProvider on_message_keyword failed to find separator: %s" % self.keyword_separator)
                    self.logger.logerr("MQTTSubscribe", "**** MessageCallbackProvider Ignoring field=%s " % field)
                    continue

                name = field[:eq_index].strip()
                value = field[eq_index + 1:].strip()
                data[self.label_map.get(name, name)] = to_float(value)

            if data:
                self.topic_manager.append_data(msg.topic, data)
            else:
                self.logger.logerr("MQTTSubscribe", "MessageCallbackProvider on_message_keyword failed to find data in: topic=%s and payload=%s" % (msg.topic, msg.payload))
        
        except Exception as exception:
            self.logger.logerr("MQTTSubscribe", "MessageCallbackProvider on_message_keyword failed with: %s" % exception)
            self.logger.logerr("MQTTSubscribe", "**** MessageCallbackProvider Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))
