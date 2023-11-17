#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""
Configuration:
[MQTTSubscribeService] or [MQTTSubscribeDriver]

    # The message callback provider.
    message_callback_provider = user.ExampleMessageCallbackProvider.MessageCallbackProvider

"""

import xml.etree.ElementTree
import user.MQTTSubscribe

from weeutil.weeutil import to_float # used in eval statement pylint: disable=unused-import

class MessageCallbackProvider(user.MQTTSubscribe.AbstractMessageCallbackProvider):
    # pylint: disable=too-few-public-methods
    """ Provide the MQTT callback. """
    def __init__(self, _config, logger, topic_manager):
        super().__init__(logger, topic_manager)

    def get_callback(self):
        """ Get the MQTT callback. """
        return self._on_message

    def get_observations(self, parent, fullname, fields, unit_system):
        """ Create the dictionary of observations. """
        observations = {}
        conversion_func = {
            'source': 'lambda x: to_float(x)',
            'compiled': eval('lambda x: to_float(x)') # pylint: disable=eval-used
        }

        for child in parent:
            saved_fullname = fullname
            fullname = fullname + '/' + child.tag
            observations.update(self.get_observations(child, fullname, fields, unit_system))
            fullname = saved_fullname

        if parent.text is None:
            for (_, tvalue) in parent.items():
                (fieldname, value) = self._update_data(fullname[1:], tvalue, fields, conversion_func,  unit_system) # pylint: disable=eval-used
                observations[fieldname] = value
        elif not parent:
            (fieldname, value) = self._update_data(fullname[1:], parent.text, fields, conversion_func, unit_system) # pylint: disable=eval-used
            observations[fieldname] = value

        return observations

    def _on_message(self, _client, _userdata, msg):
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self.logger.debug(f"MessageCallbackProvider For {msg.topic} received: {msg.payload}")
            fields = self.topic_manager.get_fields(msg.topic)
            unit_system = self.topic_manager.get_unit_system(msg.topic) # TODO - need public method
            root = xml.etree.ElementTree.fromstring(msg.payload)
            observations = self.get_observations(root, "", fields, unit_system)

            if observations:
                self.topic_manager.append_data(msg.topic, observations)

        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self.logger.error(f"MessageCallbackProvider on_message_keyword failed with: {exception}")
            self.logger.error(f"**** MessageCallbackProvider Ignoring topic={msg.topic} and payload={msg.payload}")
