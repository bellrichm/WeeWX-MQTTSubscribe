#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""
WeeWX driver and service that subscribes to MQTT topics and
creates/updates loop packets/archive records.

Installation:
    1. Put this file in the bin/user directory.
    2. Update weewx.conf [MQTTSubscribeService] as needed to configure the service.
    OR
    Update weewx.conf [MQTTSubscribeDriver] as needed to configure the driver.
    3. Update weewx.conf [Accumulator] for any custom fields.

Overview:
    The MQTT loop_start is used to run a separate thread to manage the MQTT subscriptions.
    The payloads are put on a queue to be processed by the driver or service.

    The service binds to either the NEW_LOOP_PACKET or NEW_ARCHIVE_RECORD event.
    On this event, it processes the queue of MQTT payloads and updates the packet or record

    The driver processes the queue and generates a packet for each element currently in the queue.
    A topic can be desinated as an 'archive topic'. Data in this topic is returned as an archive record.
"""

CONFIG_SPEC_TEXT = \
"""
# [MQTTSubscribeService] or [MQTTSubscribeDriver]
[MQTTSubscribe]
    # The driver to use.
    # Only used by the driver.
    driver = user.MQTTSubscribe

    # Turn the service on and off.
    # Default is true.
    # Only used by the service.
    enable = false    

    # The binding, loop or archive.
    # Default is loop.
    # Only used by the service.
    binding = loop    

    # The MQTT server.
    # Default is localhost.
    host = localhost

    # Maximum period in seconds allowed between communications with the broker.
    # Default is 60.
    keepalive = 60

    # Controls the MQTT logging.
    # Default is false.
    log = false

    # password for broker authentication.
    # Default is None.
    password = None

    # The port to connect to.
    # Default is 1883.
    port = 1883

    # username for broker authentication.
    # Default is None.
    username = None

    # Less common options follow

    # Payload in this topic is processed like an archive record.
    # Default is None.
    # Only used by the driver.
    archive_topic = None

    # The WeeWX archive interval.
    # The default is 300.
    # Only used when the archive_topic is set and MQTTSubscribe is running in 'hardware generation' mode.
    archive_interval = 300

    # The MQTT clean_session setting.
    # Default is True
    clean_session = True

    # The clientid to connect with.
    # Service default is MQTTSubscribeService-xxxx.
    # Driver default is MQTTSubscribeDriver-xxxx.
    #    Where xxxx is a random number between 1000 and 9999.
    clientid =

    # The name of a file to log to.
    # The default is None.
    logging_filename = None

    # The maximum time in seconds that the client will wait before trying to reconnect.
    # Default is 120
    max_delay = 120

    # When no loop packet has been generated in max_loop_interval, MQTTSubscribeDriver will generate an 'empty' packet.
    # This can be useful to ensure that archive processing regulary happens when the MQTT payload arrives very irregularly.
    # Default is 0 (off).
    # Only used by the driver
    max_loop_interval= 0

    # The minimum time in seconds that the client will wait before trying to reconnect.
    # Default is 1
    min_delay = 1    

    # When the MQTT queue has no data, the amount of time in seconds to wait
    # before checking again.
    # Default is 2.
    # Only used by the driver
    wait_before_retry = 2

    # The TLS options that are passed to tls_set method of the MQTT client.
    # For additional information see, https://eclipse.org/paho/clients/python/docs/strptime-format-codes
    [[tls]]
        # Turn tls on and off.
        # Default is true.
        enable = false

        # Path to the Certificate Authority certificate files that are to be treated as trusted by this client.
        ca_certs =

        # The PEM encoded client certificate and private keys.
        # Default is None
        certfile = None

        # The certificate requirements that the client imposes on the broker.
        # Valid values: none, optional, required
        # Default is required,
        certs_required = required

        # The encryption ciphers that are allowable for this connection. Specify None to use the defaults
        # Default is None.
        ciphers = None

        # The private keys.
        # Default is None
        keyfile = None

        # The version of the SSL/TLS protocol to be used.
        # Valid values: sslv2, sslv23, sslv3, tls, tlsv1, tlsv11, tlsv12.
        # Default is tlsv12.
        tls_version = tlsv12

    # Configuration for the message callback.
    # DEPRECATED - use [[[message]]] under [[topics]]
    [[message_callback]]
        # The format of the MQTT payload.
        # Currently support: individual, json, keyword
        # Must be specified.
        type = REPLACE_ME

        # When the json is nested, the delimiter between the hierarchies.
        # Default is _.
        flatten_delimiter = _

        # The delimiter between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is is ",".
        keyword_delimiter = ","

        # The separator between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is "=".
        keyword_separator = "="

    # For additional information see, https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Configuring#the-topic-name-sections
    [[topics]]
        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX.
        # For more information see, http://weewx.com/docs/customizing.htm#units
        # Default is US.
        unit_system = US

        # Less common options follow

        # Allow MQTT data with a datetime this many seconds after the current packet's datetime.
        # to be added to the current packet.
        # Default is 0.
        # Only used by the service.
        adjust_end_time = 0

        # Allow MQTT data with a datetime this many seconds prior to the previous packet's datetime.
        # to be added to the current packet.
        # Default is 0.
        # Only used by the service.
        adjust_start_time = 0

        # The name of the MQTT on_message callback.
        # Default is 'message'.
        callback_config_name = message

        # With the exception of wind data, by default a packet is created for every MQTT message received.
        # When this is true, MQTTSubscribe attempts to collect observations across messages into a packet.
        # Default is False.
        # This is experimental and may be removed.
        collect_observations = False

        # By default wind data is collected together across generation of loop packets.
        # Setting to false results in the data only being collected together within a loop packet.
        # Default is True.
        collect_wind_across_loops = True

        # Formatting string for converting a timestamp to an epoch datetime.
        # For additional information see, https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        # Default is None
        datetime_format = None

        # When the True, the MQTT data will continue to be processed even if its datetime is greater than the packet's datetime.
        # Default is False.
        # Only used by the service.
        ignore_end_time = False

        # When True, the MQTT datetime will be not be checked that is greater than the last packet processed.
        # Default is False.
        # Only used by the service.
        ignore_start_time = False

        # The maximum queue size.
        # When the queue is larger than this value, the oldest element is removed.
        # In general the queue should not grow large, but it might if the time
        # between the driver creating packets is large and the MQTT broker publishes frequently.
        # Or if subscribing to 'individual' payloads with wildcards. This results in many topic
        # in a single queue.
        max_queue = sys.maxsize         

        # Formatting string for converting time offset when converting a timestamp to an epoch datetime.
        # Default is None.
        # Example values: -hhmm +hhmm hh:mm
        offset_format = None

        # With the exception of wind data, by default a queue is created for every MQTT topic.
        # When this is true, MQTTSubsribe uses a single queue for all non wind data.
        # This is useful when 'collect_observations = True'.
        # Default is False.
        # This is experimental and may be removed.
        single_queue = False

        # Controls if this topic is subscribed to.
        # Default is True.
        subscribe = True

        # When true, the last segment of the topic is used as the fieldname.
        # Only used for individual payloads.
        # Default is False.
        # This is experimental and may be removed.
        topic_tail_is_fieldname = False

        # Even if the payload has a datetime, ignore it and use the server datetime.
        # Default is False.
        use_server_datetime = False

        # When true, the fieldname is set to the topic and therefore [[[[fieldname]]]] cannot be used.
        # This allows the [[[[fieldname]]]] configuration to be specified directly under the [[[topic]]].
        # Default is False.
        # DEPRECATED - no longer needed
        use_topic_as_fieldname = False

        # Configuration information about the MQTT message format for this topic
        [[[message]]]
            # The format of the MQTT payload.
            # Currently support: individual, json, keyword.
            # Must be specified.
            type = REPLACE_ME

            # When the json is nested, the delimiter between the hierarchies.
            # Default is _.
            flatten_delimiter = _

            # The delimiter between fieldname and value pairs. (field1=value1, field2=value2).
            # Default is is ",".
            keyword_delimiter = ","

            # The separator between fieldname and value pairs. (field1=value1, field2=value2).
            # Default is "=".
            keyword_separator = "="               

        # The first topic to subscribe to
        # For additional information see, https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Configuring#the-topic-name-sections
        [[[REPLACE_ME]]]
            # When set to false, the topic is not subscribed to.
            # Valid values: True, False
            # Default is True
            subscribe = True

            # Sets the default value for all fields in this topic.
            # Setting the value to 'true' "opts out" and the desired fields will need to set 'ignore = true'
            # Valid values: True, False.
            # Default is False.
            ignore = False            

            # Less common options follow

            # Specifies a field name in the mqtt message.
            # The value of the field is appended to every field name in the mqtt message.
            # This enables same formatted messages to map to different WeeWX fields.
            # Default is None.
            # Only used with json payloads.
            msg_id_field = None

            # The QOS level to subscribe to.
            # Default is 0
            qos = 0            
    
            # Configuration information about the MQTT message format for this topic
            # ToDo: create wiki entry and reference it
            [[[[message]]]]
                # The format of the MQTT payload.
                # Currently support: individual, json, keyword.
                # Must be specified.
                type = REPLACE_ME

                # When the json is nested, the delimiter between the hierarchies.
                # Default is _.
                flatten_delimiter = _

                # The delimiter between fieldname and value pairs. (field1=value1, field2=value2).
                # Default is is ",".
                keyword_delimiter = ","

                # The separator between fieldname and value pairs. (field1=value1, field2=value2).
                # Default is "=".
                keyword_separator = "="               

            # The incoming field name from MQTT.
            # For additional information see, https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Configuring#the-field-name-sections
            [[[[REPLACE_ME]]]]
                # True if the incoming field should not be processed into WeeWX.
                # Valid values: True, False.
                # Default is  derived from the 'ignore' option at the topic level.
                ignore = False

                # True if the incoming data is cumulative.
                # Valid values: True, False.
                # Default is False.
                contains_total = False      
      
                # The WeeWX name.
                # Default is the name from MQTT.
                name = REPLACE_ME

                # When True, the value in the field specified in msg_id_field is not appended to the fieldname in the mqtt message.
                # Valid values: True, False.
                # Default is False
                ignore_msg_id_field = False

                # Less common options follow

                # When True: if there is an exception converting the data type, the value is set to None.
                # When False: if there is an exception converting the data type, an error is logged and the MQTT msg is skipped.
                # Valid values: True, False.
                # Default is False.
                conversion_error_to_none = False
                
                # Valid values, a Python expression that when evaluated returns a valid value.
                # Example, conversion_func = lambda x: True if x == 'ON' else False
                # Default is not set.
                conversion_func = NOT_SET

                # The conversion type necessary for WeeWX compatibility.
                # Valid values: bool, float, int, none.
                # Default is float.
                conversion_type = float

                # In seconds how long the cache is valid.
                # Value of 0 means the cache is always expired.
                # Useful if missing fields should have a value of None instead of the previous value.
                # Value of None means the cache never expires.
                # Default is not set.
                # EXPERIMENTAL - may be removed
                expires_after = NOT_SET

                # When the field has any of the listed values, the MQTT message is not processed.
                # Any set of values separated by a comma is valid. For example: v1, v2, v3.
                # Default is empty.
                filter_out_message_when = ,
                # Only used for json payloads.
                # Note, conversion_type will most likely have to be set.

                # True if the cumulative data can wrap around.
                # Valid values: True, False.
                # Default is False.
                total_wrap_around = False
                                
                # The units of the incoming data.
                # Useful if this field's units differ from the topic's unit_system's units.
                # Valid values: see, http://www.weewx.com/docs/customizing.htm#units
                # Default is not set.
                units = NOT_SET

                # This is only valid when the fieldname is an array. Each subsection 'names' the element in the array.
                [[[[[subfields]]]]]
                    foo = foo # This is here to make ConfigObj formatting work
                    # Each subfield can be configured like a field in the json.
					[[[[[[REPLACE_ME]]]]]]
                        name = REPLACE_ME

        # The second topic to subscribe to
        [[[REPLACE_ME_TOO]]]
"""

ADDITIONAL_CONFIG_INFO = \
"""            
    # Configure additional observations and units for WeeWX to use.
    # See, http://weewx.com/docs/customizing.htm#Creating_a_new_unit_group
    # This assumes a good knowledge of customizing WeeWX.
    # EXPERIMENTAL - may be removed
    [[weewx]]
        [[[observations]]]
            # The observation and unit group it belongs to.
            observation-name = unit-group-name

        [[[units]]]
            # The unit to be added
            [[[[unit-name-a]]]]
                # The unit system this unit belongs to.
                unit_system = us
                # The unit group this unit belongs to.
                group = unit-group-name
                # Formatting for this unit.
                format = formatting for unit
                # Label for this unit.
                label = label for unit
                [[[[[conversion]]]]]
                    # Conversion formula to other unit.
                    to-unit-name-b = function to convert from unit to to-unit

            [[[[unit-name-b]]]]
                unit_system = metric, metricwx
"""

# readability, I want the config spec at the top of the file pylint: disable=wrong-import-position
import argparse
import copy
import datetime
import json
import locale
import logging
import os
import platform
import random
import re
import ssl
import sys
import syslog
import time
import traceback
from collections import deque

import configobj
import paho.mqtt.client as mqtt
from paho.mqtt.client import connack_string

import weecfg

import weeutil
import weeutil.logger
from weeutil.weeutil import to_bool, to_float, to_int, to_sorted_string

from weeutil.config import merge_config

import weewx
import weewx.drivers
from weewx.engine import StdEngine, StdService
# pylint: enable=wrong-import-position

VERSION = '3.0.0-rc01'
DRIVER_NAME = 'MQTTSubscribeDriver'
DRIVER_VERSION = VERSION

def gettid():
    """Get TID as displayed by htop.
       This is architecture dependent."""
    import ctypes # pylint: disable=import-outside-toplevel
    from ctypes.util import find_library # pylint: disable=import-outside-toplevel
    libc = ctypes.CDLL(find_library('c'))
    for cmd in (186, 224, 178):
        tid = ctypes.CDLL(libc).syscall(cmd)
        if tid != -1:
            return tid

    return 0

class ConversionError(ValueError):
    """ Error converting data types. """

class AbstractLogger():
    """ The abstract logging class. """
    def __init__(self, mode, level='NOTSET', filename=None, console=None):
        self.console = console
        self.mode = mode
        self.filename = filename
        self.weewx_debug = weewx.debug

        # Setup custom TRACE level
        self.trace_level = 5
        if logging.getLevelName(self.trace_level) == 'Level 5':
            logging.addLevelName(self.trace_level, "TRACE")

        # check that the level configured is valid
        self.level = logging._checkLevel(level)

    def log_environment(self, config_dict):
        """ Log the environment we are running in. """
        # Since WeeWX logs this, only log it when debugging
        self.debug(f"Using weewx version {weewx.__version__}")
        self.debug(f"Using Python {sys.version}")
        self.debug(f"Platform {platform.platform()}")
        self.debug(f"Locale is '{locale.setlocale(locale.LC_ALL)}'")

        self.debug(config_dict)
        archive_dict = config_dict.get('StdArchive', {})
        record_augmentation = archive_dict.get('record_augmentation', None)
        record_generation = archive_dict.get('record_generation', None)
        self.debug(f"Record Augmentation is: {record_augmentation}")
        self.debug(f"Record Generation is: {record_generation}")
        self.info(f"Version is {VERSION}")
        self.info(f"Log level: {int(self.level)}")
        self.info(f"Log debug setting: {int(self.weewx_debug)}")
        self.info(f"Log console: {self.console}")
        self.info(f"Log file: {self.filename}")

    def trace(self, msg):
        """ Log trace messages. """
        raise NotImplementedError("Method 'trace' not implemented")

    def debug(self, msg):
        """ Log debug messages. """
        raise NotImplementedError("Method 'debug' not implemented")

    def info(self, msg):
        """ Log info messages. """
        raise NotImplementedError("Method 'info' not implemented")

    def error(self, msg):
        """ Log error messages. """
        raise NotImplementedError("Method 'error' not implemented")

    def setup_logging(self, logging_level, config_dict):
        """ Setup logging for running in standalone mode."""
        if logging_level:
            weewx.debug = logging_level

        weeutil.logger.setup('wee_MQTTSS', config_dict)

class Logger(AbstractLogger):
    """ The logging class. """
    MSG_FORMAT = "(%s) %s"

    def __init__(self, mode, level='NOTSET', filename=None, console=None):
        super().__init__(mode, level, filename=filename, console=console)
        self._logmsg = logging.getLogger(__name__)
        if self.console:
            self._logmsg.addHandler(logging.StreamHandler(sys.stdout))

        if self.level > 0:
            self.weewx_debug = 0
            self._logmsg.propagate = 0
            self._logmsg.setLevel(self.level)
            # Get a copy of all the handlers
            handlers = self.get_handlers(self._logmsg.parent)
            for handler in handlers:
                handler.setLevel(self.level)
                self._logmsg.addHandler(handler)
        else:
            self.weewx_debug = weewx.debug

        if self.filename is not None:
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
            file_handler = logging.FileHandler(self.filename, mode='w')
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            self._logmsg.addHandler(file_handler)

    def get_handlers(self, logger):
        """ recursively get parent handlers """
        handlers = []
        for handler in logger.handlers:
            # Unfortunately cannot make a deep copy, but this seems safe
            # we only change the logging level...
            handlers.append(copy.copy(handler))

        if logger.propagate and logger.parent is not None:
            handlers.extend(self.get_handlers(logger.parent))

        return handlers

    def trace(self, msg):
        """ Log trace messages. """
        if self.weewx_debug > 1:
            self._logmsg.debug(self.MSG_FORMAT, self.mode, msg)
        else:
            self._logmsg.log(self.trace_level, self.MSG_FORMAT, self.mode, msg)

    def debug(self, msg):
        """ Log debug messages. """
        self._logmsg.debug(self.MSG_FORMAT, self.mode, msg)

    def info(self, msg):
        """ Log informational messages. """
        self._logmsg.info(self.MSG_FORMAT, self.mode, msg)

    def error(self, msg):
        """ Log error messages. """
        self._logmsg.error(self.MSG_FORMAT, self.mode, msg)

    class Logger(AbstractLogger):
        """ The logging class. """
        def __init__(self, mode, level='NOTSET', filename=None, console=None):
            super().__init__(mode, level, filename=filename, console=console)

            self.file = self._open_file(filename)

        def __del__(self):
            if self.file:
                self.file.close()

        def _open_file(self, filename):
            if filename is not None:
                return open(filename, 'w', encoding='UTF-8')
            return None

        def trace(self, msg):
            """ Log trace messages. """
            if self.level == self.trace_level or self.weewx_debug > 1:
                self._logmsg(syslog.LOG_DEBUG, msg)

        def debug(self, msg):
            """ Log debug messages. """
            if self.level <= 10:
                self._logmsg(syslog.LOG_DEBUG, msg)

        def info(self, msg):
            """ Log informational messages. """
            if self.level <= 20:
                self._logmsg(syslog.LOG_INFO, msg)

        def error(self, msg):
            """ Log error messages. """
            if self.level <= 40:
                self._logmsg(syslog.LOG_ERR, msg)

        def _logmsg(self, dst, msg):
            syslog.syslog(dst, f'({self.mode}) {__name__}: {msg}')
            if self.console:
                print(f'{__name__}: {msg}')
            if self.file:
                self.file.write(f'{__name__}: {msg}\n')

class RecordCache():
    """ Manage the cache. """
    def __init__(self):
        self.unit_system = None
        self.cached_values = {}

    def get_value(self, key, timestamp, expires_after):
        """ Get the cached value. """
        if key in self.cached_values and \
            (expires_after is None or timestamp - self.cached_values[key]['timestamp'] < expires_after):
            return self.cached_values[key]['value']

        return None

    def update_value(self, key, value, unit_system, timestamp):
        """ Update the cached value. """
        if self.unit_system is None:
            self.unit_system = unit_system
        if unit_system != self.unit_system:
            raise ValueError(f"Unit system does not match unit system of the cache. {unit_system} vs {self.unit_system}")
        self.cached_values[key] = {}
        self.cached_values[key]['value'] = value
        self.cached_values[key]['timestamp'] = timestamp

    def update_timestamp(self, key, timestamp):
        """ Update the ts. """
        if key in self.cached_values:
            self.cached_values[key]['timestamp'] = timestamp

    def remove_value(self, key):
        """ Remove a cached value. """
        if key in self.cached_values:
            del self.cached_values[key]

    def clear_cache(self):
        """ Clear the cache """
        self.cached_values = {}

class CollectData():
    """ Manage fields that are 'grouped together', like wind data. """
    def __init__(self, fields, unit_system):
        self.fields = fields
        self.unit_system = unit_system
        self.data = {}
        self.date_time = None

    def add_data(self, field, in_data):
        """ Add data to the collection and return old collection if this field is already in the collection. """
        self.date_time = in_data['dateTime']
        old_data = {}
        if field in self.data:
            old_data = dict(self.data)
            old_data['usUnits'] = self.unit_system
            old_data['dateTime'] = self.date_time
            self.data = {}

        target_data = dict(in_data)
        target_data = weewx.units.to_std_system(target_data, self.unit_system)
        if 'dateTime' in target_data:
            del target_data['dateTime']
        if 'usUnits' in target_data:
            del target_data['usUnits']

        self.data[field] = target_data[field]

        return old_data

    def add_dict(self, in_dict):
        """ Add data to the collection and return old collection if any field is already in the collection. """
        self.date_time = in_dict['dateTime']
        old_data = {}
        if any(item in in_dict for item in self.data):
            old_data = dict(self.data)
            old_data['usUnits'] = self.unit_system
            old_data['dateTime'] = self.date_time
            self.data = {}

        target_data = dict(in_dict)
        target_data = weewx.units.to_std_system(target_data, self.unit_system)
        if 'dateTime' in target_data:
            del target_data['dateTime']
        if 'usUnits' in target_data:
            del target_data['usUnits']

        self.data.update(target_data)

        return old_data

    def get_data(self):
        """ Return the collection. """
        if self.data:
            self.data['usUnits'] = self.unit_system
            self.data['dateTime'] = self.date_time
        return self.data

class TopicManager():
    """ Manage the MQTT topic subscriptions. """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, archive_topic, config, logger):
        self.logger = logger

        if not config.sections:
            raise ValueError("At least one topic must be configured.")

        self.message_config_name = f"message-{time.time():f}"

        topic_defaults = self._configure_topic_options(config)

        field_defaults = {}
        field_defaults['ignore_msg_id_field'] = config.get('ignore_msg_id_field', False)
        field_defaults['ignore'] = to_bool(config.get('ignore', False))
        field_defaults['contains_total'] = to_bool(config.get('contains_total', False))
        field_defaults['total_wrap_around'] = to_bool(config.get('total_wrap_around', False))
        field_defaults['conversion_type'] = config.get('conversion_type', 'float')
        field_defaults['conversion_error_to_none'] = to_bool(config.get('conversion_error_to_none', False))

        default_message_dict = config.get('message', configobj.ConfigObj())
        # if 'type' option is not set, this not 'topic'
        # so, no default 'message' configuration exists
        if default_message_dict.get('type', None) is None:
            default_message_dict = configobj.ConfigObj({})

        self.topics = {}
        self.subscribed_topics = {}
        self.cached_fields = {}
        self.queues = []

        single_queue = to_bool(config.get('single_queue', False))
        self.logger.debug(f"TopicManager single_queue is {single_queue}")
        single_queue_obj = None
        if single_queue:
            single_queue_obj = dict(
                {'name': f"{time.time():f}-single-queue",
                 'type': 'normal',
                 'ignore_start_time': topic_defaults['ignore_start_time'],
                 'ignore_end_time': topic_defaults['ignore_end_time'],
                 'adjust_start_time': topic_defaults['adjust_start_time'],
                 'adjust_end_time': topic_defaults['adjust_end_time'],
                 'max_size': topic_defaults['max_queue'],
                 'data': deque()
                }
            )
            self.queues.append(single_queue_obj)

        self._configure_topics(config, archive_topic, single_queue, single_queue_obj, default_message_dict, topic_defaults, field_defaults)

        self._add_collector_queue(topic_defaults)

        self.logger.debug(f"TopicManager self.subscribed_topics is {json.dumps(self.subscribed_topics, default=str)}")
        self.logger.debug(f"TopicManager self.cached_fields is {self.cached_fields}")

    def _configure_topics(self, config, archive_topic, single_queue, single_queue_obj, default_message_dict, topic_defaults, field_defaults):
        # pylint: disable=too-many-arguments, too-many-locals
        for topic in config.sections:
            topic_dict = config.get(topic, {})
            callback_config_name = topic_dict.get('callback_config_name', topic_defaults['callback_config_name'])

            # if 'type' option is set, this not a 'topic'
            # it is actually a 'callback (message)' configuration stanza
            # and it has already been retrieved into default_message_config
            if topic == callback_config_name and topic_dict.get('type', None) is not None:
                continue

            unit_system_name = topic_dict.get('unit_system', topic_defaults['unit_system_name']).strip().upper()
            if unit_system_name not in weewx.units.unit_constants:
                raise ValueError(f"MQTTSubscribe: Unknown unit system: {unit_system_name}")
            unit_system = weewx.units.unit_constants[unit_system_name]

            self.subscribed_topics[topic] = {}
            # ignore is set at the topic level in addtion to the field level
            # This allows it to be set to false at the topic level, changing MQTTSubscribe from an 'opt out' to 'opt in' strategy
            self.subscribed_topics[topic]['ignore'] = to_bool(topic_dict.get('ignore', field_defaults['ignore']))
            self.subscribed_topics[topic]['subscribe'] = to_bool(topic_dict.get('subscribe', True))

            self._set_conversion_func(topic, topic_dict)

            self.subscribed_topics[topic]['unit_system'] = unit_system
            self.subscribed_topics[topic]['msg_id_field'] = topic_dict.get('msg_id_field', topic_defaults['msg_id_field'])
            self.subscribed_topics[topic]['qos'] = to_int(topic_dict.get('qos', topic_defaults['qos']))
            self.subscribed_topics[topic]['topic_tail_is_fieldname'] = to_bool(topic_dict.get('topic_tail_is_fieldname',
                                                                                              topic_defaults['topic_tail_is_fieldname']))
            self.subscribed_topics[topic]['use_server_datetime'] = to_bool(topic_dict.get('use_server_datetime',
                                                                                          topic_defaults['use_server_datetime']))
            self.subscribed_topics[topic]['datetime_format'] = topic_dict.get('datetime_format', topic_defaults['datetime_format'])
            self.subscribed_topics[topic]['offset_format'] = topic_dict.get('offset_format', topic_defaults['offset_format'])
            self.subscribed_topics[topic]['ignore_msg_id_field'] = callback_config_name # ToDo - investigate
            self.subscribed_topics[topic]['ignore_msg_id_field'] = []
            self.subscribed_topics[topic]['fields'] = {}
            self._setup_queue(archive_topic, single_queue, single_queue_obj, topic_defaults, topic, topic_dict)

            self.subscribed_topics[topic]['filters'] = {}

            temp_message_dict = topic_dict.get(callback_config_name, {})
            message_type = temp_message_dict.get('type', None)

            # ugly "deep" copy workaround
            message_dict = configobj.ConfigObj({})
            message_dict.merge(default_message_dict)

            # if 'type' option is set, this a 'callback configuration (message)' section
            # So merge the default message settings
            if message_type is not None:
                message_dict.merge(temp_message_dict)
            self.subscribed_topics[topic][self.message_config_name] = message_dict

            if len(topic_dict.sections) > 1 or (len(topic_dict.sections) == 1  and message_type is None):
                self. _configure_topic_fields(field_defaults, callback_config_name, topic, topic_dict)
            else:
                self._configure_topic_as_field(field_defaults, topic, topic_dict)

    def _setup_queue(self, archive_topic, single_queue, single_queue_obj, topic_defaults, topic, topic_dict):
        # pylint: disable=too-many-arguments
        if not single_queue or topic == archive_topic:
            queue = dict(
                {'name': topic,
                    'type': 'normal',
                    'ignore_start_time': to_bool(topic_dict.get('ignore_start_time', topic_defaults['ignore_start_time'])),
                    'ignore_end_time': to_bool(topic_dict.get('ignore_end_time', topic_defaults['ignore_end_time'])),
                    'adjust_start_time': to_float(topic_dict.get('adjust_start_time', topic_defaults['adjust_start_time'])),
                    'adjust_end_time': to_float(topic_dict.get('adjust_end_time', topic_defaults['adjust_end_time'])),
                    'max_size': topic_dict.get('max_queue', topic_defaults['max_queue']),
                    'data': deque()
                }
            )
            self.queues.append(queue)
            self.subscribed_topics[topic]['queue'] = queue
        else:
            self.subscribed_topics[topic]['queue'] = single_queue_obj

    def _set_conversion_func(self, topic, topic_dict):
        conversion_type = topic_dict.get('conversion_type', 'float')
        self.subscribed_topics[topic]['conversion_func'] = {}
        if conversion_type == 'bool':
            self.subscribed_topics[topic]['conversion_func']['source'] = 'lambda x: to_bool(x)'
        elif conversion_type == 'float':
            self.subscribed_topics[topic]['conversion_func']['source'] = 'lambda x: to_float(x)'
        elif conversion_type == 'int':
            self.subscribed_topics[topic]['conversion_func']['source'] = 'lambda x: to_int(x)'
        else:
            self.subscribed_topics[topic]['conversion_func']['source'] = 'lambda x: x'
        # pylint: disable=eval-used
        self.subscribed_topics[topic]['conversion_func']['compiled'] = eval(self.subscribed_topics[topic]['conversion_func']['source'])
        # pylint: enable=eval-used

    def _configure_topic_fields(self, field_defaults, callback_config_name, topic, topic_dict):
        for field in topic_dict.sections:
            if field == callback_config_name and topic_dict[field].get('type', None) is not None:
                continue

            self.subscribed_topics[topic]['fields'][field] = self._configure_field(topic_dict, topic_dict[field], field, field_defaults)

            if self.subscribed_topics[topic]['fields'][field].get('subfields'):
                self.subscribed_topics[topic]['fields'][field]['ignore_msg_id_field'] = field_defaults['ignore_msg_id_field']

                self._configure_subfields(topic, field, topic_dict)

            else:
                self._configure_ignore_fields(topic_dict, topic_dict[field], topic, field, field_defaults)
            filter_values = weeutil.weeutil.option_as_list(topic_dict[field].get('filter_out_message_when', None))
            if filter_values:
                conversion_func = self.subscribed_topics[topic]['fields'][field]['conversion_func']['compiled']
                self._configure_filter_out_message(topic, field, filter_values, conversion_func)
            self._configure_cached_fields(topic_dict[field])

    def _configure_subfields(self, topic, field, topic_dict):
        for subfield in self.subscribed_topics[topic]['fields'][field].get('subfields', []):
            self.subscribed_topics[topic]['fields'][subfield] = \
                self._configure_field(self.subscribed_topics[topic]['fields'][field],
                                        topic_dict[field]['subfields'][subfield],
                                        subfield,
                                        self.subscribed_topics[topic]['fields'][field])
            if 'units' in self.subscribed_topics[topic]['fields'][field]:
                self.subscribed_topics[topic]['fields'][subfield]['units'] = \
                    self.subscribed_topics[topic]['fields'][field]['units']
            self._configure_ignore_fields(topic_dict,
                                            topic_dict[field],
                                            topic, subfield,
                                            self.subscribed_topics[topic]['fields'][field])

    def _configure_topic_as_field(self, field_defaults, topic, topic_dict):
        # See if any field options are directly under the topic.
        # And if so, use the topic as the field name.
        for (key, _) in topic_dict.items():
            if key not in self.topic_options:
                self.subscribed_topics[topic]['fields'][topic] = self._configure_field(topic_dict, topic_dict, topic, field_defaults)
                self._configure_ignore_fields(topic_dict, topic_dict, topic, topic, field_defaults)
                filter_values = weeutil.weeutil.option_as_list(topic_dict.get('filter_out_message_when', None))
                if filter_values:
                    conversion_func = self.subscribed_topics[topic]['fields'][topic]['conversion_func']['compiled']
                    self._configure_filter_out_message(topic, topic, filter_values, conversion_func)
                self._configure_cached_fields(topic_dict)
                break

    def _add_collector_queue(self, topic_defaults):
        # Add the collector queue as a subscribed topic so that data can retrieved from it
        # Yes, this is a bit of a hack.
        # Note, it would not be too hard to allow additional fields via the [fields] configuration option
        self.collected_units = weewx.units.unit_constants[topic_defaults['unit_system_name']]
        self.collected_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']
        self.collected_queue = deque()
        self.collected_topic = f"{time.time():f}-{'-'.join(self.collected_fields)}"
        topic = self.collected_topic
        self.subscribed_topics[topic] = {}
        self.subscribed_topics[topic]['subscribe'] = False
        self.subscribed_topics[topic][self.message_config_name] = {}
        self.subscribed_topics[topic]['unit_system'] = weewx.units.unit_constants[topic_defaults['unit_system_name']]
        self.subscribed_topics[topic]['qos'] = topic_defaults['qos']
        self.subscribed_topics[topic]['topic_tail_is_fieldname'] = topic_defaults['topic_tail_is_fieldname']
        self.subscribed_topics[topic]['use_server_datetime'] = topic_defaults['use_server_datetime']
        self.subscribed_topics[topic]['datetime_format'] = topic_defaults['datetime_format']
        self.subscribed_topics[topic]['offset_format'] = topic_defaults['offset_format']
        queue = dict(
            {'name': topic,
             'type': 'collector',
             'ignore_start_time': topic_defaults['ignore_start_time'],
             'ignore_end_time': topic_defaults['ignore_end_time'],
             'adjust_start_time': topic_defaults['adjust_start_time'],
             'adjust_end_time': topic_defaults['adjust_end_time'],
             'max_size': topic_defaults['max_queue'],
             'data': self.collected_queue
            }
        )
        self.subscribed_topics[topic]['queue'] = queue
        self.queues.append(queue)

        if self.collect_wind_across_loops:
            self.collector = CollectData(self.collected_fields, self.collected_units)

    def _configure_topic_options(self, config):
        self.topic_options = ['collect_wind_across_loops', 'collect_observations', 'single_queue', 'unit_system',
                              'msg_id_field', 'qos', 'topic_tail_is_fieldname',
                              'use_server_datetime', 'ignore_start_time', 'ignore_end_time', 'adjust_start_time', 'adjust_end_time',
                              'datetime_format', 'offset_format', 'max_queue']

        default = {}

        self.collect_wind_across_loops = to_bool(config.get('collect_wind_across_loops', True))
        self.logger.debug(f"TopicManager self.collect_wind_across_loops is {self.collect_wind_across_loops}")

        self.collect_observations = to_bool(config.get('collect_observations', False))
        self.logger.debug(f"TopicManager self.collect_observations is {self.collect_observations}")

        single_queue = to_bool(config.get('single_queue', False))
        self.logger.debug(f"TopicManager single_queue is {single_queue}")

        default['unit_system_name'] = config.get('unit_system', 'US').strip().upper()
        if default['unit_system_name'] not in weewx.units.unit_constants:
            raise ValueError(f"MQTTSubscribe: Unknown unit system: {default['unit_system_name']}")

        default['msg_id_field'] = config.get('msg_id_field', None)
        default['qos'] = to_int(config.get('qos', 0))
        default['topic_tail_is_fieldname'] = to_bool(config.get('topic_tail_is_fieldname', False))

        default['use_server_datetime'] = to_bool(config.get('use_server_datetime', False))
        default['ignore_start_time'] = to_bool(config.get('ignore_start_time', False))
        default['ignore_end_time'] = to_bool(config.get('ignore_end_time', False))
        if default['ignore_start_time']:
            default['adjust_start_time'] = to_float(config.get('adjust_start_time', 1))
        else:
            default['adjust_start_time'] = to_float(config.get('adjust_start_time', 0))
        default['adjust_end_time'] = to_float(config.get('adjust_end_time', 0))

        default['datetime_format'] = config.get('datetime_format', None)
        default['offset_format'] = config.get('offset_format', None)

        default['max_queue'] = config.get('max_queue', sys.maxsize)
        default['callback_config_name'] = config.get('callback_config_name', 'message')

        return default

    @staticmethod
    def _configure_field(topic_dict, field_dict, fieldname, defaults):
        ignore = to_bool(topic_dict.get('ignore', defaults['ignore']))
        contains_total = to_bool(topic_dict.get('contains_total', defaults['contains_total']))
        total_wrap_around = to_bool(topic_dict.get('total_wrap_around', defaults['total_wrap_around']))
        conversion_type = topic_dict.get('conversion_type', defaults['conversion_type'])
        conversion_error_to_none = topic_dict.get('conversion_error_to_none', defaults['conversion_error_to_none'])
        field = {}
        field['name'] = (field_dict).get('name', fieldname)
        field['ignore'] = to_bool((field_dict).get('ignore', ignore))
        field['contains_total'] = to_bool((field_dict).get('contains_total', contains_total))
        field['total_wrap_around'] = to_bool((field_dict).get('total_wrap_around', total_wrap_around))
        conversion_func = field_dict.get('conversion_func', None)
        conversion_type = field_dict.get('conversion_type', conversion_type)
        field['conversion_func'] = {}
        field['conversion_type'] = conversion_type # todo - hack so that a field configuration can be used as a default for its subfields
        if conversion_func:
            field['conversion_func']['source'] = conversion_func
        elif conversion_type == 'bool':
            field['conversion_func']['source'] = 'lambda x: to_bool(x)'
        elif conversion_type == 'float':
            field['conversion_func']['source'] = 'lambda x: to_float(x)'
        elif conversion_type == 'int':
            field['conversion_func']['source'] = 'lambda x: to_int(x)'
        else:
            field['conversion_func']['source'] = 'lambda x: x'
        field['conversion_func']['compiled'] = eval(field['conversion_func']['source']) # pylint: disable=eval-used
        field['conversion_error_to_none'] = (field_dict).get('conversion_error_to_none', conversion_error_to_none)
        if 'units' in field_dict:
            if field_dict['units'] in weewx.units.conversionDict and field['name'] in weewx.units.obs_group_dict:
                field['units'] = field_dict['units']
            else:
                raise ValueError(f"For {field['name']} invalid units, {field_dict['units']}.")

        if (field_dict).get('subfields', None):
            field['subfields'] = (field_dict)['subfields'].sections
        return field

    def _configure_filter_out_message(self, topic, fieldname, filter_values, conversion_func):
        values = []
        for value in filter_values:
            new_value = conversion_func(value)
            values.append(new_value)
        self.subscribed_topics[topic]['filters'].update({fieldname: values})

    def _configure_ignore_fields(self, topic_dict, field_dict, topic, fieldname, defaults):
        # pylint: disable=too-many-arguments, too-many-locals
        ignore_msg_id_field = topic_dict.get('ignore_msg_id_field', defaults['ignore_msg_id_field'])
        if to_bool((field_dict).get('ignore_msg_id_field', ignore_msg_id_field)):
            self.subscribed_topics[topic]['ignore_msg_id_field'].append(fieldname)

    def _configure_cached_fields(self, field_dict):
        if 'expires_after' in field_dict:
            weewx_name = field_dict['name']
            self.cached_fields[weewx_name] = {}
            self.cached_fields[weewx_name]['expires_after'] = to_float(field_dict['expires_after'])

    def append_data(self, topic, in_data, fieldname=None):
        """ Add the MQTT data to the queue. """
        self.logger.debug(f"TopicManager data-> incoming {topic}: {to_sorted_string(in_data)}")
        data = dict(in_data)
        payload = {}

        queue = self._get_queue(topic)
        use_server_datetime = self._get_value('use_server_datetime', topic)

        if 'dateTime' not in data or use_server_datetime:
            data['dateTime'] = time.time()
        if 'usUnits' not in data:
            data['usUnits'] = self.get_unit_system(topic)

        datetime_format = self._get_value('datetime_format', topic)
        if datetime_format and 'dateTime' in data:
            data['dateTime'] = self._to_epoch(data['dateTime'], datetime_format, self._get_value('offset_format', topic))

        payload['data'] = data

        if fieldname in self.collected_fields:
            self._queue_size_check(self.collected_queue, queue['max_size'])
            self.logger.trace(
                f"TopicManager Adding wind data {fieldname} {weeutil.weeutil.timestamp_to_string(data['dateTime'])}: {to_sorted_string(data)}")
            payload['fieldname'] = fieldname
            self.collected_queue.append(payload)
        else:
            self._queue_size_check(queue, queue['max_size'])
            self.logger.trace(
                (f"TopicManager Added to queue {topic} {self._lookup_topic(topic)} {weeutil.weeutil.timestamp_to_string(data['dateTime'])}: "
                f"{to_sorted_string(data)}"))
            queue['data'].append(payload,)

    def peek_datetime(self, queue):
        """ Return the date/time of the first element in the queue. """
        self.logger.trace(f"TopicManager queue size is: {len(queue)}")
        datetime_value = None
        if queue:
            datetime_value = queue[0]['data']['dateTime']

        return datetime_value

    def peek_last_datetime(self, queue):
        """ Return the date/time of the last element in the queue. """
        self.logger.trace(f"TopicManager queue size is: {len(queue)}")
        datetime_value = 0
        if queue:
            datetime_value = queue[-1]['data']['dateTime']

        return datetime_value

    def has_data(self, topic):
        """ Return True if queue has data. """
        return bool(self._get_queue(topic)['data'])

    def get_data(self, queue, end_ts=sys.maxsize):
        """ Get data off the queue of MQTT data. """
        queue_name = queue['name']
        data_queue = queue['data']
        self.logger.trace(f"TopicManager starting queue {queue_name} size is: {len(data_queue)}")
        if self.collect_wind_across_loops:
            collector = self.collector
        else:
            collector = CollectData(self.collected_fields, self.collected_units)

        observation_collector = None
        if self.collect_observations:
            observation_collector = CollectData(None, self.collected_units)

        for data in self._process_queue(end_ts, collector, observation_collector, queue):
            yield data

        if not self.collect_wind_across_loops:
            data = collector.get_data()
            if data:
                self.logger.debug(f"TopicManager data-> outgoing wind {queue_name}: {to_sorted_string(data)}")
                yield data

        if self.collect_observations:
            data = observation_collector.get_data()
            if data:
                self.logger.debug(f"TopicManager data-> outgoing collected {queue_name}: {to_sorted_string(data)}")
                yield data

    def _process_queue(self,end_ts, collector, observation_collector, queue):
        queue_name = queue['name']
        data_queue = queue['data']
        queue_type = queue['type']

        while data_queue:
            if data_queue[0]['data']['dateTime'] > end_ts:
                self.logger.trace(f"TopicManager leaving queue: {queue_name} size: {len(data_queue)} content: {data_queue[0]}")
                break
            payload = data_queue.popleft()
            if queue_type == 'collector':
                fieldname = payload['fieldname']
                self.logger.trace(
                    (f"TopicManager processing wind data {fieldname} {weeutil.weeutil.timestamp_to_string(payload['data']['dateTime'])}: "
                    f"{to_sorted_string(payload)}."))
                data = collector.add_data(fieldname, payload['data'])
            elif self.collect_observations:
                data = observation_collector.add_dict(payload['data'])
            else:
                data = payload['data']

            if data:
                self.logger.debug(f"TopicManager data-> outgoing {queue_name}: {to_sorted_string(data)}")
                yield data

    def get_accumulated_data(self, queue, start_time, end_time, units):
        # pylint: disable=too-many-locals
        """ Get the MQTT data after being accumulated. """
        queue_name = queue['name']
        data_queue = queue['data']
        if not bool(data_queue):
            return {}

        ignore_start_time = queue['ignore_start_time']
        ignore_end_time = queue['ignore_end_time']
        adjust_start_time = queue['adjust_start_time']
        adjust_end_time = queue['adjust_end_time']

        if ignore_start_time:
            self.logger.trace("TopicManager ignoring start time.")
            start_ts = self.peek_datetime(data_queue) - adjust_start_time
        else:
            start_ts = start_time - adjust_start_time

        if ignore_end_time:
            self.logger.trace("TopicManager ignoring end time.")
            end_ts = self.peek_last_datetime(data_queue) + adjust_end_time
        else:
            end_ts = end_time + adjust_end_time

        self.logger.trace(f"TopicManager processing interval: {start_ts:f} {end_ts:f}")
        accumulator = weewx.accum.Accum(weeutil.weeutil.TimeSpan(start_ts, end_ts))

        for data in self.get_data(queue, end_ts):
            try:
                self.logger.trace(
                    (f"TopicManager input to accumulate {queue_name} {weeutil.weeutil.timestamp_to_string(data['dateTime'])}: "
                    f"{to_sorted_string(data)}"))
                accumulator.addRecord(data)
            except weewx.accum.OutOfSpan:
                self.logger.info(
                    f"TopicManager ignoring record outside of interval {start_ts:f} {end_ts:f} {data['dateTime']:f} {to_sorted_string(data)}")

        target_data = {}
        if not accumulator.isEmpty:
            aggregate_data = accumulator.getRecord()
            self.logger.trace(
                (f"TopicManager prior to conversion is {queue_name} {weeutil.weeutil.timestamp_to_string(aggregate_data['dateTime'])}: "
                f"{to_sorted_string(aggregate_data)}"))
            target_data = weewx.units.to_std_system(aggregate_data, units)
            self.logger.trace(
                (f"TopicManager after conversion is {queue_name} {weeutil.weeutil.timestamp_to_string(target_data['dateTime'])}: "
                f"{to_sorted_string(target_data)}"))
        else:
            self.logger.trace("TopicManager accumulator was empty")

        # Force dateTime to packet's datetime so that the packet datetime is not updated to the MQTT datetime
        if ignore_end_time:
            target_data['dateTime'] = end_time

        self.logger.debug(f"TopicManager data-> outgoing accumulated {queue_name}: {to_sorted_string(target_data)}")
        return target_data

    def _queue_size_check(self, queue, max_queue):
        while len(queue) >= max_queue:
            element = queue.popleft()
            self.logger.error(f"TopicManager queue limit {int(max_queue)} reached. Removing: {element}")

    def get_fields(self, topic):
        """ Get the fields. """
        return self._get_value('fields', topic)

    def get_filters(self, topic):
        """ Get the filters. """
        return self._get_value('filters', topic)

    def get_qos(self, topic):
        """ Get the QOS. """
        return self._get_value('qos', topic)

    def get_topic_tail_is_fieldname(self, topic):
        """ Get the topic_tail_is_fieldname. """
        return self._get_value('topic_tail_is_fieldname', topic)

    def get_message_dict(self, topic):
        """ Get the type. """
        return self._get_value(self.message_config_name, topic)

    def get_unit_system(self, topic):
        """ Get the unit system """
        return self._get_value('unit_system', topic)

    def get_msg_id_field(self, topic):
        """ Get the msg_id_field value """
        return self._get_value('msg_id_field', topic)

    def get_ignore_value(self, topic):
        """ Get the ignore value """
        return self._get_value('ignore', topic)

    def get_conversion_func(self, topic):
        """ Get the ignore value """
        return self._get_value('conversion_func', topic)

    def get_(self, topic):
        """ Get the ignore value """
        return self._get_value('ignore', topic)


    def get_ignore_msg_id_field(self, topic):
        """ Get the ignore_msg_id_field value """
        return self._get_value('ignore_msg_id_field', topic)

    def _get_queue(self, topic):
        return self._get_value('queue', topic)

    def _get_value(self, value, topic):
        subscribed_topic = self._lookup_topic(topic)
        return self.subscribed_topics[subscribed_topic][value]

    def _lookup_topic(self, topic):
        if topic in self.topics:
            return self.topics[topic]

        for subscribed_topic in self.subscribed_topics:
            if mqtt.topic_matches_sub(subscribed_topic, topic):
                self.topics[topic] = subscribed_topic
                return subscribed_topic

        raise ValueError(f"Did not find topic, {topic}.")

    def _to_epoch(self, datetime_input, datetime_format, offset_format=None):
        self.logger.trace(
            f"TopicManager datetime conversion datetime_input:{datetime_input} datetime_format:{datetime_format} offset_format:{offset_format}")
        if offset_format:
            offset_start = len(datetime_input)-len(offset_format)
            offset = re.sub(r"\D", "", datetime_input[offset_start:]) #remove everything but the numbers from the UTC offset
            sign = datetime_input[offset_start-1:offset_start] # offset plus or minus
            offset_delta = datetime.timedelta(hours=int(offset[:2]), minutes=int(offset[2:]))
            if sign == '-':
                offset_delta = -offset_delta

            datetime_string = datetime_input[:offset_start-1].strip()

            self.logger.trace(f"TopicManager datetime conversion offset:{offset} sign:{sign}")

        else:
            datetime_string = datetime_input
            offset_delta = datetime.timedelta(hours=0, minutes=0)

        epoch = time.mktime((datetime.datetime.strptime(datetime_string, datetime_format) + offset_delta).timetuple())
        self.logger.trace(f"TopicManager datetime conversion datetime_string:{datetime_string} epoch:{epoch}")

        return epoch

class AbstractMessageCallbackProvider(): # pylint: disable=too-few-public-methods
    """ The abstract MessageCallbackProvider. """
    def __init__(self, logger, topic_manager):
        self.logger = logger
        self.topic_manager = topic_manager
        self.previous_values = {}

    def get_callback(self):
        """ Get the MQTT callback. """
        raise NotImplementedError("Method 'get_callback' not implemented")

    def _update_data(self, orig_name, orig_value, fields, default_field_conversion_func, unit_system):
        # pylint: disable=too-many-arguments
        value = self._convert_value(fields, default_field_conversion_func, orig_name, orig_value)
        fieldname = fields.get(orig_name, {}).get('name', orig_name)

        if orig_name in fields and 'units' in fields[orig_name]: # TODO - simplify, if possible
            (to_units, _) = weewx.units.getStandardUnitType(unit_system, fieldname)
            (value, _, _) = weewx.units.convert((value, fields[orig_name]['units'], None), to_units)

        if fields.get(orig_name, {}).get('contains_total', False):
            current_value = value
            total_wrap_around = fields.get(orig_name, {}).get('total_wrap_around', False)
            value = self._calc_increment(orig_name, current_value, self.previous_values.get(orig_name), total_wrap_around)
            self.previous_values[orig_name] = current_value

        return fieldname, value

    def _calc_increment(self, observation, current_total, previous_total, wrap_around):
        self.logger.trace(
            (f"MessageCallbackProvider _calc_increment calculating increment for {observation} with current: "
            f"{current_total:f} and previous {previous_total is None and 'None' or str(previous_total)} values."))

        if current_total is not None and previous_total is not None:
            if current_total >= previous_total:
                return current_total - previous_total

            if wrap_around and current_total < previous_total:
                self.logger.trace(
                    (f"MessageCallbackProvider _calc_increment wrap around detected for {observation} with current: "
                    f"{current_total:f} and previous {previous_total:f} values."))

                return current_total

            self.logger.trace(
                (f"MessageCallbackProvider _calc_increment skipping calculating increment for {observation} with current: "
                f"{current_total:f} and previous {previous_total:f} values."))

        return None

    @staticmethod
    def _convert_value(fields, default_field_conversion_func, field, value):
        conversion_func = fields.get(field, {}).get('conversion_func', default_field_conversion_func)
        try:
            return conversion_func['compiled'](value)
        except ValueError as exception:
            conversion_error_to_none = fields.get(field, {}).get('conversion_error_to_none', False)
            if conversion_error_to_none:
                return None
            raise ConversionError(
                f"Failed converting field {field} with value {value} using '{conversion_func['source']}' with reason {exception}.")\
                    from exception

class MessageCallbackProvider(AbstractMessageCallbackProvider):
    """ Provide the MQTT callback. """
    def __init__(self, config, logger, topic_manager):
        super().__init__(logger, topic_manager)

        for topic in topic_manager.subscribed_topics:
            if topic_manager.subscribed_topics[topic]['queue']['type'] == 'collector':
                continue

            if config is not None:
                # backwards compability
                if not topic_manager.subscribed_topics[topic][topic_manager.message_config_name]:
                    topic_manager.subscribed_topics[topic][topic_manager.message_config_name] = config.dict()
                else:
                    self.logger.info("Message configuration found under [[MessageCallback]] and [[Topic]]. Ignoring [[MessageCallback]].")

            if not topic_manager.subscribed_topics[topic][topic_manager.message_config_name]:
                raise ValueError(f"{topic} topic is missing '[[[[message]]]]' section")
            message_type = topic_manager.subscribed_topics[topic][topic_manager.message_config_name].get('type', None)
            if message_type is None:
                raise ValueError(f"{topic} topic is missing '[[[[message]]]] type=' section")
            if message_type not in ['json', 'keyword', 'individual']:
                raise ValueError(f"Invalid type configured: {message_type}")

            self._set_flatten_delimiter(topic, topic_manager)

    def _set_flatten_delimiter(self, topic, topic_manager):
        # ToDo Investigate this and copying, maybe a merge?
        if 'flatten_delimiter' not in topic_manager.subscribed_topics[topic][topic_manager.message_config_name]:
            topic_manager.subscribed_topics[topic][topic_manager.message_config_name]['flatten_delimiter'] = '_'
        if 'keyword_delimiter' not in topic_manager.subscribed_topics[topic][topic_manager.message_config_name]:
            topic_manager.subscribed_topics[topic][topic_manager.message_config_name]['keyword_delimiter'] = ','
        if 'keyword_separator' not in topic_manager.subscribed_topics[topic][topic_manager.message_config_name]:
            topic_manager.subscribed_topics[topic][topic_manager.message_config_name]['keyword_separator'] = '='

    def get_callback(self):
        """ Get the MQTT callback. """
        return self.on_message_multi

    def _flatten(self, fields, fields_ignore_default, delim, prefix, new_dict, old_dict):
        # pylint: disable=too-many-arguments
        if isinstance(old_dict, dict):
            for key, value in old_dict.items():
                new_key = prefix + key
                if isinstance(value, dict):
                    self._flatten(fields, fields_ignore_default, delim, new_key + '_', new_dict, value)
                elif isinstance(value, list):
                    self._flatten_list(fields, fields_ignore_default, delim, prefix, new_key, value, new_dict)
                else:
                    new_dict[new_key] = value
        else:
            self._flatten_list(fields, fields_ignore_default, delim, prefix, prefix[:-1], old_dict, new_dict)

    def _flatten_list(self, fields, fields_ignore_default, delim, prefix, new_key, value, new_dict):
        # pylint: disable=too-many-arguments
        if new_key in fields and 'subfields' in fields[new_key]:
            if len(value) > len(fields[new_key]['subfields']):
                self.logger.error(f"Skipping {new_key} because array data too big. Array={value} subfields={fields[new_key]['subfields']}")
            elif len(value) < len(fields[new_key]['subfields']):
                self.logger.error(f"Skipping {new_key} because array data too small. Array={value} subfields={fields[new_key]['subfields']}")
            else:
                i = 0
                for subvalue in value:
                    if isinstance(subvalue, (dict, list)):
                        self._flatten(fields, fields_ignore_default, delim, prefix + fields[new_key]['subfields'][i] + '_', new_dict, subvalue)
                    else:
                        new_dict[prefix + fields[new_key]['subfields'][i]] = subvalue
                    i += 1
        else:
            #if not fields.get(lookup_key, {}).get('ignore', fields_ignore_default):
            self.logger.error(f"Skipping {new_key} because data is an array and has no configured subfields. Array={value}")

    def _log_message(self, msg):
        self.logger.debug(
            f"MessageCallbackProvider data-> incoming topic: {msg.topic}, QOS: {int(msg.qos)}, retain: {msg.retain}, payload: {msg.payload}")

    def _log_exception(self, method, exception, msg):
        self.logger.error(f"MessageCallbackProvider {method} failed with {type(exception)} and reason {exception}.")
        self.logger.error(f"**** MessageCallbackProvider Ignoring topic={msg.topic} and payload={msg.payload}")
        self.logger.error(f"**** MessageCallbackProvider {traceback.format_exc()}")

    def _on_message_keyword(self, _client, _userdata, msg):
        # pylint: disable= too-many-locals
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self._log_message(msg)
            message_dict = self.topic_manager.get_message_dict(msg.topic)
            fields = self.topic_manager.get_fields(msg.topic)
            fields_ignore_default = self.topic_manager.get_ignore_value(msg.topic)
            fields_conversion_func = self.topic_manager.get_conversion_func(msg.topic)

            payload_str = msg.payload.decode('utf-8')

            fielddata = payload_str.split(message_dict['keyword_delimiter'])
            data = {}
            unit_system = self.topic_manager.get_unit_system(msg.topic)
            for field in fielddata:
                eq_index = field.find(message_dict['keyword_separator'])
                # Ignore all fields that do not have the separator
                if eq_index == -1:
                    self.logger.error(
                        f"MessageCallbackProvider on_message_keyword failed to find separator: {message_dict['keyword_separator']}")
                    self.logger.error(f"**** MessageCallbackProvider Skipping field={field} ")
                    continue

                key = field[:eq_index].strip()
                if not fields.get(key, {}).get('ignore', fields_ignore_default):
                    (fieldname, value) = self._update_data(key, field[eq_index + 1:].strip(), fields, fields_conversion_func, unit_system)
                    data[fieldname] = value
                else:
                    self.logger.trace(f"MessageCallbackProvider on_message_keyword ignoring field: {key}")

            if data:
                self.topic_manager.append_data(msg.topic, data)
            else:
                self.logger.error(
                    f"MessageCallbackProvider on_message_keyword failed to find data in: topic={msg.topic} and payload={msg.payload}")

        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_keyword', exception, msg)

    def _on_message_json(self, _client, _userdata, msg):
        # pylint: disable=too-many-branches
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self._log_message(msg)
            message_dict = self.topic_manager.get_message_dict(msg.topic)
            fields = self.topic_manager.get_fields(msg.topic)
            fields_ignore_default = self.topic_manager.get_ignore_value(msg.topic)

            payload_str = msg.payload.decode('utf-8')

            data_flattened = {}
            self._flatten(fields, fields_ignore_default, message_dict['flatten_delimiter'], '', data_flattened, json.loads(payload_str))

            data_final = self._process_json_dict(msg, fields, fields_ignore_default, data_flattened)

            if data_final:
                self.topic_manager.append_data(msg.topic, data_final)

        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_json', exception, msg)

    def _process_json_dict(self, msg, fields, fields_ignore_default, data_flattened):
        # pylint: disable= too-many-locals
        msg_id_field = self.topic_manager.get_msg_id_field(msg.topic)
        ignore_msg_id_field = self.topic_manager.get_ignore_msg_id_field(msg.topic)
        unit_system = self.topic_manager.get_unit_system(msg.topic)
        filters = self.topic_manager.get_filters(msg.topic)
        fields_conversion_func = self.topic_manager.get_conversion_func(msg.topic)

        data_final = {}
        if msg_id_field:
            msg_id = data_flattened[msg_id_field]

        for key, value in data_flattened.items():
            if msg_id_field and key not in ignore_msg_id_field:
                lookup_key = key + "_" + str(msg_id) # todo - cleanup
            else:
                lookup_key = key
            if lookup_key in filters and value in filters[lookup_key]:
                self.logger.info(
                    (f"MessageCallbackProvider on_message_json filtered out {msg.topic} : "
                    f"{msg.payload} with {lookup_key}={filters[lookup_key]}"))
                return None
            if not fields.get(lookup_key, {}).get('ignore', fields_ignore_default):
                (fieldname, value) = self._update_data(lookup_key, value, fields, fields_conversion_func, unit_system)
                data_final[fieldname] = value
            else:
                self.logger.trace(f"MessageCallbackProvider on_message_json ignoring field: {lookup_key}")

        return data_final

    def _on_message_individual(self, _client, _userdata, msg):

        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self._log_message(msg)
            fields = self.topic_manager.get_fields(msg.topic)
            fields_ignore_default = self.topic_manager.get_ignore_value(msg.topic)
            fields_conversion_func = self.topic_manager.get_conversion_func(msg.topic)
            topic_tail_is_fieldname = self.topic_manager.get_topic_tail_is_fieldname(msg.topic)

            payload_str = msg.payload

            key = msg.topic
            if topic_tail_is_fieldname:
                key = key.rpartition('/')[2]

            if msg.payload is not None:
                payload_str = msg.payload.decode('utf-8')

            unit_system = self.topic_manager.get_unit_system(msg.topic)
            if not fields.get(key, {}).get('ignore', fields_ignore_default):
                (fieldname, value) = self._update_data(key, payload_str, fields, fields_conversion_func, unit_system)
                data = {}
                data[fieldname] = value
                self.topic_manager.append_data(msg.topic, data, fieldname)
            else:
                self.logger.trace(f"MessageCallbackProvider on_message_individual ignoring field: {key}")

        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_individual', exception, msg)

    def on_message_multi(self, client, userdata, msg):
        ''' The on message call back.'''
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            message_dict = self.topic_manager.get_message_dict(msg.topic)
            message_type = message_dict['type']
            # ToDo: eliminate if/elif?
            if message_type == 'individual':
                self._on_message_individual(client, userdata, msg)
            elif message_type == 'json':
                self._on_message_json(client, userdata, msg)
            elif message_type == 'keyword':
                self._on_message_keyword(client, userdata, msg)
            else:
                self.logger.error(f"Unknown message_type={message_type}. Skipping topic={msg.topic} and payload={msg.payload}")
        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_multi', exception, msg)

class ManageWeewxConfig():
    ''' Manage the WeeWX configuration. '''
    def _add_unit_group(self, unit_config, unit):
        group = unit_config.get('group')
        if not group:
            raise ValueError(f"{unit} is missing a group.")

        unit_systems = weeutil.weeutil.option_as_list(unit_config.get('unit_system'))
        if not unit_systems:
            raise ValueError(f"{unit} is missing an unit_system.")

        for unit_system in unit_systems:
            if unit_system == 'us':
                weewx.units.USUnits.extend({group: unit})
            elif unit_system == 'metric':
                weewx.units.MetricUnits.extend({group: unit})
            elif unit_system == 'metricwx':
                weewx.units.MetricWXUnits.extend({group: unit})
            else:
                raise ValueError(f"Invalid unit_system {unit_system} for {unit}.")

    def _update_format_config(self, unit_config, unit):
        format_config = unit_config.get('format')
        if format_config:
            weewx.units.default_unit_format_dict[unit] = format_config

    def _update_label_dict(self, unit_config, unit):
        label = unit_config.get('label')
        if label:
            weewx.units.default_unit_label_dict[unit] = label

    def _update_conversion_dict(self, unit_config, unit):
        conversion = unit_config.get('conversion')
        if conversion:
            for to_unit in conversion:
                if unit not in weewx.units.conversionDict:
                    weewx.units.conversionDict[unit] = {}

                weewx.units.conversionDict[unit][to_unit] = eval(conversion[to_unit]) # pylint: disable=eval-used

    def update_unit_config(self, weewx_config):
        ''' Update the unit sections of the WeeWX configuration.'''
        units = weewx_config.get('units')
        if units:
            for unit in units.sections:
                unit_config = units.get(unit)

                self._add_unit_group(unit_config, unit)
                self._update_format_config(unit_config, unit)
                self._update_label_dict(unit_config, unit)
                self._update_conversion_dict(unit_config, unit)

    def add_observation_to_unit_dict(self, weewx_config):
        ''' Add the observations to WeeWX's unit dictionart. '''
        observations = weewx_config.get('observations')
        if observations:
            for observation in observations.keys():
                weewx.units.obs_group_dict.extend({observation: observations[observation]})

class MQTTSubscriber():
    """ Manage MQTT sunscriptions. """
    def __init__(self, service_dict, logger):
        self.logger = logger

        exclude_keys = ['password']
        sanitized_service_dict = {k: service_dict[k] for k in set(list(service_dict.keys())) - set(exclude_keys)}
        self.logger.debug(f"sanitized configuration removed {exclude_keys}")
        self.logger.debug(f"MQTTSUBscriber sanitized_service_dict is {sanitized_service_dict}")

        message_callback_config = service_dict.get('message_callback', None)

        topics_dict = service_dict.get('topics', None)
        if topics_dict is None:
            raise ValueError("[[topics]] is required.")

        self.archive_topic = service_dict.get('archive_topic', None)
        if self.archive_topic and self.archive_topic not in service_dict['topics']:
            raise ValueError(f"Archive topic {self.archive_topic} must be in [[topics]]")

        self._check_deprecated_options(service_dict)

        message_callback_provider_name = service_dict.get('message_callback_provider',
                                                          'user.MQTTSubscribe.MessageCallbackProvider')
        self.manager = TopicManager(self.archive_topic, topics_dict, self.logger)

        self.cached_fields = None
        self.cached_fields = self.manager.cached_fields

        weewx_config = service_dict.get('weewx')
        if weewx_config:
            manage_weewx_config = ManageWeewxConfig()
            manage_weewx_config.update_unit_config(weewx_config)
            manage_weewx_config.add_observation_to_unit_dict(weewx_config)

        mqtt_options = {
            'clientid': service_dict.get('clientid', 'MQTTSubscribe-' + str(random.randint(1000, 9999))),
            'clean_session': to_bool(service_dict.get('clean_session', True)),
            'host': service_dict.get('host', 'localhost'),
            'keepalive': to_int(service_dict.get('keepalive', 60)),
            'port': to_int(service_dict.get('port', 1883)),
            'username': service_dict.get('username', None),
            'password': service_dict.get('password', None),
            'min_delay': to_int(service_dict.get('min_delay', 1)),
            'max_delay': to_int(service_dict.get('max_delay', 120)),
            'log_mqtt': to_bool(service_dict.get('log', False)),
            'tls_dict': service_dict.get('tls'),
        }

        self.logger.info(f"message_callback_provider_name is {message_callback_provider_name}")
        self.logger.info(f"clientid is {mqtt_options['clientid']}")
        self.logger.info(f"client_session is {mqtt_options['clean_session']}")
        self.logger.info(f"host is {mqtt_options['host']}")
        self.logger.info(f"port is {mqtt_options['port']}")
        self.logger.info(f"keepalive is {mqtt_options['keepalive']}")
        self.logger.info(f"username is {mqtt_options['username']}")
        self.logger.info(f"min_delay is {mqtt_options['min_delay']}")
        self.logger.info(f"max_delay is {mqtt_options['max_delay']}")
        if mqtt_options['password'] is not None:
            self.logger.info("password is set")
        else:
            self.logger.info("password is not set")
        self.logger.info(f"Archive topic is {self.archive_topic}")

        self._setup_mqtt(mqtt_options, message_callback_provider_name, message_callback_config)

    def _setup_mqtt(self, mqtt_options, message_callback_provider_name, message_callback_config):
        self.mqtt_logger = {
            mqtt.MQTT_LOG_INFO: self.logger.info,
            mqtt.MQTT_LOG_NOTICE: self.logger.info,
            mqtt.MQTT_LOG_WARNING: self.logger.info,
            mqtt.MQTT_LOG_ERR: self.logger.error,
            mqtt.MQTT_LOG_DEBUG: self.logger.debug
        }

        self.userdata = {}
        self.userdata['connect'] = False
        self.userdata['connect_rc'] = None
        self.userdata['connect_flags'] = 0
        self.client = mqtt.Client(client_id=mqtt_options['clientid'], userdata=self.userdata, clean_session=mqtt_options['clean_session'])

        if mqtt_options['tls_dict'] and to_bool(mqtt_options['tls_dict'].get('enable', True)):
            self.config_tls(mqtt_options['tls_dict'])

        if mqtt_options['log_mqtt']:
            self.client.on_log = self._on_log

        message_callback_provider_class = weeutil.weeutil.get_object(message_callback_provider_name)
        message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                    self.logger,
                                                                    self.manager)

        self.client.on_message = message_callback_provider.get_callback()

        self.client.on_subscribe = self._on_subscribe

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        if mqtt_options['username'] is not None and mqtt_options['password'] is not None:
            self.client.username_pw_set(mqtt_options['username'], mqtt_options['password'])

        self.client.reconnect_delay_set(min_delay=mqtt_options['min_delay'], max_delay=mqtt_options['max_delay'])

        try:
            self.client.connect(mqtt_options['host'], mqtt_options['port'], mqtt_options['keepalive'])
        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self.logger.error(f"Failed to connect to {mqtt_options['host']} at {int(mqtt_options['port'])}. '{exception}'")
            raise weewx.WeeWxIOError(exception)

    def _check_deprecated_options(self, service_dict):
        if 'topic' in service_dict:
            raise ValueError("'topic' is deprecated, use '[[topics]][[[topic name]]]'")
        if 'overlap' in service_dict:
            raise ValueError("'overlap' is deprecated, use 'adjust_start_time'")
        if 'archive_field_cache' in service_dict:
            raise ValueError("'archive_field_cache' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]'")
        if 'message_callback' in service_dict:
            if 'full_topic_fieldname' in service_dict['message_callback']:
                raise ValueError("'full_topic_fieldname' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]'")
            if 'contains_total' in service_dict['message_callback']:
                raise ValueError("'contains_total' is deprecated use '[[topics]][[[topic name]]][[[[field name]]]]' contains_total setting.")
            if 'label_map' in service_dict['message_callback']:
                raise ValueError("'label_map' is deprecated use '[[topics]][[[topic name]]][[[[field name]]]]' name setting.")
            if 'fields' in service_dict['message_callback']:
                raise ValueError("'fields' is deprecated, use '[[topics]][[[topic name]]][[[[field name]]]]'")
            if 'use_topic_as_fieldname' in service_dict['topics']:
                self.logger.info("'use_topic_as_fieldname' option is no longer needed and can be removed.")

    @property
    def queues(self):
        """ The queues of observations. """
        return self.manager.queues # pragma: no cover

    def config_tls(self, tls_dict):
        """ Configure TLS."""
        valid_cert_reqs = {
            'none': ssl.CERT_NONE,
            'optional': ssl.CERT_OPTIONAL,
            'required': ssl.CERT_REQUIRED
        }

        # Some versions are dependent on the OpenSSL install
        valid_tls_versions = {}
        try:
            valid_tls_versions['tls'] = ssl.PROTOCOL_TLS
        except AttributeError:
            pass
        try:
            valid_tls_versions['tlsv1'] = ssl.PROTOCOL_TLSv1
        except AttributeError:
            pass
        try:
            valid_tls_versions['tlsv11'] = ssl.PROTOCOL_TLSv1_1
        except AttributeError:
            pass
        try:
            valid_tls_versions['tlsv12'] = ssl.PROTOCOL_TLSv1_2
        except AttributeError:
            pass
        try:
            valid_tls_versions['sslv2'] = ssl.PROTOCOL_SSLv2
        except AttributeError:
            pass
        try:
            valid_tls_versions['sslv23'] = ssl.PROTOCOL_SSLv23
        except AttributeError:
            pass
        try:
            valid_tls_versions['sslv3'] = ssl.PROTOCOL_SSLv3
        except AttributeError:
            pass

        ca_certs = tls_dict.get('ca_certs')

        valid_cert_reqs = valid_cert_reqs.get(tls_dict.get('certs_required', 'required'))
        if valid_cert_reqs is None:
            raise ValueError(f"Invalid 'certs_required'., {tls_dict['certs_required']}")

        tls_version = valid_tls_versions.get(tls_dict.get('tls_version', 'tlsv12'))
        if tls_version is None:
            raise ValueError(f"Invalid 'tls_version'., {tls_dict['tls_version']}")

        self.client.tls_set(ca_certs=ca_certs,
                            certfile=tls_dict.get('certfile'),
                            keyfile=tls_dict.get('keyfile'),
                            cert_reqs=valid_cert_reqs,
                            tls_version=tls_version,
                            ciphers=tls_dict.get('ciphers'))

    def get_data(self, queue, end_ts=sys.maxsize):
        """ Get data off the queue of MQTT data. """
        return self.manager.get_data(queue, end_ts) # pragma: no cover

    def get_accumulated_data(self, queue, start_ts, end_ts, units):
        """ Get the MQTT data after being accumulated. """
        return self.manager.get_accumulated_data(queue, start_ts, end_ts, units) # pragma: no cover

    def start(self):
        """ start subscribing to the topics """
        self.logger.debug("Starting loop")
        self.client.loop_start()

        self.logger.info("Waiting for MQTT connection.")
        while not self.userdata['connect']:
            time.sleep(1)

        if self.userdata['connect_rc'] > 0:
            raise weewx.WeeWxIOError(
                (f"Unable to connect. Return code is {int(self.userdata['connect_rc'])}, '{connack_string(self.userdata['connect_rc'])}', "
                f"flags are {self.userdata['connect_flags']}."))

        self.logger.info("MQTT initialization complete.")

    def disconnect(self):
        """ shut it down """
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        # https://pypi.org/project/paho-mqtt/#on-connect
        # rc:
        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorised
        # 6-255: Currently unused.
        self.logger.info(f"Connected with result code {int(rc)}")
        self.logger.info(f"Connected flags {str(flags)}")

        userdata['connect'] = True
        userdata['connect_rc'] = rc
        userdata['connect_flags'] = flags

        for topic, info in self.manager.subscribed_topics.items():
            if not info['subscribe']:
                continue

            (result, mid) = client.subscribe(topic, self.manager.get_qos(topic))
            self.logger.info(f"Subscribing to {topic} has a mid {int(mid)} and rc {int(result)}")

    def _on_disconnect(self, _client, _userdata, rc):
        self.logger.info(f"Disconnected with result code {int(rc)}")

    def _on_subscribe(self, _client, _userdata, mid, granted_qos):
        self.logger.info(f"Subscribed to mid: {int(mid)} is size {len(granted_qos)} has a QOS of {int(granted_qos[0])}")

    def _on_log(self, _client, _userdata, level, msg):
        self.mqtt_logger[level](f"MQTTSubscribe MQTT: {msg}")

class MQTTSubscribeService(StdService):
    """ The MQTT subscribe service. """
    def __init__(self, engine, config_dict):
        super().__init__(engine, config_dict)

        self.subscriber = None
        service_dict = config_dict.get('MQTTSubscribeService', {})
        logging_filename = service_dict.get('logging_filename', None)
        logging_level = service_dict.get('logging_level', 'NOTSET')
        console = to_bool(service_dict.get('console', False))
        self.logger = Logger('Service', level=logging_level, filename=logging_filename, console=console)
        self.logger.log_environment(config_dict)

        self.enable = to_bool(service_dict.get('enable', True))
        if not self.enable:
            self.logger.info("Not enabled, exiting.")
            return

        if engine.stn_info.hardware == DRIVER_NAME:
            self.logger.info("Running as both a driver and a service.")

        self.binding = service_dict.get('binding', 'loop')

        if 'archive_topic' in service_dict:
            raise ValueError(f"archive_topic, {service_dict['archive_topic']}, is invalid when running as a service")

        self.end_ts = 0 # prime for processing loop packet

        self.subscriber = MQTTSubscriber(service_dict, self.logger)

        self.logger.info(f"binding is {self.binding}")

        self.subscriber.start()

        self.cache = RecordCache()
        archive_dict = config_dict.get('StdArchive', {})
        record_generation = archive_dict.get('record_generation', "none").lower()

        if self.binding not in ('loop', 'archive'):
            raise ValueError(f"MQTTSubscribeService: Unknown binding: {self.binding}")

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

        if self.binding == 'loop':
            self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)

        if self.subscriber.cached_fields and record_generation != 'software' and self.binding == 'loop':
            raise ValueError(f"caching is not available with record generation of type '{record_generation}' and and binding of type 'loop'")

    def shutDown(self): # need to override parent - pylint: disable=invalid-name
        """Run when an engine shutdown is requested."""
        if self.subscriber:
            self.subscriber.disconnect()

    def new_loop_packet(self, event):
        """ Handle the new loop packet event. """
        # packet has traveled back in time
        if self.end_ts > event.packet['dateTime']:
            self.logger.error(f"Ignoring packet has dateTime of {event.packet['dateTime']:f} which is prior to previous packet {self.end_ts:f}")
        else:
            start_ts = self.end_ts
            self.end_ts = event.packet['dateTime']

            for queue in self.subscriber.queues: # topics might not be cached.. therefore use subscribed?
                self.logger.trace(
                    (f"Packet prior to update is: "
                    f"{weeutil.weeutil.timestamp_to_string(event.packet['dateTime'])} {to_sorted_string(event.packet)}"))
                target_data = self.subscriber.get_accumulated_data(queue,
                                                                   start_ts, self.end_ts, event.packet['usUnits'])
                self.logger.trace(f"Queue {queue['name']} has data: {target_data}")
                event.packet.update(target_data)
                self.logger.trace(
                    f"Packet after update is: {weeutil.weeutil.timestamp_to_string(event.packet['dateTime'])} {to_sorted_string(event.packet)}")

            self.logger.debug(
                f"data-> final packet is {weeutil.weeutil.timestamp_to_string(event.packet['dateTime'])}: {to_sorted_string(event.packet)}")

    # this works for hardware generation, but software generation does not 'quality control'
    # the archive record, so this data is not 'QC' in this case.
    # If this is important, bind to the loop packet.
    def new_archive_record(self, event):
        """ Handle the new archive record event. """
        self.logger.debug(
            f"data-> incoming record is {weeutil.weeutil.timestamp_to_string(event.record['dateTime'])}: {to_sorted_string(event.record)}")
        if self.binding == 'archive':
            end_ts = event.record['dateTime']
            start_ts = end_ts - event.record['interval'] * 60

            for queue in self.subscriber.queues:
                self.logger.trace(
                    (f"Record prior to update is: "
                    f"{weeutil.weeutil.timestamp_to_string(event.record['dateTime'])} {to_sorted_string(event.record)}"))
                target_data = self.subscriber.get_accumulated_data(queue, start_ts, end_ts, event.record['usUnits'])
                self.logger.trace(f"Queue {queue['name']} has data: {target_data}")
                event.record.update(target_data)
                self.logger.trace(
                    f"Record after update is: {weeutil.weeutil.timestamp_to_string(event.record['dateTime'])} {to_sorted_string(event.record)}")

        if self.subscriber.cached_fields:
            target_data = {}
            for field in self.subscriber.cached_fields:
                if field in event.record:
                    timestamp = time.time()
                    self.logger.trace(
                        (f"Update cache {event.record[field]} "
                        f"to {field} with units of {int(event.record['usUnits'])} and timestamp of {int(timestamp)}"))
                    self.cache.update_value(field,
                                            event.record[field],
                                            event.record['usUnits'],
                                            timestamp)
                else:
                    target_data[field] = self.cache.get_value(field,
                                                            time.time(),
                                                            self.subscriber.cached_fields[field]['expires_after'])
                    self.logger.trace(f"target_data after cache lookup is: {to_sorted_string(target_data)}")

            event.record.update(target_data)

        self.logger.debug(
            f"data-> final record is {weeutil.weeutil.timestamp_to_string(event.record['dateTime'])}: {to_sorted_string(event.record)}")

def loader(config_dict, engine):
    """ Load and return the driver. """
    return MQTTSubscribeDriver(config_dict, engine) # pragma: no cover

def confeditor_loader():
    """ Load and return the configuration editor. """
    return MQTTSubscribeDriverConfEditor() # pragma: no cover

class MQTTSubscribeDriver(weewx.drivers.AbstractDevice):
    # (methods not used) pylint: disable=abstract-method
    # pylint: disable=too-many-instance-attributes
    """weewx driver that reads data from MQTT"""
    def __init__(self, config_dict, engine):
        stn_dict = config_dict[DRIVER_NAME]
        console = to_bool(stn_dict.get('console', False))
        logging_filename = stn_dict.get('logging_filename', None)
        logging_level = stn_dict.get('logging_level', 'NOTSET').upper()
        self.logger = Logger('Driver', level=logging_level, filename=logging_filename, console=console)
        self.logger.log_environment(config_dict)

        self.max_loop_interval = to_int(stn_dict.get('max_loop_interval', 0))
        self.logger.info(f"Max loop interval is: {int(self.max_loop_interval)}")
        self.last_loop_packet_ts = 0
        self.start_loop_period_ts = 0

        self.wait_before_retry = float(stn_dict.get('wait_before_retry', 2))
        self._archive_interval = to_int(stn_dict.get('archive_interval', 300))
        self.archive_topic = stn_dict.get('archive_topic', None)
        self.prev_archive_start = 0

        engine.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

        self.subscriber = MQTTSubscriber(stn_dict, self.logger)

        self.queue = next((q for q in self.subscriber.queues if q['name'] == self.archive_topic), None)

        self.logger.info(f"Wait before retry is {int(self.wait_before_retry)}")
        self.subscriber.start()

    @property
    def hardware_name(self):
        """ The name of the hardware driver. """
        return "MQTTSubscribeDriver" # pragma: no cover

    @property
    def archive_interval(self):
        """ The archive interval. """
        if not self.archive_topic:
            self.logger.debug("No archive topic configured.")
            raise NotImplementedError

        return self._archive_interval

    def closePort(self): # need to override parent - pylint: disable=invalid-name
        """ Called to perform any close/cleanup before termination. """
        self.subscriber.disconnect()

    def new_archive_record(self, event):
        """ Handle the new archive record event. """
        self.logger.debug(
            f"data-> final record is {weeutil.weeutil.timestamp_to_string(event.record['dateTime'])}: {to_sorted_string(event.record)}")

    def genLoopPackets(self): # need to override parent - pylint: disable=invalid-name
        """ Called to generate loop packets. """
        while True:
            packet_count = 0
            for data in self._process_queues():
                packet_count += 1
                yield data

            if packet_count == 0:
                data = self._handle_empty_queue()
                if data:
                    yield data

    def _process_queues(self):
        for queue in self.subscriber.queues:
            if queue['name'] == self.archive_topic:
                continue

            for data in self.subscriber.get_data(queue):
                if data:
                    archive_start = weeutil.weeutil.startOfInterval(data['dateTime'], self._archive_interval)
                    if archive_start < self.prev_archive_start:
                        self.logger.error(
                            (f"Ignoring record because {archive_start} archival start "
                            f"is before previous archive start {self.prev_archive_start}: "
                            f"{to_sorted_string(data)}"))
                    else:
                        self.last_loop_packet_ts = data['dateTime']
                        self.prev_archive_start = archive_start
                        self.logger.debug(
                            (f"data-> final loop packet is {queue['name']} {weeutil.weeutil.timestamp_to_string(data['dateTime'])}: "
                            f"{to_sorted_string(data)}"))
                        yield data

    def _handle_empty_queue(self):
        self.logger.trace("Queues are empty.")
        if self.max_loop_interval:
            now = int(time.time() + 0.5)
            start_loop_period_ts = weeutil.weeutil.startOfInterval(now, self.max_loop_interval)
            if start_loop_period_ts != self.start_loop_period_ts:
                if self.last_loop_packet_ts < self.start_loop_period_ts:
                    data = {}
                    data['dateTime'] = self.start_loop_period_ts
                    data['MQTTSubscribe'] = None # WeeWX accumulator requires at least one observation
                    data['usUnits'] = 1
                    self.last_loop_packet_ts = data['dateTime']
                    self.logger.trace(
                        f"Creating empty loop packet {weeutil.weeutil.timestamp_to_string(data['dateTime'])}: {to_sorted_string(data)}")
                    return data

                self.start_loop_period_ts = start_loop_period_ts

        time.sleep(self.wait_before_retry)
        return None

    def genArchiveRecords(self, lastgood_ts): # need to override parent - pylint: disable=invalid-name
        """ Called to generate the archive records. """
        if not self.archive_topic:
            self.logger.debug("No archive topic configured.")
            raise NotImplementedError

        for data in self.subscriber.get_data(self.queue):
            if data:
                self.logger.debug(
                    (f"data-> final archive record is {self.archive_topic} {weeutil.weeutil.timestamp_to_string(data['dateTime'])}: "
                    f"{to_sorted_string(data)}"))
                if lastgood_ts is None  or data['dateTime'] > lastgood_ts:
                    yield data
            else:
                break

class MQTTSubscribeDriverConfEditor(weewx.drivers.AbstractConfEditor): # pragma: no cover
    """ Methods for producing and updating configuration stanzas for use in configuration file. """
    def __init__(self):
        self.mqttsubscribe_configuration = MQTTSubscribeConfiguration('MQTTSubscribeDriver')
        self.existing_options = {}
        super().__init__()

    @property
    def default_stanza(self):
        """ The default configuration stanza. """
        mqttsubscribe_configuration = MQTTSubscribeConfiguration('MQTTSubscribeDriver')
        return mqttsubscribe_configuration.default_stanza

    def prompt_for_settings(self):
        """ Prompt for settings required for proper operation of this driver. """
        default_config = self.mqttsubscribe_configuration.default_config

        settings = {}
        self._configure(default_config['MQTTSubscribeDriver'], settings)

        if len(self.existing_options['topics']) > 1:
            print("Topics have been configured, currently these cannot be changed interactively.")
        else:
            settings['topics'] = {}
            topic = 'REPLACE_ME'
            while topic:
                print("Enter a topic to subscribe to. Leave blank when done.")
                topic = self._prompt('topic')
                if topic:
                    settings['topics'][topic] = {}
                    settings['topics'][topic]['message'] = {}
                    print("Enter the MQTT paylod type: individual|json|keyword")
                    settings['topics'][topic]['message']['type'] = self._prompt('type', 'json', ['individual', 'json', 'keyword'])
                else:
                    if len(settings['topics']) == 1:
                        topic = 'REPLACE_ME'

        return settings

    def _configure(self, section, settings):
        for key, _ in section.items():
            if key not in section.sections:
                for comment in section.comments[key]:
                    print(comment.replace('#', '', 1).lstrip())
                settings[key] = self._prompt(key, section[key])

        for key in section.sections:
            if key == 'topics':
                continue

            settings[key] = {}
            print("")
            print(f"Configuring section '{key}'")
            print("")
            self._configure(section[key], settings[key])

class MQTTSubscribeConfiguration():
    """ Manage the MQTTSubscribe configuration. """
    def __init__(self, section=None):
        self.section = section

    @property
    def default_config(self):
        """ The default configuration. """

        example_intial_comment = f'''#
# This is an example configuration for MQTTSubscribe
# It was created on {datetime.date.today()} at {datetime.datetime.now().strftime("%H:%M:%S")}
#

'''

        config_spec = configobj.ConfigObj(CONFIG_SPEC_TEXT.splitlines())


        remove_items = {
            'archive_interval': ['MQTTSubscribe'],
            'archive_topic': ['MQTTSubscribe'],
            'clean_session': ['MQTTSubscribe'],
            'clientid': ['MQTTSubscribe'],
            'keepalive': ['MQTTSubscribe'],
            'logging_filename': ['MQTTSubscribe'],
            'message_callback': ['MQTTSubscribe'],
            'max_delay': ['MQTTSubscribe'],
            'max_loop_interval': ['MQTTSubscribe'],
            'min_delay': ['MQTTSubscribe'],
            'wait_before_retry': ['MQTTSubscribe'],
            'adjust_end_time': ['MQTTSubscribe', 'topics'],
            'adjust_start_time': ['MQTTSubscribe', 'topics'],
            'callback_config_name': ['MQTTSubscribe', 'topics'],
            'collect_observations': ['MQTTSubscribe', 'topics'],
            'collect_wind_across_loops': ['MQTTSubscribe', 'topics'],
            'datetime_format': ['MQTTSubscribe', 'topics'],
            'ignore_end_time': ['MQTTSubscribe', 'topics'],
            'ignore_start_time': ['MQTTSubscribe', 'topics'],
            'max_queue': ['MQTTSubscribe', 'topics'],
            'message': ['MQTTSubscribe', 'topics'],
            'offset_format': ['MQTTSubscribe', 'topics'],
            'single_queue': ['MQTTSubscribe', 'topics'],
            'subscribe': ['MQTTSubscribe', 'topics'],
            'topic_tail_is_fieldname': ['MQTTSubscribe', 'topics'],
            'use_server_datetime': ['MQTTSubscribe', 'topics'],
            'use_topic_as_fieldname': ['MQTTSubscribe', 'topics'],
            'msg_id_field': ['MQTTSubscribe', 'topics', 'REPLACE_ME'],
            'qos': ['MQTTSubscribe', 'topics', 'REPLACE_ME'],
            'flatten_delimiter': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'message'],
            'keyword_delimiter': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'message'],
            'keyword_separator': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'message'],
            'conversion_error_to_none': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'REPLACE_ME'],
            'conversion_func': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'REPLACE_ME'],
            'conversion_type': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'REPLACE_ME'],
            'expires_after': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'REPLACE_ME'],
            'ignore_msg_id_field': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'REPLACE_ME'],
            'subfields': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'REPLACE_ME'],
            'total_wrap_around': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'REPLACE_ME'],
            'units': ['MQTTSubscribe', 'topics', 'REPLACE_ME', 'REPLACE_ME'],
        }

        if self.section and self.section != 'MQTTSubscribeDriver':
            del config_spec['MQTTSubscribe']['driver']

        if self.section and self.section != 'MQTTSubscribeService':
            del config_spec['MQTTSubscribe']['enable']

        for remove_item, _ in remove_items.items():
            current_section = config_spec
            for key in remove_items[remove_item]:
                if key in current_section:
                    current_section = current_section[key]
                else:
                    current_section = {}
                    break

            if remove_item in current_section:
                del current_section[remove_item]
            else:
                raise ValueError(f"Trying to remove {remove_item} and it is not in the config spec.")

        if self.section:
            config_spec.rename('MQTTSubscribe', self.section)

        config_spec.initial_comment = example_intial_comment.splitlines()
        if not self.section:
            config_spec.initial_comment.append("# Replace '[MQTTSubscribe]' with '[MQTTSubscribeService]' or '[MQTTSubscribeDriver]'")
        config_spec.initial_comment.append("# For additional information see, https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Configuring#the-mqttsubscribedrivermqttsubscribesection-section")

        return config_spec

    @property
    def default_stanza(self):
        """ The default configuration stanza. """
        return '\n'.join(self.default_config.write())

class Simulator():
    """ Run the service or driver. """
    # pylint: disable=too-many-instance-attributes

    usage = """
            [--conf=CONFIG]
            [--records=RECORD_COUNT]
            [--interval=INTERVAL]
            [--delay=DELAY]
            [--units=US|METRIC|METRICWX]
            [--binding=archive|loop]
            [--verbose]
            [--console]

    CONFIG = The WeeWX configuration file, typically weewx.conf.
    """

    @classmethod
    def add_parsers(cls, parser):
        ''' Add the parsers. '''
        cls.simulator_parser = parser.add_parser('simulate')
        simulator_subparsers = cls.simulator_parser.add_subparsers(dest='type')

        simulate_service_parser = simulator_subparsers.add_parser('service', usage=f"MQTTSubscribe.py simulate service {cls.usage}")
        simulate_service_parser.add_argument("--conf", required=False,
                            help="The WeeWX configuration file. Typically weewx.conf.")
        simulate_service_parser.add_argument('--records', dest='record_count', type=int,
                            help='The number of archive records to create.',
                            default=2)
        simulate_service_parser.add_argument('--interval', dest='interval', type=int,
                            help='The archive interval in seconds.',
                            default=300)
        simulate_service_parser.add_argument('--delay', dest='delay', type=int,
                            help='The archive delay in seconds.',
                            default=15)
        simulate_service_parser.add_argument("--units", choices=["US", "METRIC", "METRICWX"],
                            help="The default units if not in MQTT payload.",
                            default="US")
        simulate_service_parser.add_argument("--binding", choices=["archive", "loop"],
                            help="The type of binding.",
                            default="archive")
        simulate_service_parser.add_argument("--verbose", action="store_true", dest="verbose",
                            help="Log extra output (debug=1).")
        simulate_service_parser.add_argument("--console", action="store_true", dest="console",
                            help="Log to console in addition to syslog.")
        simulate_service_parser.add_argument("--host",
                            help="The MQTT server.")
        simulate_service_parser.add_argument("--topics",
                            help="Comma separated list of topics to subscribe to.")
        simulate_service_parser.add_argument("--callback",
                            help="The callback type.")

        simulate_driver_parser = simulator_subparsers.add_parser('driver', usage=f"MQTTSubscribe.py simulate driver {cls.usage}")
        simulate_driver_parser.add_argument("--conf", required=False,
                            help="The WeeWX configuration file. Typicall weewx.conf.")
        simulate_driver_parser.add_argument('--records', dest='record_count', type=int,
                            help='The number of archive records to create.',
                            default=10)
        simulate_driver_parser.add_argument('--interval', dest='interval', type=int,
                            help='The archive interval in seconds.',
                            default=300)
        simulate_driver_parser.add_argument('--delay', dest='delay', type=int,
                            help='The archive delay in seconds.',
                            default=15)
        simulate_driver_parser.add_argument("--units", choices=["US", "METRIC", "METRICWX"],
                            help="The default units if not in MQTT payload.",
                            default="US")
        simulate_driver_parser.add_argument("--binding", choices=["archive", "loop"],
                            help="The type of binding.",
                            default="loop")
        simulate_driver_parser.add_argument("--verbose", action="store_true", dest="verbose",
                            help="Log extra output (debug=1).")
        simulate_driver_parser.add_argument("--console", action="store_true", dest="console",
                            help="Log to console in addition to syslog.")
        simulate_driver_parser.add_argument("--host",
                            help="The MQTT server.")
        simulate_driver_parser.add_argument("--topics",
                            help="Comma separated list of topics to subscribe to.")
        simulate_driver_parser.add_argument("--callback",
                            help="The callback type.")

    def __init__(self, options):
        """ Initialize the new instance. """
        if not options.type:
            self.simulator_parser.print_help()
            sys.exit(2)
        self.simulation_type = options.type
        self.binding = options.binding
        self.record_count = options.record_count
        self.interval = options.interval
        self.delay = options.delay
        self.callback = options.callback
        self.topics = options.topics
        self.host = options.host
        self.console = options.console
        self.config_file = options.conf
        self.units = options.units
        self.verbose = options.verbose

        self.engine = None
        self.config_dict = None

        print(f"Simulation is {self.simulation_type}")
        print(f"Creating {int(self.record_count)} {self.binding} records")
        print(f"Interval is {int(self.interval)} seconds")
        print(f"Delay is {int(self.delay)} seconds")

    def init_configuration(self):
        """ Initialuze the configuration object. """
        config_path = os.path.abspath(self.config_file)

        self.config_dict = configobj.ConfigObj(config_path, file_error=True)

        # override the configured binding with the parameter value
        merge_config(self.config_dict, {'MQTTSubscribeService': {'binding': self.binding}})

        if self.topics:
            topics = self.topics.split(',')
            if 'MQTTSubscribeService' in self.config_dict and 'topics' in self.config_dict['MQTTSubscribeService']:
                self.config_dict['MQTTSubscribeService']['topics'] = {}
            if 'MQTTSubscribeDriver' in self.config_dict and 'topics' in self.config_dict['MQTTSubscribeDriver']:
                self.config_dict['MQTTSubscribeDriver']['topics'] = {}
            for topic in topics:
                merge_config(self.config_dict, {'MQTTSubscribeService': {'topics': {topic:{}}}})
                merge_config(self.config_dict, {'MQTTSubscribeDriver': {'topics': {topic:{}}}})

        if self.host:
            merge_config(self.config_dict, {'MQTTSubscribeService': {'host': self.host}})
            merge_config(self.config_dict, {'MQTTSubscribeDriver': {'host': self.host}})

        if self.callback:
            merge_config(self.config_dict, {'MQTTSubscribeService': {'message_callback': {'type': self.callback}}})
            merge_config(self.config_dict, {'MQTTSubscribeDriver': {'message_callback': {'type': self.callback}}})

        if self.console:
            merge_config(self.config_dict, {'MQTTSubscribeService': {'console': True}})
            merge_config(self.config_dict, {'MQTTSubscribeDriver': {'console': True}})

    def init_weewx(self):
        """ Perform the necessary WeeWX initialization. """
        min_config_dict = {
            'Station': {
                'altitude': [0, 'foot'],
                'latitude': 0,
                'station_type': 'Simulator',
                'longitude': 0
            },
            'Simulator': {
                'driver': 'weewx.drivers.simulator',
            },
            'Engine': {
                'Services': {}
            }
        }

        self.engine = StdEngine(min_config_dict)

        weewx.accum.initialize(self.config_dict)

    def simulate_driver_archive(self, driver):
        """ Simulate running MQTTSubscribe as a driver that generates archive records. """
        i = 0
        while i < self.record_count:
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / self.interval) + 1) * self.interval
            end_delay_ts = end_period_ts + self.delay
            sleep_amount = end_delay_ts - current_time
            print(f"Sleeping {int(sleep_amount)} seconds")
            time.sleep(sleep_amount)

            for record in driver.genArchiveRecords(end_period_ts):
                print(f"Record is: {weeutil.weeutil.timestamp_to_string(record['dateTime'])} {to_sorted_string(record)}")

                i += 1
                if i >= self.record_count:
                    break

    def simulate_driver_packet(self, driver):
        """ Simulate running MQTTSubscribe as a driver that generates loop packets. """
        i = 0
        for packet in driver.genLoopPackets():
            print(f"Packet is: {weeutil.weeutil.timestamp_to_string(packet['dateTime'])} {to_sorted_string(packet)}")
            i += 1
            if i >= self.record_count:
                break

    def simulate_service(self):
        """ Simulate running MQTTSubscribe as a service. """
        service = MQTTSubscribeService(self.engine, self.config_dict)
        units = weewx.units.unit_constants[self.units]
        i = 0
        while i < self.record_count:
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time /self.interval) + 1) * self.interval
            end_delay_ts = end_period_ts + self.delay
            sleep_amount = end_delay_ts - current_time

            print(f"Sleeping {int(sleep_amount)} seconds")
            time.sleep(sleep_amount)

            data = {}
            data['dateTime'] = end_period_ts
            data['usUnits'] = units

            if self.binding == 'archive':
                data['interval'] = self.interval / 60
                new_archive_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                       record=data,
                                                       origin='hardware')
                self.engine.dispatchEvent(new_archive_record_event)
                print(
                    (f"Archive Record is: "
                    f"{weeutil.weeutil.timestamp_to_string(new_archive_record_event.record['dateTime'])} "
                    f"{to_sorted_string(new_archive_record_event.record)}"))
            elif self.binding == 'loop':
                new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=data)
                self.engine.dispatchEvent(new_loop_packet_event)
                print(
                    (f"Loop packet is: "
                    f"{weeutil.weeutil.timestamp_to_string(new_loop_packet_event.packet['dateTime'])} "
                    f"{to_sorted_string(new_loop_packet_event.packet)}"))

            i += 1

        service.shutDown()

    def run(self):
        """ Run the driver or service in standalone mode. """
        if self.simulation_type == "service":
            self.simulate_service()
        elif self.simulation_type == "driver":
            driver = "user.MQTTSubscribe"
            __import__(driver)
            # This is a bit of Python wizardry. First, find the driver module
            # in sys.modules.
            driver_module = sys.modules[driver]
            # Find the function 'loader' within the module:
            loader_function = getattr(driver_module, 'loader')
            driver = loader_function(self.config_dict, self.engine)

            if self.binding == "archive":
                self.simulate_driver_archive(driver)
            elif self.binding == "loop":
                self.simulate_driver_packet(driver)

class Configurator():
    ''' Configure the service or driver.'''
    # pylint: disable=too-many-instance-attributes

    @classmethod
    def add_parsers(cls, parser):
        ''' Add the parsers.'''
        subparser = parser.add_parser('configure')
        subparser.add_argument("--create-example",
                            help="Export the existing configuration.")

        configurator_subparsers = subparser.add_subparsers(dest='type')
        configurator_service_parser = configurator_subparsers.add_parser('service')
        configure_service_group = configurator_service_parser.add_mutually_exclusive_group(required=False)
        configurator_service_parser.add_argument("--conf",
                            help="The WeeWX configuration file. Typically weewx.conf.")
        configure_service_group.add_argument("--add-from",
                            help="The configuration that will and add to (but not update existing settings) the existing configuration.")
        configure_service_group.add_argument("--export",
                            help="Export the existing configuration.")
        configure_service_group.add_argument("--print-configspec",
                            help="Write the configspec to a file.")
        configure_service_group.add_argument("--replace-with",
                            help="The configuration that will replace the existing configuration.")
        configure_service_group.add_argument("--update-from",
                            help="The configuration that will update (and add to) the existing configuration.")
        configure_service_group.add_argument("--validate",  action="store_true", dest="validate",
                            help="Validate the configuration file.")
        # The following is only used by the service
        configurator_service_parser.add_argument("--enable", dest="enable",
                            help="Enable/Disable the service.")
        configurator_service_parser.add_argument("--no-backup", action="store_true", default=False,
                            help="When updating the WeeWX configuration (--conf), do not back it up.")
        configurator_service_parser.add_argument("--output",
                            help="Instead of updating the WeeWX configuration (--conf), write it to this file")

        configurator_driver_parser = configurator_subparsers.add_parser('driver')
        configure_driver_group = configurator_driver_parser.add_mutually_exclusive_group(required=False)
        configurator_driver_parser.add_argument("--conf",
                            help="The WeeWX configuration file. Typicall weewx.conf.")
        configure_driver_group.add_argument("--add-from",
                            help="The configuration that will and add to (but not update existing settings) the existing configuration.")
        configure_driver_group.add_argument("--export",
                            help="Export the existing configuration.")
        configure_driver_group.add_argument("--print-configspec",
                            help="Write the configspec to a file.")
        configure_driver_group.add_argument("--replace-with",
                            help="The configuration that will replace the existing configuration.")
        configure_driver_group.add_argument("--update-from",
                            help="The configuration that will update (and add to) the existing configuration.")
        configure_driver_group.add_argument("--validate",
                            help="Validate the configuration file.")
        configure_driver_group.add_argument("--no-backup", action="store_true", default=False,
                            help="When updating the WeeWX configuration (--conf), do not back it up.")
        configurator_driver_parser.add_argument("--output",
                            help="Instead of updating the WeeWX configuration (--conf), write it to this file")

        return subparser

    def __init__(self, parser, options):
        self.no_update_actions = ["--create-example", "--export", "--print-configspec", "--validate"]
        if (options.type and options.create_example) or (not options.type and not options.create_example):
            parser.error("Either 'service|driver' or '--create-example' is required.")

        if options.type == 'MQTTSubscribe' and options.enable and len(sys.argv) > 2:
            parser.error("'--enable' is mutually exclusive with all other options.")

        if options.type and options.output and options.export:
            parser.error("'--output' is mutually exclusive with '--create-example'")

        if options.type == 'service':
            self.section = 'MQTTSubscribeService'
        elif options.type == 'driver':
            self.section = 'MQTTSubscribeDriver'
        else:
            self.section = None

        self.config_spec = configobj.ConfigObj(CONFIG_SPEC_TEXT.splitlines())

        self.config_input_dict = None
        self.config_dict = None
        self.config_output_path = None
        self.oputput_path = None
        self.action = None
        self.enable = None

        if options.type:
            self._setup_subcommand(options)
        elif options.create_example:
            self.action = '--create-example'
            self.config_output_path = os.path.abspath(options.create_example)

        if options.type and options.no_backup and self.action in self.no_update_actions:
            parser.error(f"'--output' is mutually exclusive with '{self.no_update_actions}'")

        if options.type:
            self.no_backup = options.no_backup

    def _setup_subcommand(self, options):
        if options.conf:
            config_path = os.path.abspath(options.conf)
            self.config_dict = configobj.ConfigObj(config_path, encoding='utf-8', file_error=True)
            self.oputput_path = config_path

        config_input = None
        if options.add_from:
            self.action = '--add-from'
            config_input = options.add_from
            self.config_output_path = os.path.abspath(options.conf)
        elif options.export:
            self.action = '--export'
            self.config_output_path = os.path.abspath(options.export)
        elif options.print_configspec:
            self.action = '--print-configspec'
            self.config_output_path = os.path.abspath(options.print_configspec)
        if options.replace_with:
            self.action = '--replace-with'
            config_input = options.replace_with
            self.config_output_path = os.path.abspath(options.conf)
        if options.validate:
            self.action = '--validate'
            config_input = options.validate
        if options.update_from:
            self.action = '--update-from'
            config_input = options.update_from
            self.config_output_path = os.path.abspath(options.conf)

        if options.type == 'service' and options.enable:
            self.enable = to_bool(options.enable)

        if options.output:
            self.config_output_path = os.path.abspath(options.output)

        if config_input:
            config_input_path = os.path.abspath(config_input)
            config_input_dict = configobj.ConfigObj(config_input_path, encoding='utf-8', file_error=True)
            self.config_input_dict = weeutil.config.deep_copy(config_input_dict[self.section])

    def run(self):
        ''' Update the configuration. '''
        if self.action == '--add-from':
            weeutil.config.conditional_merge(self.config_dict[self.section], self.config_input_dict)
        elif self.action == '--create-example':
            mqttsubscribe_configuration = MQTTSubscribeConfiguration(None)
            default_configuration = mqttsubscribe_configuration.default_config
            default_configuration.filename = self.config_output_path
            default_configuration.write()
        elif self.action == '--export':
            export_dict = {}
            export_dict[self.section] = self.config_dict[self.section]
            export_config = configobj.ConfigObj(export_dict)
            export_config.filename = self.config_output_path
            export_config.write()
        elif self.action == '--print-configspec':
            self.config_spec.filename = self.config_output_path
            self.config_spec.write()
        elif self.action == '--replace-with':
            #del self.config_dict[self.section]
            self.config_dict[self.section] = self.config_input_dict
        elif self.action == '--validate':
            self._validate("", "", self.config_input_dict, self.config_spec['MQTTSubscribe'])
        elif self.action == '--update-from':
            self.config_dict[self.section] = self.config_input_dict
        else:
            conf_editor = MQTTSubscribeDriverConfEditor()
            conf_editor.existing_options = self.config_dict.get(self.section, {})
            settings = conf_editor.prompt_for_settings()
            # copy the keys that have been configured/channged, similar to weecfg.modify_config
            for key, value in settings.items():
                self.config_dict[self.section][key] = value

        if self.section == 'MQTTSubscribService' and self.enable is not None:
            self.config_dict[self.section]['enable'] = self.enable

        if self.action not in self.no_update_actions:
            weecfg.save(self.config_dict, self.config_output_path, not self.no_backup)
            #self.config_dict.filename = self.config_output_path
            #self.config_dict.write()

    def _validate(self, parent, hierarchy, section, section_configspec):
        hierarchy += f"{section.name}-"
        for key, value in section.items():
            if key in section.sections:
                continue
            if key not in section_configspec:
                print(f"ERROR: Unknown option: {hierarchy}{key}")
            if "REPLACE_ME" in value:
                print(f"ERROR: Specify a value for: {hierarchy}{key}")

        for subsection in section.sections:
            if "REPLACE_ME" in subsection:
                print(f"ERROR: Specify a value for: {hierarchy}{subsection}")
            elif subsection not in section_configspec.sections and parent == 'subfields':
                self._validate(subsection,
                               hierarchy,
                               section[subsection],
                               self.config_spec['MQTTSubscribe']['topics']['REPLACE_ME']["REPLACE_ME"])
            elif subsection not in section_configspec.sections:
                if "REPLACE_ME" in section_configspec.sections:
                    self._validate(subsection, hierarchy, section[subsection], section_configspec["REPLACE_ME"])
                else:
                    print(f"ERROR: Unknown option: {hierarchy}{subsection}")
            else:
                self._validate(subsection, hierarchy, section[subsection], section_configspec[subsection])

# To Run
# setup.py install:
# PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/MQTTSubscribe.py
#
# rpm or deb package install:
# PYTHONPATH=/usr/share/weewx python /usr/share/weewx/user/MQTTSubscribe.py
if __name__ == '__main__': # pragma: no cover
    def main():
        """ Run it."""

        print("start")
        parser = argparse.ArgumentParser()
        parser.add_argument('--version', action='version', version=f"MQTTSubscribe version is {VERSION}")

        subparsers = parser.add_subparsers(dest='command')

        Simulator.add_parsers(subparsers)
        configurator_subparser = Configurator.add_parsers(subparsers)

        options = parser.parse_args()

        if options.command == 'simulate':
            simulator = Simulator(options)
            simulator.init_configuration()
            simulator.init_weewx()
            simulator.run()
        elif options.command == 'configure':
            configurator = Configurator(configurator_subparser, options)
            configurator.run()
        else:
            parser.print_help()

        print("done")

    main()
