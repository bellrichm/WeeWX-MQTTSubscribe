"""
Configuration:
[MQTTSubscribeService] or [MQTTSubscribeDriver]

    # The message callback provider.
    message_callback_provider = user.ExampleMessageCallbackProvider.MessageCallbackProvider

"""

# need to be python 2 compatible pylint: disable=bad-option-value, raise-missing-from, super-with-arguments
# pylint: enable=bad-option-value

import xml.etree.ElementTree
import user.MQTTSubscribe

class MessageCallbackProvider(user.MQTTSubscribe.AbstractMessageCallbackProvider):
    # pylint: disable=too-few-public-methods
    """ Provide the MQTT callback. """
    def __init__(self, config, logger, topic_manager): # need to match signature pylint: disable=unused-argument
        super(MessageCallbackProvider, self).__init__(logger, topic_manager)

    def get_callback(self):
        """ Get the MQTT callback. """
        return self._on_message

    def get_observations(self, parent, fullname, fields, unit_system):
        """ Create the dictionary of observations. """
        observations = {}

        for child in parent:
            saved_fullname = fullname
            fullname = fullname + '/' + child.tag
            observations.update(self.get_observations(child, fullname, fields, unit_system))
            fullname = saved_fullname

        if parent.text is None:
            for (name, tvalue) in parent.items(): # need to match signature pylint: disable=unused-variable
                (fieldname, value) = self._update_data(fields, fullname[1:], tvalue, unit_system)
                observations[fieldname] = value
        elif not parent:
            (fieldname, value) = self._update_data(fields, fullname[1:], parent.text, unit_system)
            observations[fieldname] = value

        return observations

    def _on_message(self, client, userdata, msg):  # (match callback signature) pylint: disable=unused-argument
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self.logger.debug("MessageCallbackProvider For %s received: %s" %(msg.topic, msg.payload))
            fields = self.topic_manager.get_fields(msg.topic)
            unit_system = self.topic_manager.get_unit_system(msg.topic) # TODO - need public method
            root = xml.etree.ElementTree.fromstring(msg.payload)
            observations = self.get_observations(root, "", fields, unit_system)

            if observations:
                self.topic_manager.append_data(msg.topic, observations)

        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self.logger.error("MessageCallbackProvider on_message_keyword failed with: %s" % exception)
            self.logger.error("**** MessageCallbackProvider Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))
