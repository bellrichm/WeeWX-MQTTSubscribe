"""
WeeWX driver and service that subscribes to MQTT topics and
creates/updates loop packets/archive records.

Installation:
    Put this file in the bin/user directory.
    Update weewx.conf [MQTTSubscribeService] as needed to configure the service.
    Update weewx.conf [MQTTSubscribeDriver] as needed to configure the driver.
    Update weewx.conf [Accumulator] for any custom fields.

Overview:
    The MQTT loop_start is used to run a separate thread to manage the MQTT subscriptions.
    The payloads are put on a queue to be processed by the driver or service.

    The service binds to either the NEW_LOOP_PACKET or NEW_ARCHIVE_RECORD event.
    On this event, it processes the queue of MQTT payloads and updates the packet or record

    The driver processes the queue and generates a packet for each element currently in the queue.
    A topic can be desinated as an 'archive topic'. Data in this topic is returned as an archive record.

Configuration:
[MQTTSubscribeService] or [MQTTSubscribeDriver]
    # The MQTT server.
    # Default is: localhost
    host = localhost

    # The port to connect to.
    # Default is: 1883
    port = 1883

    # Maximum period in seconds allowed between communications with the broker.
    # Default is: 60
    keepalive = 60

    # username for broker authentication.
    # Default is: None
    username = None

    # password for broker authentication.
    # Default is: None
    password = None

    # Controls the MQTT logging.
    # Default is: false
    log = false

    # The clientid to connect with.
    # Service default is: MQTTSubscribeService-xxxx
    # Driver default is: MQTTSubscribeDriver-xxxx
    #    where xxxx is a random number between 1000 and 9999
    clientid =

    # The topic to subscribe to.
    # DEPRECATED - use [[topics]]
    # topic =

    # Turn the service on and off.
    # Default is: true
    # Only used by the service.
    enable = false

    # The amount of time in seconds to overlap the start time when processing the MQTT queue.
    # When the time of the MQTT payload is less than the end time of the previous packet/record,
    # the MQTT payload is ignored. When overlap is set, MQTT payloads within this number of seconds
    # of the previous end time will be processed.
    # Default is: 0
    # Only used by the service.
    # DEPRECATED  - use adjust_start_time
    # overlap = 0

    # The binding, loop or archive.
    # Default is: loop
    # Only used by the service.
    binding = loop

    # When the MQTT queue has no data, the amount of time in seconds to wait
    # before checking again.
    # Default is: 2
    # Only used by the driver
    wait_before_retry = 2

    # Payload in this topic is processed like an archive record.
    # Default is: None
    # Only used by the driver.
    archive_topic = None

    # DEPRECATED - move the expires_after under the [[topic]]/[[[topic name]]][[[[fieldname]]]]
    # Fields in this section will be cached.
    # If the field is not in the current archive record, its value will be retrieved from the cache.
    # Only used by the service.
    # EXPERIMENTAL - may be removed
    # [[archive_field_cache]]
    #     # The unit system of the cache.
    #     # This must match the unit_system of the archive record.
    #     # Default is US.
    #     unit_system = US
    #
    #     # The WeeWX fields to cache.
    #     [[[fields]]]
    #         # The name of the field to cache.
    #         [[[[fieldname]]]]
    #             # In seconds how long the cache is valid.
    #             # Value of 0 means the cache is always expired.
    #             # Useful if missing fields should have a value of None instead of the previous value.
    #             # Value of None means the cache never expires.
    #             # Default is None.
    #             expires_after = None

    # Configuration for the message callback.
    [[message_callback]]
        # The format of the MQTT payload.
        # Currently support: individual, json, keyword
        # Must be specified.
        type = REPLACE_ME

        # When True, the full topic (weather/outTemp) is used as the fieldname.
        # When false, the topic furthest to the right is used.
        # Valid values: True, False
        # Default is: False
        # Only used when type is 'individual'.
        full_topic_fieldname = False

        # When the json is nested, the delimiter between the hierarchies.
        # Default is: _
        flatten_delimiter = _

        # The delimiter between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is: ,
        keyword_delimiter = ","

        # The separator between fieldname and value pairs. (field1=value1, field2=value2).
        # Default is: =
        keyword_separator = =

        # List of fields that are cumulative values
        # Default is: [] (empty list)
        # DEPRECATED - use [[[fields]]] contains_total setting.
        # contains_total =

        # Mapping to WeeWX names.
        # DEPRECATED - use [[[fields]]] name setting
        # [[[label_map]]]
        #     temp1 = extraTemp1

        # Information to map the MQTT data to WeeWX.
        # DEPRECATED - move the fieldname under the [[topic]]/[[[topic name]]]
        # [[[fields]]]
        #     # The incoming field name from MQTT.
        #     [[[[temp1]]]
        #        # The WeeWX name.
        #         # Default is the name from MQTT.
        #         name = extraTemp1
        #
        #         # The conversion type necessary for WeeWX compatibility
        #         # Valid values: bool, float, int, none
        #         # Default is float
        #         conversion_type = float
        #
        #         # The units of the incoming data.
        #         # Useful if this field's units differ from the topic's unit_system's units.
        #         # Valid values: see, http://www.weewx.com/docs/customizing.htm#units
        #         # Default is not set
        #         # units = km_per_hour
        #
        #         # True if the incoming data is cumulative.
        #         # Valid values: True, False
        #         # Default is False
        #         contains_total = False
        #
        #         # True if the incoming data should not be processed into WeeWX.
        #         # Valid values: True, False
        #         # Default is False
        #         ignore = False

    # The topics to subscribe to.
    [[topics]
        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX
        # Default is: US
        unit_system = US

        # Even if the payload has a datetime, ignore it and use the server datetime
        # Default is False
        use_server_datetime = False

        # When True, the MQTT datetime will be not be checked that is greater than the last packet processed.
        # Default is False
        # Only used by the service.
        ignore_start_time = False

        # When the True, the MQTT data will continue to be processed even if its datetime is greater than the packet's datetime.
        # Default is False
        # Only used by the service.
        ignore_end_time = False

        # Allow MQTT data with a datetime this many seconds prior to the previous packet's datetime
        # to be added to the current packet.
        # Default is 0
        # Only used by the service.
        adjust_start_time = 0

        # Allow MQTT data with a datetime this many seconds after the current packet's datetime
        # to be added to the current packet.
        # Default is 0
        # Only used by the service.
        adjust_end_time = 0

        # The maximum queue size.
        # When the queue is larger than this value, the oldest element is removed.
        # In general the queue should not grow large, but it might if the time
        # between the driver creating packets is large and the MQTT broker publishes frequently.
        # Or if subscribing to 'individual' payloads with wildcards. This results in many topic
        # in a single queue.
        # Default is: sys.maxsize for python 3 and sys.maxint for python 2
        max_queue = MAXSIZE

        [[[first/topic]]]
            # The incoming field name from MQTT.
            [[[[temp1]]]
                # The WeeWX name.
                # Default is the name from MQTT.
                name = extraTemp1

                # The conversion type necessary for WeeWX compatibility
                # Valid values: bool, float, int, none
                # Default is float
                conversion_type = float

                # The units of the incoming data.
                # Useful if this field's units differ from the topic's unit_system's units.
                # Valid values: see, http://www.weewx.com/docs/customizing.htm#units
                # Default is not set
                # units = km_per_hour

                # True if the incoming data is cumulative.
                # Valid values: True, False
                # Default is False
                contains_total = False

                # True if the incoming data should not be processed into WeeWX.
                # Valid values: True, False
                # Default is False
                ignore = False

                # In seconds how long the cache is valid.
                # Value of 0 means the cache is always expired.
                # Useful if missing fields should have a value of None instead of the previous value.
                # Value of None means the cache never expires.
                # Default is not set.
                # EXPERIMENTAL - may be removed
                # expires_after = None

        [[[second/topic]]]
"""

from __future__ import with_statement
from __future__ import print_function
import copy
import datetime
import json
import locale
import logging
import platform
import random
import re
import sys
import time
from collections import deque

import configobj
import paho.mqtt.client as mqtt

import weewx
import weewx.drivers
from weewx.engine import StdService
import weeutil
from weeutil.weeutil import option_as_list, to_bool, to_float, to_int, to_sorted_string

VERSION = '1.5.3'
DRIVER_NAME = 'MQTTSubscribeDriver'
DRIVER_VERSION = VERSION

# Stole from six module. Added to eliminate dependency on six when running under WeeWX 3.x
PY2 = sys.version_info[0] == 2
if PY2:
    MAXSIZE = sys.maxint # (only a python 3 error) pylint: disable=no-member
else:
    MAXSIZE = sys.maxsize

try: # pragma: no cover
    import weeutil.logger
    def setup_logging(logging_level, config_dict):
        """ Setup logging for running in standalone mode."""
        if logging_level:
            weewx.debug = logging_level

        weeutil.logger.setup('wee_MQTTSS', config_dict) # weewx3 false positive, code never reached pylint: disable=no-member

    class Logger(object):
        """ The logging class. """
        def __init__(self, mode, level='NOTSET', filename=None, console=None):
            self.mode = mode
            self.filename = filename
            self.console = console
            # Setup custom TRACE level
            self.trace_level = 5
            if logging.getLevelName(self.trace_level) == 'Level 5':
                logging.addLevelName(self.trace_level, "TRACE")

            self._logmsg = logging.getLogger(__name__)
            if self.console:
                self._logmsg.addHandler(logging.StreamHandler(sys.stdout))

            self.level = logging._checkLevel(level) # not sure there is a better way pylint: disable=protected-access
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

        def log_environment(self):
            """ Log the environment we are running in. """
            # Since WeeWX logs this, only log it when debugging
            self.debug("Using weewx version %s" % weewx.__version__)
            self.debug("Using Python %s" % sys.version)
            self.debug("Platform %s" % platform.platform())
            self.debug("Locale is '%s'" % locale.setlocale(locale.LC_ALL))
            self.info("Version is %s" % VERSION)
            self.info("Log level: %i" % self.trace_level)
            self.info("Log debug setting: %i" % self.weewx_debug)
            self.info("Log console: %s" % self.console)
            self.info("Log file: %s" % self.filename)

        def trace(self, msg):
            """ Log trace messages. """
            if self.weewx_debug > 1:
                self._logmsg.debug("(%s) %s", self.mode, msg)
            else:
                self._logmsg.log(self.trace_level, "(%s) %s", self.mode, msg)

        def debug(self, msg):
            """ Log debug messages. """
            self._logmsg.debug("(%s) %s", self.mode, msg)

        def info(self, msg):
            """ Log informational messages. """
            self._logmsg.info("(%s) %s", self.mode, msg)

        def error(self, msg):
            """ Log error messages. """
            self._logmsg.error("(%s) %s", self.mode, msg)
except ImportError: # pragma: no cover
    import syslog
    def setup_logging(logging_level, config_dict): # Need to match signature pylint: disable=unused-argument
        """ Setup logging for running in standalone mode."""
        syslog.openlog('wee_MQTTSS', syslog.LOG_PID | syslog.LOG_CONS)
        if logging_level:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
        else:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

    class Logger(object):
        """ The logging class. """
        def __init__(self, mode, level='NOTSET', filename=None, console=None): # Need to match signature pylint: disable=unused-argument
            self.mode = mode
            self.filename = filename
            self.weewx_debug = weewx.debug
            # Setup custom TRACE level
            self.trace_level = 5
            if logging.getLevelName(self.trace_level) == 'Level 5':
                logging.addLevelName(self.trace_level, "TRACE")

            self.level = logging._checkLevel(level) # not sure there is a better way pylint: disable=protected-access
            self.console = console

            self.file = None
            if self.filename is not None:
                self.file = open(filename, 'w')

        def log_environment(self):
            """ Log the environment we are running in. """
            # Since WeeWX logs this, only log it when debugging
            self.debug("Using weewx version %s" % weewx.__version__)
            self.debug("Using Python %s" % sys.version)
            self.debug("Platform %s" % platform.platform())
            self.debug("Locale is '%s'" % locale.setlocale(locale.LC_ALL))
            self.info("Version is %s" % VERSION)
            self.info("Log level: %i" % self.trace_level)
            self.info("Log debug setting: %i" % self.weewx_debug)
            self.info("Log console: %s" % self.console)
            self.info("Log file: %s" % self.filename)

        def trace(self, msg):
            """ Log trace messages. """
            if self.level == self.trace_level or self.weewx_debug > 1:
                self._logmsg(syslog.LOG_DEBUG, msg)

        def debug(self, msg):
            """ Log debug messages. """
            self._logmsg(syslog.LOG_DEBUG, msg)

        def info(self, msg):
            """ Log informational messages. """
            self._logmsg(syslog.LOG_INFO, msg)

        def error(self, msg):
            """ Log error messages. """
            self._logmsg(syslog.LOG_ERR, msg)

        def _logmsg(self, dst, msg):
            syslog.syslog(dst, '(%s) %s: %s' % (self.mode, __name__, msg))
            if self.console:
                print('%s: %s' % (__name__, msg))
            if self.file:
                self.file.write('%s: %s\n' % (__name__, msg))

# pylint: disable=fixme

class RecordCache(object):
    """ Manage the cache. """
    def __init__(self, unit_system):
        self.unit_system = unit_system
        self.cached_values = {}

    def get_value(self, key, timestamp, expires_after):
        """ Get the cached value. """
        if key in self.cached_values and \
            (expires_after is None or timestamp - self.cached_values[key]['timestamp'] < expires_after):
            return self.cached_values[key]['value']

        return None

    def update_value(self, key, value, unit_system, timestamp):
        """ Update the cached value. """
        if unit_system != self.unit_system:
            raise ValueError("Unit system does not match unit system of the cache. %s vs %s"
                             % (unit_system, self.unit_system))
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

class CollectData(object):
    """ Manage fields that are 'grouped together', like wind data. """
    def __init__(self, fields, unit_system):
        self.fields = fields
        self.unit_system = unit_system
        self.data = {}

    def add_data(self, field, in_data):
        """ Add data to the collection and return old collection if this field is already in the collection. """
        old_data = {}
        if field in self.data:
            old_data = dict(self.data)
            old_data['usUnits'] = self.unit_system
            self.data = {}

        target_data = weewx.units.to_std_system(in_data, self.unit_system)

        self.data[field] = target_data[field]
        self.data['dateTime'] = in_data['dateTime']

        return old_data

    def get_data(self):
        """ Return the collection. """
        if self.data != {}:
            self.data['usUnits'] = self.unit_system
        return self.data

class TopicManager(object):
    # pylint: disable=too-many-instance-attributes
    """ Manage the MQTT topic subscriptions. """
    def __init__(self, config, logger):
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        self.logger = logger

        if not config.sections:
            raise ValueError("At least one topic must be configured.")

        self.logger.debug("TopicManager config is %s" % config)

        default_qos = to_int(config.get('qos', 0))
        default_use_server_datetime = to_bool(config.get('use_server_datetime', False))
        default_ignore_start_time = to_bool(config.get('ignore_start_time', False))
        default_ignore_end_time = to_bool(config.get('ignore_end_time', False))
        overlap = to_float(config.get('overlap', 0)) # Backwards compatibility
        default_adjust_start_time = to_float(config.get('adjust_start_time', overlap))
        default_adjust_end_time = to_float(config.get('adjust_end_time', 0))
        default_datetime_format = config.get('datetime_format', None)
        default_offset_format = config.get('offset_format', None)
        ignore_default = to_bool(config.get('ignore', False))
        contains_total_default = to_bool(config.get('contains_total', False))
        conversion_type_default = config.get('conversion_type', 'float')

        default_unit_system_name = config.get('unit_system', 'US').strip().upper()
        if default_unit_system_name not in weewx.units.unit_constants:
            raise ValueError("MQTTSubscribe: Unknown unit system: %s" % default_unit_system_name)

        max_queue = config.get('max_queue', MAXSIZE)

        self.topics = {}
        self.subscribed_topics = {}
        self.managing_fields = False
        self.record_cache = {}

        for topic in config.sections:
            topic_dict = config.get(topic, {})

            qos = to_int(topic_dict.get('qos', default_qos))
            use_server_datetime = to_bool(topic_dict.get('use_server_datetime',
                                                         default_use_server_datetime))
            ignore_start_time = to_bool(topic_dict.get('ignore_start_time', default_ignore_start_time))
            ignore_end_time = to_bool(topic_dict.get('ignore_end_time', default_ignore_end_time))
            adjust_start_time = to_float(topic_dict.get('adjust_start_time', default_adjust_start_time))
            adjust_end_time = to_float(topic_dict.get('adjust_end_time', default_adjust_end_time))
            datetime_format = topic_dict.get('datetime_format', default_datetime_format)
            offset_format = topic_dict.get('offset_format', default_offset_format)
            fields_ignore_default = to_bool(topic_dict.get('ignore', ignore_default))
            fields_contains_total_default = to_bool(topic_dict.get('contains_total', contains_total_default))
            fields_conversion_type_default = topic_dict.get('conversion_type', conversion_type_default)

            unit_system_name = topic_dict.get('unit_system', default_unit_system_name).strip().upper()
            if unit_system_name not in weewx.units.unit_constants:
                raise ValueError("MQTTSubscribe: Unknown unit system: %s" % unit_system_name)
            unit_system = weewx.units.unit_constants[unit_system_name]

            self.subscribed_topics[topic] = {}
            self.subscribed_topics[topic]['type'] = 'normal'
            self.subscribed_topics[topic]['unit_system'] = unit_system
            self.subscribed_topics[topic]['qos'] = qos
            self.subscribed_topics[topic]['use_server_datetime'] = use_server_datetime
            self.subscribed_topics[topic]['ignore_start_time'] = ignore_start_time
            self.subscribed_topics[topic]['ignore_end_time'] = ignore_end_time
            self.subscribed_topics[topic]['adjust_start_time'] = adjust_start_time
            self.subscribed_topics[topic]['adjust_end_time'] = adjust_end_time
            self.subscribed_topics[topic]['datetime_format'] = datetime_format
            self.subscribed_topics[topic]['offset_format'] = offset_format
            self.subscribed_topics[topic]['max_queue'] = topic_dict.get('max_queue', max_queue)
            self.subscribed_topics[topic]['queue'] = deque()

            if topic_dict.sections:
                self.managing_fields = True

            self.subscribed_topics[topic]['fields'] = {}
            for field in topic_dict.sections:
                self.subscribed_topics[topic]['fields'][field] = {}
                self.subscribed_topics[topic]['fields'][field]['name'] = (topic_dict[field]).get('name', field)
                self.subscribed_topics[topic]['fields'][field]['ignore'] = to_bool((topic_dict[field]).get('ignore', fields_ignore_default))
                self.subscribed_topics[topic]['fields'][field]['contains_total'] = \
                    to_bool((topic_dict[field]).get('contains_total', fields_contains_total_default))
                self.subscribed_topics[topic]['fields'][field]['conversion_type'] = \
                    (topic_dict[field]).get('conversion_type', fields_conversion_type_default)
                if 'expires_after' in topic_dict[field]:
                    self.record_cache[field] = {}
                    self.record_cache[field]['expires_after'] = to_float(topic_dict[field]['expires_after'])
                if 'units' in topic_dict[field]:
                    if topic_dict[field]['units'] in weewx.units.conversionDict:
                        self.subscribed_topics[topic]['fields'][field]['units'] = topic_dict[field]['units']
                    else:
                        raise ValueError("For %s invalid units, %s" % (field, topic_dict[field]['units']))

        # Add the collector queue as a subscribed topic so that data can retrieved from it
        # Yes, this is a bit of a hack.
        # Note, it would not be too hard to allow additional fields via the [fields] configuration option
        self.collected_units = weewx.units.unit_constants[default_unit_system_name]
        self.collected_fields = ['windGust', 'windGustDir', 'windDir', 'windSpeed']
        self.collected_queue = deque()
        self.collected_topic = "%f-%s" % (time.time(), '-'.join(self.collected_fields))
        topic = self.collected_topic
        self.subscribed_topics[topic] = {}
        self.subscribed_topics[topic]['type'] = 'collector'
        self.subscribed_topics[topic]['unit_system'] = weewx.units.unit_constants[default_unit_system_name]
        self.subscribed_topics[topic]['qos'] = default_qos
        self.subscribed_topics[topic]['use_server_datetime'] = default_use_server_datetime
        self.subscribed_topics[topic]['ignore_start_time'] = default_ignore_start_time
        self.subscribed_topics[topic]['ignore_end_time'] = default_ignore_end_time
        self.subscribed_topics[topic]['adjust_start_time'] = default_adjust_start_time
        self.subscribed_topics[topic]['adjust_end_time'] = default_adjust_end_time
        self.subscribed_topics[topic]['datetime_format'] = default_datetime_format
        self.subscribed_topics[topic]['offset_format'] = default_offset_format
        self.subscribed_topics[topic]['max_queue'] = max_queue
        self.subscribed_topics[topic]['queue'] = self.collected_queue

        self.logger.debug("TopicManager self.subscribed_topics is %s" % self.subscribed_topics)
        self.logger.debug("TopicManager self.record_cache is %s" % self.record_cache)

    def append_data(self, topic, in_data, fieldname=None):
        """ Add the MQTT data to the queue. """
        self.logger.debug("TopicManager data-> incoming %s: %s"
                          %(topic, to_sorted_string(in_data)))
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
            self._queue_size_check(self.collected_queue, self._get_max_queue(topic))
            self.logger.trace("TopicManager Adding wind data %s %s: %s"
                              % (fieldname, weeutil.weeutil.timestamp_to_string(data['dateTime']), to_sorted_string(data)))
            payload['fieldname'] = fieldname
            self.collected_queue.append(payload)
        else:
            self._queue_size_check(queue, self._get_max_queue(topic))
            self.logger.trace("TopicManager Added to queue %s %s %s: %s"
                              %(topic, self._lookup_topic(topic),
                                weeutil.weeutil.timestamp_to_string(data['dateTime']), to_sorted_string(data)))
            queue.append(payload,)

    def peek_datetime(self, topic):
        """ Return the date/time of the first element in the queue. """
        queue = self._get_queue(topic)
        self.logger.trace("TopicManager queue size is: %i" % len(queue))
        datetime_value = None
        if queue:
            datetime_value = queue[0]['data']['dateTime']

        return datetime_value

    def peek_last_datetime(self, topic):
        """ Return the date/time of the last element in the queue. """
        queue = self._get_queue(topic)
        self.logger.trace("TopicManager queue size is: %i" % len(queue))
        datetime_value = 0
        if queue:
            datetime_value = queue[-1]['data']['dateTime']

        return datetime_value

    def has_data(self, topic):
        """ Return True if queue has data. """
        return bool(self._get_queue(topic))

    def get_data(self, topic, end_ts=MAXSIZE):
        """ Get data off the queue of MQTT data. """
        queue = self._get_queue(topic)
        self.logger.trace("TopicManager starting queue %s size is: %i" %(topic, len(queue)))
        collector = CollectData(self.collected_fields, self.collected_units)
        while queue:
            if queue[0]['data']['dateTime'] > end_ts:
                self.logger.trace("TopicManager leaving queue: %s size: %i content: %s" %(topic, len(queue), queue[0]))
                break
            payload = queue.popleft()
            if self.get_type(topic) == 'collector':
                fieldname = payload['fieldname']
                self.logger.trace("TopicManager processing wind data %s %s: %s."
                                  %(fieldname, weeutil.weeutil.timestamp_to_string(payload['data']['dateTime']), to_sorted_string(payload)))
                data = collector.add_data(fieldname, payload['data'])
            else:
                data = payload['data']

            if data:
                self.logger.debug("TopicManager data-> outgoing %s: %s"
                                  %(topic, to_sorted_string(data)))
                yield data

        data = collector.get_data()
        if data:
            self.logger.debug("TopicManager data-> outgoing collected %s: %s"
                              % (topic, to_sorted_string(data)))
            yield data

    def get_accumulated_data(self, topic, start_time, end_time, units):
        """ Get the MQTT data after being accumulated. """
        if not self.has_data(topic):
            return {}

        ignore_start_time = self._get_value('ignore_start_time', topic)
        ignore_end_time = self._get_value('ignore_end_time', topic)
        adjust_start_time = self._get_value('adjust_start_time', topic)
        adjust_end_time = self._get_value('adjust_end_time', topic)

        if ignore_start_time:
            self.logger.trace("TopicManager ignoring start time.")
            start_ts = self.peek_datetime(topic) - adjust_start_time
        else:
            start_ts = start_time - adjust_start_time

        if ignore_end_time:
            self.logger.trace("TopicManager ignoring end time.")
            end_ts = self.peek_last_datetime(topic) + adjust_end_time
        else:
            end_ts = end_time + adjust_end_time

        self.logger.trace("TopicManager processing interval: %f %f" %(start_ts, end_ts))
        accumulator = weewx.accum.Accum(weeutil.weeutil.TimeSpan(start_ts, end_ts))

        for data in self.get_data(topic, end_ts):
            if data:
                try:
                    self.logger.trace("TopicManager input to accumulate %s %s: %s"
                                      % (topic, weeutil.weeutil.timestamp_to_string(data['dateTime']), to_sorted_string(data)))
                    accumulator.addRecord(data)
                except weewx.accum.OutOfSpan:
                    self.logger.info("TopicManager ignoring record outside of interval %f %f %f %s"
                                     %(start_ts, end_ts, data['dateTime'], (to_sorted_string(data))))
            else:
                break

        target_data = {}
        if not accumulator.isEmpty:
            aggregate_data = accumulator.getRecord()
            self.logger.trace("TopicManager prior to conversion is %s %s: %s"
                              % (topic, weeutil.weeutil.timestamp_to_string(aggregate_data['dateTime']), to_sorted_string(aggregate_data)))
            target_data = weewx.units.to_std_system(aggregate_data, units)
            self.logger.trace("TopicManager after conversion is %s %s: %s"
                              % (topic, weeutil.weeutil.timestamp_to_string(target_data['dateTime']), to_sorted_string(target_data)))
        else:
            self.logger.trace("TopicManager accumulator was empty")

        # Force dateTime to packet's datetime so that the packet datetime is not updated to the MQTT datetime
        if ignore_end_time:
            target_data['dateTime'] = end_time

        self.logger.debug("TopicManager data-> outgoing accumulated %s: %s"
                          % (topic, to_sorted_string(target_data)))
        return target_data

    def _queue_size_check(self, queue, max_queue):
        while len(queue) >= max_queue:
            element = queue.popleft()
            self.logger.error("TopicManager queue limit %i reached. Removing: %s" %(max_queue, element))

    def get_fields(self, topic):
        """ Get the fields. """
        return self._get_value('fields', topic)

    def get_qos(self, topic):
        """ Get the QOS. """
        return self._get_value('qos', topic)

    def get_type(self, topic):
        """ Get the type. """
        return self._get_value('type', topic)

    def get_unit_system(self, topic):
        """ Get the unit system """
        return self._get_value('unit_system', topic)

    def _get_max_queue(self, topic):
        return self._get_value('max_queue', topic)

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

        return None

    def _to_epoch(self, datetime_input, datetime_format, offset_format=None):
        self.logger.trace("TopicManager datetime conversion datetime_input:%s datetime_format:%s offset_format:%s"
                          %(datetime_input, datetime_format, offset_format))
        if offset_format:
            offset_start = len(datetime_input)-len(offset_format)
            offset = re.sub(r"\D", "", datetime_input[offset_start:]) #remove everything but the numbers from the UTC offset
            sign = datetime_input[offset_start-1:offset_start] # offset plus or minus
            offset_delta = datetime.timedelta(hours=int(offset[:2]), minutes=int(offset[2:]))
            if sign == '-':
                offset_delta = -offset_delta

            datetime_string = datetime_input[:offset_start-1].strip()

            self.logger.trace("TopicManager datetime conversion offset:%s sign:%s" %(offset, sign))

        else:
            datetime_string = datetime_input
            offset_delta = datetime.timedelta(hours=0, minutes=0)

        epoch = time.mktime((datetime.datetime.strptime(datetime_string, datetime_format) + offset_delta).timetuple())
        self.logger.trace("TopicManager datetime conversion datetime_string:%s epoch:%s" %(datetime_string, epoch))

        return epoch

class MessageCallbackProvider(object):
    # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """ Provide the MQTT callback. """
    def __init__(self, config, logger, topic_manager):
        self.logger = logger
        self.topic_manager = topic_manager
        self.logger.debug("MessageCallbackProvider config is %s" % config)
        self._setup_callbacks()
        self.type = config.get('type', None)
        self.flatten_delimiter = config.get('flatten_delimiter', '_')
        self.keyword_delimiter = config.get('keyword_delimiter', ',')
        self.keyword_separator = config.get('keyword_separator', '=')
        contains_total = option_as_list(config.get('contains_total', []))
        label_map = config.get('label_map', {})
        self.full_topic_fieldname = to_bool(config.get('full_topic_fieldname', False))

        self.fields = config.get('fields', {})
        orig_fields = config.get('fields', {})

        if self.type not in self.callbacks:
            raise ValueError("Invalid type configured: %s" % self.type)

        self.fields_ignore_default = to_bool(self.fields.get('ignore', False))

        if self.fields:
            self.logger.info("'fields' is deprecated, use '[[topics]][[[topic name]]][[[[fieldname]]]]'")
            if self.topic_manager.managing_fields:
                self.logger.debug("MessageCallbackProvider ignoring fields configuration and using topics/fields configuration.")

            for field in self.fields.sections:
                self.fields[field]['ignore'] = to_bool((self.fields[field]).get('ignore', self.fields_ignore_default))
                if  'contains_total' in self.fields[field]:
                    self.fields[field]['contains_total'] = to_bool(self.fields[field]['contains_total'])
                if 'conversion_type' in self.fields[field]:
                    self.fields[field]['conversion_type'] = self.fields[field]['conversion_type'].lower()
                if 'units' in self.fields[field]:
                    try:
                        weewx.units.conversionDict[self.fields[field]['units']]
                    except KeyError:
                        raise ValueError("For %s invalid units, %s" % (field, self.fields[field]['units']))

        self.set_backwards_compatibility(label_map, orig_fields, contains_total)
        self.previous_values = {}

        self.logger.debug("MessageCallbackProvider self.fields is %s" % self.fields)

    def set_backwards_compatibility(self, label_map, orig_fields, contains_total):
        """ Any config for backwards compatibility. """
        # backwards compatible, add the label map
        # ToDo - fix side affect of setting self.fields
        for field in label_map:
            if not field in orig_fields:
                self.fields[field] = {}
            if not 'name' in self.fields[field]:
                self.fields[field]['name'] = label_map[field]

        # backwards compatible, add the cumulative fields
        for field in contains_total:
            if not field in orig_fields:
                if not field in self.fields:
                    value = {}
                    value['contains_total'] = True
                    self.fields[field] = value
                else:
                    self.fields[field]['contains_total'] = True

    def get_callback(self):
        """ Get the MQTT callback. """
        return self.callbacks[self.type]

    def _setup_callbacks(self):
        self.callbacks = {}
        self.callbacks['individual'] = self._on_message_individual
        self.callbacks['json'] = self._on_message_json
        self.callbacks['keyword'] = self._on_message_keyword

    @staticmethod
    def _convert_value(fields, field, value):
        conversion_type = fields.get(field, {}).get('conversion_type', 'float')
        if conversion_type == 'bool':
            return to_bool(value)
        if conversion_type == 'float':
            return to_float(value)
        if conversion_type == 'int':
            return to_int(value)

        return value

    def _byteify(self, data, ignore_dicts=False):
        if PY2:
            # if this is a unicode string, return its string representation
            if isinstance(data, unicode): # (never called under python 3) pylint: disable=undefined-variable
                return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [self._byteify(item, ignore_dicts=True) for item in data]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            data2 = {}
            for key, value in data.items():
                key2 = self._byteify(key, ignore_dicts=True)
                value2 = self._byteify(value, ignore_dicts=True)
                data2[key2] = value2
            return data2
        # if it's anything else, return it in its original form
        return data

    def _flatten_dict(self, dictionary, separator):
        def _items():
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    for subkey, subvalue in self._flatten_dict(value, separator).items():
                        yield key + separator + subkey, subvalue
                else:
                    yield key, value

        return dict(_items())

    def _get_fields(self, topic):
        if self.topic_manager.managing_fields:
            return self.topic_manager.get_fields(topic)

        return self.fields

    def _calc_increment(self, observation, current_total, previous_total):
        self.logger.trace("MessageCallbackProvider _calc_increment calculating increment " \
                         "for %s with current: %f and previous %s values."
                          % (observation, current_total, (previous_total is None and 'None' or str(previous_total))))

        if current_total is not None and previous_total is not None:
            if current_total >= previous_total:
                return current_total - previous_total

            self.logger.trace("MessageCallbackProvider _calc_increment skipping calculating increment " \
                             "for %s with current: %f and previous %f values."
                              % (observation, current_total, previous_total))

        return None

    def _update_data(self, fields, orig_name, orig_value, unit_system):
        value = self._convert_value(fields, orig_name, orig_value)
        fieldname = fields.get(orig_name, {}).get('name', orig_name)

        if orig_name in fields and 'units' in fields[orig_name]: # TODO - simplify, if possible
            (to_units, to_group) = weewx.units.getStandardUnitType(unit_system, fieldname) # match signature pylint: disable=unused-variable
            (value, new_units, new_group) = weewx.units.convert((value, fields[orig_name]['units'], None), to_units) # match signature pylint: disable=unused-variable

        if fields.get(orig_name, {}).get('contains_total', False):
            current_value = value
            value = self._calc_increment(orig_name, current_value, self.previous_values.get(orig_name))
            self.previous_values[orig_name] = current_value

        return fieldname, value

    def _log_message(self, msg):
        self.logger.debug("MessageCallbackProvider data-> incoming topic: %s, QOS: %i, retain: %s, payload: %s"
                          %(msg.topic, msg.qos, msg.retain, msg.payload))

    def _log_exception(self, method, exception, msg):
        self.logger.error("MessageCallbackProvider %s failed with: %s" %(method, exception))
        self.logger.error("**** MessageCallbackProvider Ignoring topic=%s and payload=%s" % (msg.topic, msg.payload))

    def _on_message_keyword(self, client, userdata, msg): # (match callback signature) pylint: disable=unused-argument
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self._log_message(msg)
            fields = self._get_fields(msg.topic)

            if PY2:
                payload_str = msg.payload
            else:
                payload_str = msg.payload.decode('utf-8')

            fielddata = payload_str.split(self.keyword_delimiter)
            data = {}
            unit_system = self.topic_manager.get_unit_system(msg.topic) # TODO - need public method
            for field in fielddata:
                eq_index = field.find(self.keyword_separator)
                # Ignore all fields that do not have the separator
                if eq_index == -1:
                    self.logger.error("MessageCallbackProvider on_message_keyword failed to find separator: %s"
                                      % self.keyword_separator)
                    self.logger.error("**** MessageCallbackProvider Skipping field=%s " % field)
                    continue

                key = field[:eq_index].strip()
                if not fields.get(key, {}).get('ignore', self.fields_ignore_default):
                    (fieldname, value) = self._update_data(fields, key, field[eq_index + 1:].strip(), unit_system)
                    data[fieldname] = value
                else:
                    self.logger.trace("MessageCallbackProvider on_message_keyword ignoring field: %s" % key)

            if data:
                self.topic_manager.append_data(msg.topic, data)
            else:
                self.logger.error("MessageCallbackProvider on_message_keyword failed to find data in: topic=%s and payload=%s"
                                  % (msg.topic, msg.payload))

        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_keyword', exception, msg)

    def _on_message_json(self, client, userdata, msg): # (match callback signature) pylint: disable=unused-argument
        # pylint: disable=too-many-locals
        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self._log_message(msg)
            fields = self._get_fields(msg.topic)

            if PY2:
                payload_str = msg.payload
                topic_str = msg.topic.encode('utf-8')
            else:
                payload_str = msg.payload.decode('utf-8')
                topic_str = msg.topic

            data = self._byteify(json.loads(payload_str, object_hook=self._byteify), ignore_dicts=True)

            data_flattened = self._flatten_dict(data, self.flatten_delimiter)

            unit_system = self.topic_manager.get_unit_system(msg.topic) # TODO - need public method
            data_final = {}
            # ToDo - if I have to loop, removes benefit of _bytefy, time to remove it?
            for key in data_flattened:
                if self.full_topic_fieldname:
                    lookup_key = topic_str + "/" + key # todo - cleanup and test unicode vs str stuff
                else:
                    lookup_key = key
                if not fields.get(lookup_key, {}).get('ignore', self.fields_ignore_default):
                    (fieldname, value) = self._update_data(fields, lookup_key, data_flattened[key], unit_system)
                    data_final[fieldname] = value
                else:
                    self.logger.trace("MessageCallbackProvider on_message_json ignoring field: %s" % lookup_key)

            if data_final:
                self.topic_manager.append_data(msg.topic, data_final)

        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_json', exception, msg)

    def _on_message_individual(self, client, userdata, msg): # (match callback signature) pylint: disable=unused-argument

        # Wrap all the processing in a try, so it doesn't crash and burn on any error
        try:
            self._log_message(msg)
            fields = self._get_fields(msg.topic)

            payload_str = msg.payload
            if not PY2:
                if msg.payload is not None:
                    payload_str = msg.payload.decode('utf-8')

            if self.full_topic_fieldname:
                key = msg.topic
            else:
                key = msg.topic.rpartition('/')[2]

            if PY2:
                key = key.encode('utf-8')

            unit_system = self.topic_manager.get_unit_system(msg.topic) # TODO - need public method
            if not fields.get(key, {}).get('ignore', self.fields_ignore_default):
                (fieldname, value) = self._update_data(fields, key, payload_str, unit_system)
                data = {}
                data[fieldname] = value
                self.topic_manager.append_data(msg.topic, data, fieldname)
            else:
                self.logger.trace("MessageCallbackProvider on_message_individual ignoring field: %s" % key)
        except Exception as exception: # (want to catch all) pylint: disable=broad-except
            self._log_exception('on_message_individual', exception, msg)

class MQTTSubscribe(object):
    """ Manage MQTT sunscriptions. """
    def __init__(self, service_dict, logger):
        # pylint: disable=too-many-locals, too-many-statements
        self.logger = logger
        self.logger.debug("service_dict is %s" % service_dict)

        if 'topic' in service_dict:
            self.logger.info("'topic' is deprecated, use '[[topics]]'")
        if 'overlap' in service_dict:
            self.logger.info("'overlap' is deprecated, use 'adjust_start_time'")
        if 'contains_total' in service_dict['message_callback']:
            self.logger.info("'contains_total' is deprecated use [[[fields]]] contains_total setting.")
        if 'label_map' in service_dict['message_callback']:
            self.logger.info("'label_map' is deprecated use [[[fields]]] name setting.")

        message_callback_config = service_dict.get('message_callback', None)
        if message_callback_config is None:
            raise ValueError("[[message_callback]] is required.")

        # For backwards compatibility
        overlap = to_float(service_dict.get('overlap', 0))
        self.logger.info("overlap is %s" % overlap)
        topics_dict = service_dict.get('topics', {})
        topics_dict['overlap'] = overlap

        message_callback_provider_name = service_dict.get('message_callback_provider',
                                                          'user.MQTTSubscribe.MessageCallbackProvider')
        self.manager = TopicManager(topics_dict, self.logger)

        self.record_cache = None
        if self.manager.managing_fields:
            self.record_cache = self.manager.record_cache

        clientid = service_dict.get('clientid',
                                    'MQTTSubscribe-' + str(random.randint(1000, 9999)))
        clean_session = to_bool(service_dict.get('clean_session', True))

        host = service_dict.get('host', 'localhost')
        keepalive = to_int(service_dict.get('keepalive', 60))
        port = to_int(service_dict.get('port', 1883))
        username = service_dict.get('username', None)
        password = service_dict.get('password', None)
        log_mqtt = to_bool(service_dict.get('log', False))

        self.archive_topic = service_dict.get('archive_topic', None)

        if self.archive_topic and self.archive_topic not in service_dict['topics']:
            raise ValueError("Archive topic %s must be in [[topics]]" % self.archive_topic)

        self.logger.info("message_callback_provider_name is %s" % message_callback_provider_name)
        self.logger.info("clientid is %s" % clientid)
        self.logger.info("client_session is %s" % clean_session)
        self.logger.info("host is %s" % host)
        self.logger.info("port is %s" % port)
        self.logger.info("keepalive is %s" % keepalive)
        self.logger.info("username is %s" % username)
        if password is not None:
            self.logger.info("password is set")
        else:
            self.logger.info("password is not set")
        self.logger.info("Archive topic is %s" % self.archive_topic)

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
        self.userdata['connect_flags'] = None
        self.client = mqtt.Client(client_id=clientid, userdata=self.userdata, clean_session=clean_session)

        if log_mqtt:
            self.client.on_log = self._on_log

        message_callback_provider_class = weeutil.weeutil._get_object(message_callback_provider_name) # pylint: disable=protected-access
        message_callback_provider = message_callback_provider_class(message_callback_config,
                                                                    self.logger,
                                                                    self.manager)

        self.client.on_message = message_callback_provider.get_callback()

        self.client.on_subscribe = self._on_subscribe

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        if username is not None and password is not None:
            self.client.username_pw_set(username, password)

        self.client.connect(host, port, keepalive)

    @property
    def subscribed_topics(self):
        """ The topics subscribed to. """
        return self.manager.subscribed_topics

    def get_data(self, topic, end_ts=MAXSIZE):
        """ Get data off the queue of MQTT data. """
        return self.manager.get_data(topic, end_ts)

    def get_accumulated_data(self, topic, start_ts, end_ts, units):
        """ Get the MQTT data after being accumulated. """
        return self.manager.get_accumulated_data(topic, start_ts, end_ts, units)

    def start(self):
        """ start subscribing to the topics """
        self.logger.debug("Starting loop")
        self.client.loop_start()

        while not self.userdata['connect']:
            time.sleep(1)

        if self.userdata['connect_rc'] > 0:
            raise weewx.WeeWxIOError("Unable to connect. Return code is %i flags are %s." % (self.userdata['rc'], self.userdata['flags']))

    def disconnect(self):
        """ shut it down """
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, rc): # (match callback signature) pylint: disable=unused-argument
        # https://pypi.org/project/paho-mqtt/#on-connect
        # rc:
        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorised
        # 6-255: Currently unused.
        self.logger.debug("Connected with result code %i" % rc)
        self.logger.debug("Connected flags %s" % str(flags))

        userdata['connect'] = True
        userdata['connect_rc'] = rc
        userdata['connect_flags'] = flags

        for topic in self.manager.subscribed_topics:
            (result, mid) = client.subscribe(topic, self.manager.get_qos(topic))
            self.logger.debug("Subscribed to %s has a mid %i and rc %i" %(topic, mid, result))

    def _on_disconnect(self, client, userdata, rc): # (match callback signature) pylint: disable=unused-argument
        self.logger.debug("Disconnected with result code %i" %rc)

    def _on_subscribe(self, client, userdata, mid, granted_qos): # (match callback signature) pylint: disable=unused-argument
        self.logger.debug("Subscribed to topic mid: %i is size %i has a QOS of %i"
                          %(mid, len(granted_qos), granted_qos[0]))

    def _on_log(self, client, userdata, level, msg): # (match callback signature) pylint: disable=unused-argument
        self.mqtt_logger[level]("MQTTSubscribe MQTT msg:", msg)

class MQTTSubscribeService(StdService):
    """ The MQTT subscribe service. """
    def __init__(self, engine, config_dict):
        super(MQTTSubscribeService, self).__init__(engine, config_dict)

        service_dict = config_dict.get('MQTTSubscribeService', {})
        logging_filename = service_dict.get('logging_filename', None)
        logging_level = service_dict.get('logging_level', 'NOTSET')
        console = to_bool(service_dict.get('console', False))
        self.logger = Logger('Service', level=logging_level, filename=logging_filename, console=console)
        self.logger.log_environment()
        self.logger.debug("service_dict is %s" % service_dict)

        self.enable = to_bool(service_dict.get('enable', True))
        if not self.enable:
            self.logger.info("Not enabled, exiting.")
            return

        if engine.stn_info.hardware == DRIVER_NAME:
            self.logger.info("Running as both a driver and a service.")

        self.binding = service_dict.get('binding', 'loop')

        if 'archive_topic' in service_dict:
            raise ValueError("archive_topic, %s, is invalid when running as a service" % service_dict['archive_topic'])

        self.end_ts = 0 # prime for processing loop packet

        self.subscriber = MQTTSubscribe(service_dict, self.logger)

        self.logger.info("binding is %s" % self.binding)

        archive_field_cache_dict = service_dict.get('archive_field_cache', None)
        self.cached_fields = {}
        if archive_field_cache_dict is not None:
            self.logger.info("'archive_field_cache' is deprecated, use '[[topics]][[[topic name]]][[[[fieldname]]]]'")
            if self.subscriber.record_cache is not None:
                self.logger.trace("Ignoring archive_field_cache configration and using topics/fields configuration.")
            unit_system_name = archive_field_cache_dict.get('unit_system', 'US').strip().upper()
            if unit_system_name not in weewx.units.unit_constants:
                raise ValueError("archive_field_cache: Unknown unit system: %s" % unit_system_name)
            unit_system = weewx.units.unit_constants[unit_system_name]

            fields_dict = archive_field_cache_dict.get('fields', {})
            for field in archive_field_cache_dict.get('fields', {}):
                self.cached_fields[field] = {}
                self.cached_fields[field]['expires_after'] = to_float(fields_dict[field].get('expires_after', None))

            self.cache = RecordCache(unit_system)

        self.logger.info("archive_field_cache_dict is %s" % archive_field_cache_dict)

        self.subscriber.start()

        if self.binding == 'archive':
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        elif self.binding == 'loop':
            self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
            if archive_field_cache_dict is not None:
                self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        else:
            raise ValueError("MQTTSubscribeService: Unknown binding: %s" % self.binding)

    def shutDown(self): # need to override parent - pylint: disable=invalid-name
        """Run when an engine shutdown is requested."""
        self.subscriber.disconnect()

    def new_loop_packet(self, event):
        """ Handle the new loop packet event. """
        # packet has traveled back in time
        if self.end_ts > event.packet['dateTime']:
            self.logger.error("Ignoring packet has dateTime of %f which is prior to previous packet %f"
                              %(event.packet['dateTime'], self.end_ts))
        else:
            start_ts = self.end_ts
            self.end_ts = event.packet['dateTime']

            for topic in self.subscriber.subscribed_topics: # topics might not be cached.. therefore use subscribed?
                self.logger.trace("Packet prior to update is: %s %s"
                                  % (weeutil.weeutil.timestamp_to_string(event.packet['dateTime']),
                                     to_sorted_string(event.packet)))
                target_data = self.subscriber.get_accumulated_data(topic,
                                                                   start_ts, self.end_ts, event.packet['usUnits'])
                event.packet.update(target_data)
                self.logger.trace("Packet after update is: %s %s"
                                  % (weeutil.weeutil.timestamp_to_string(event.packet['dateTime']),
                                     to_sorted_string(event.packet)))

            self.logger.debug("data-> final packet is %s: %s"
                              % (weeutil.weeutil.timestamp_to_string(event.packet['dateTime']),
                                 to_sorted_string(event.packet)))

    # this works for hardware generation, but software generation does not 'quality control'
    # the archive record, so this data is not 'QC' in this case.
    # If this is important, bind to the loop packet.
    def new_archive_record(self, event):
        """ Handle the new archive record event. """
        if self.binding == 'archive':
            end_ts = event.record['dateTime']
            start_ts = end_ts - event.record['interval'] * 60

            for topic in self.subscriber.subscribed_topics: # topics might not be cached.. therefore use subscribed?
                self.logger.trace("Record prior to update is: %s %s"
                                  % (weeutil.weeutil.timestamp_to_string(event.record['dateTime']),
                                     to_sorted_string(event.record)))
                target_data = self.subscriber.get_accumulated_data(topic, start_ts, end_ts, event.record['usUnits'])
                event.record.update(target_data)
                self.logger.trace("Record after update is: %s %s"
                                  % (weeutil.weeutil.timestamp_to_string(event.record['dateTime']),
                                     to_sorted_string(event.record)))


        if self.subscriber.record_cache is not None:
            cached_fields = self.subscriber.record_cache
        else:
            cached_fields = self.cached_fields

        target_data = {}
        for field in cached_fields:
            if field in event.record:
                timestamp = time.time()
                self.logger.trace("Update cache %s to %s with units of %i and timestamp of %i"
                                  % (event.record[field], field, event.record['usUnits'], timestamp))
                self.cache.update_value(field,
                                        event.record[field],
                                        event.record['usUnits'],
                                        timestamp)
            else:
                target_data[field] = self.cache.get_value(field,
                                                          time.time(),
                                                          cached_fields[field]['expires_after'])
                self.logger.trace("target_data after cache lookup is: %s"
                                  % to_sorted_string(target_data))

        event.record.update(target_data)
        self.logger.debug("data-> final record is %s: %s"
                          % (weeutil.weeutil.timestamp_to_string(event.record['dateTime']),
                             to_sorted_string(event.record)))

def loader(config_dict, engine): # (Need to match function signature) pylint: disable=unused-argument
    """ Load and return the driver. """
    return MQTTSubscribeDriver(**config_dict[DRIVER_NAME])

def confeditor_loader():
    """ Load and return the configuration editor. """
    return MQTTSubscribeDriverConfEditor()

class MQTTSubscribeDriver(weewx.drivers.AbstractDevice): # (methods not used) pylint: disable=abstract-method
    """weewx driver that reads data from MQTT"""

    def __init__(self, **stn_dict):
        console = to_bool(stn_dict.get('console', False))
        logging_filename = stn_dict.get('logging_filename', None)
        logging_level = stn_dict.get('logging_level', 'NOTSET')
        self.logger = Logger('Driver', level=logging_level, filename=logging_filename, console=console)
        self.logger.log_environment()
        self.logger.debug("stn_dict is %s" % stn_dict)

        self.wait_before_retry = float(stn_dict.get('wait_before_retry', 2))
        self._archive_interval = to_int(stn_dict.get('archive_interval', 300))
        self.archive_topic = stn_dict.get('archive_topic', None)

        self.subscriber = MQTTSubscribe(stn_dict, self.logger)

        self.logger.info("Wait before retry is %i" % self.wait_before_retry)
        self.subscriber.start()

    @property
    def hardware_name(self):
        """ The name of the hardware driver. """
        return "MQTTSubscribeDriver"

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

    def genLoopPackets(self): # need to override parent - pylint: disable=invalid-name
        """ Called to generate loop packets. """
        while True:
            for topic in self.subscriber.subscribed_topics: # topics might not be cached.. therefore use subscribed?
                if topic == self.archive_topic:
                    continue

                for data in self.subscriber.get_data(topic):
                    if data:
                        self.logger.debug("data-> final loop packet is %s %s: %s"
                                          % (topic, weeutil.weeutil.timestamp_to_string(data['dateTime']), to_sorted_string(data)))
                        yield data
                    else:
                        break

            self.logger.trace("Queues are empty.")

            time.sleep(self.wait_before_retry)

    def genArchiveRecords(self, lastgood_ts): # need to override parent - pylint: disable=invalid-name
        """ Called to generate the archive records. """
        if not self.archive_topic:
            self.logger.debug("No archive topic configured.")
            raise NotImplementedError

        for data in self.subscriber.get_data(self.archive_topic, lastgood_ts):
            if data:
                self.logger.debug("data-> final archive record is %s %s: %s"
                                  % (self.archive_topic, weeutil.weeutil.timestamp_to_string(data['dateTime']), to_sorted_string(data)))
                yield data
            else:
                break

class MQTTSubscribeDriverConfEditor(weewx.drivers.AbstractConfEditor): # pragma: no cover
    """ Methods for producing and updating configuration stanzas for use in configuration file. """
    @property
    def default_stanza(self):
        """ The default configuration stanza. """
        return """
[MQTTSubscribeDriver]
    # This section is for the MQTTSubscribe driver.

    # The driver to use:
    driver = user.MQTTSubscribe

    # The MQTT server.
    # Default is: localhost
    host = localhost

    # The port to connect to.
    # Default is: 1883
    port = 1883

    # Maximum period in seconds allowed between communications with the broker.
    # Default is: 60
    keepalive = 60

    # Configuration for the message callback.
    [[message_callback]]
        # The format of the MQTT payload.
        # Currently support: individual, json, keyword
        # Must be specified.
        type = REPLACE_ME

    # The topics to subscribe to.
    [[topics]]

        # Units for MQTT payloads without unit value.
        # Valid values: US, METRIC, METRICWX
        # Default is: US
        unit_system = US

        [[[FIRST/REPLACE_ME]]]
        [[[SECOND/REPLACE_ME]]]
"""
    def prompt_for_settings(self):
        """ Prompt for settings required for proper operation of this driver. """
        settings = {}
        settings['message_callback'] = {}
        settings['topics'] = {}

        print("Enter the host.")
        settings['host'] = self._prompt('host', 'localhost')

        print("Enter the port on the host.")
        settings['port'] = self._prompt('port', '1883')

        print("Enter the maximum period in seconds allowed between communications with the broker.")
        settings['keepalive'] = self._prompt('keepalive', '60')

        print("Enter the units for MQTT payloads without unit value: US|METRIC|METRICWX")
        settings['topics']['unit_system'] = self._prompt('unit_system', 'US', ['US', 'METRIC', 'METRICWX'])

        print("Enter a topic to subscribe to. ")
        topic = self._prompt('topic')
        while topic:
            settings['topics'][topic] = {}
            print("Enter a topic to subscribe to. Leave blank when done.")
            topic = self._prompt('topic')

        print("Enter the MQTT paylod type: individual|json|keyword")
        settings['message_callback']['type'] = self._prompt('type', 'json', ['individual', 'json', 'keyword'])

        return settings

# To Run
# setup.py install:
# PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/MQTTSubscribe.py
#
# rpm or deb package install:
# PYTHONPATH=/usr/share/weewx python /usr/share/weewx/user/MQTTSubscribe.py
if __name__ == '__main__': # pragma: no cover
    import argparse
    import os
    from weewx.engine import StdEngine # pylint: disable=ungrouped-imports
    try:
        from weeutil.config import merge_config
    except ImportError:
        from weecfg import merge_config # pre WeeWX 3.9

    USAGE = """MQTTSubscribeService --help
               CONFIG_FILE
               [--records=RECORD_COUNT]
               [--interval=INTERVAL]
               [--delay=DELAY]
               [--units=US|METRIC|METRICWX]
               [--binding=archive|loop]
               [--type=driver|service]
               [--verbose]
               [--console]

    CONFIG_FILE = The WeeWX configuration file, typically weewx.conf.
    """

    def main():
        # pylint: disable=too-many-locals, too-many-statements
        """ Prepare and run MQTTSubscribe in simulation mode. """
        parser = argparse.ArgumentParser(usage=USAGE)
        parser.add_argument('--version', action='version', version="MQTTSubscribe version is %s" % VERSION)
        parser.add_argument('--records', dest='record_count', type=int,
                            help='The number of archive records to create.',
                            default=2)
        parser.add_argument('--interval', dest='interval', type=int,
                            help='The archive interval in seconds.',
                            default=300)
        parser.add_argument('--delay', dest='delay', type=int,
                            help='The archive delay in seconds.',
                            default=15)
        parser.add_argument("--units", choices=["US", "METRIC", "METRICWX"],
                            help="The default units if not in MQTT payload.",
                            default="US")
        parser.add_argument("--binding", choices=["archive", "loop"],
                            help="The type of binding.",
                            default="archive")
        parser.add_argument("--type", choices=["driver", "service"],
                            help="The simulation type.",
                            default="driver")
        parser.add_argument("--verbose", action="store_true", dest="verbose",
                            help="Log extra output (debug=1).")
        parser.add_argument("--console", action="store_true", dest="console",
                            help="Log to console in addition to syslog.")
        parser.add_argument("--host",
                            help="The MQTT server.")
        parser.add_argument("--topics",
                            help="Comma separated list of topics to subscribe to.")
        parser.add_argument("--callback",
                            help="The callback type.")
        parser.add_argument("config_file")

        options = parser.parse_args()

        simulation_type = options.type
        binding = options.binding
        record_count = options.record_count
        interval = options.interval
        delay = options.delay
        units = weewx.units.unit_constants[options.units]

        config_path = os.path.abspath(options.config_file)

        config_dict = configobj.ConfigObj(config_path, file_error=True)

        setup_logging(options.verbose, config_dict)

        config_topics(config_dict, options.topics)

        config_host(config_dict, options.host)

        config_callback(config_dict, options.callback)

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

        print("Simulation is %s" % simulation_type)
        print("Creating %i %s records" % (record_count, binding))
        print("Interval is %i seconds" % interval)
        print("Delay is %i seconds" % delay)

        engine = StdEngine(min_config_dict)

        weewx.accum.initialize(config_dict)

        # override the configured binding with the parameter value
        merge_config(config_dict, {'MQTTSubscribeService': {'binding': binding}})

        config_console(config_dict, options.console)

        if simulation_type == "service":
            simulate_service(engine, config_dict, binding, record_count, interval, delay, units)
        elif simulation_type == "driver":
            driver = "user.MQTTSubscribe"
            __import__(driver)
            # This is a bit of Python wizardry. First, find the driver module
            # in sys.modules.
            driver_module = sys.modules[driver]
            # Find the function 'loader' within the module:
            loader_function = getattr(driver_module, 'loader')
            driver = loader_function(config_dict, engine)

            if binding == "archive":
                simulate_driver_archive(driver, record_count, interval, delay)
            elif binding == "loop":
                simulate_driver_packet(driver, record_count)

    def config_topics(config_dict, topic_option):
        """ Configure the topics. """
        if topic_option:
            topics = topic_option.split(',')
            if 'MQTTSubscribeService' in config_dict and 'topics' in config_dict['MQTTSubscribeService']:
                config_dict['MQTTSubscribeService']['topics'] = {}
            if 'MQTTSubscribeDriver' in config_dict and 'topics' in config_dict['MQTTSubscribeDriver']:
                config_dict['MQTTSubscribeDriver']['topics'] = {}
            for topic in topics:
                merge_config(config_dict, {'MQTTSubscribeService': {'topics': {topic:{}}}})
                merge_config(config_dict, {'MQTTSubscribeDriver': {'topics': {topic:{}}}})

    def config_host(config_dict, host_option):
        """ Configure the host. """
        if host_option:
            merge_config(config_dict, {'MQTTSubscribeService': {'host': host_option}})
            merge_config(config_dict, {'MQTTSubscribeDriver': {'host': host_option}})

    def config_callback(config_dict, callback_option):
        """ Configure the callback. """
        if callback_option:
            merge_config(config_dict, {'MQTTSubscribeService': {'message_callback': {'type': callback_option}}})
            merge_config(config_dict, {'MQTTSubscribeDriver': {'message_callback': {'type': callback_option}}})

    def config_console(config_dict, console_option):
        """ If specified, override the console logging. """
        if console_option:
            merge_config(config_dict, {'MQTTSubscribeService': {'console': True}})
            merge_config(config_dict, {'MQTTSubscribeDriver': {'console': True}})

    def simulate_driver_archive(driver, record_count, interval, delay):
        """ Simulate running MQTTSubscribe as a driver that generates archive records. """
        i = 0
        while i < record_count:
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval
            end_delay_ts = end_period_ts + delay
            sleep_amount = end_delay_ts - current_time
            print("Sleeping %i seconds" % sleep_amount)
            time.sleep(sleep_amount)

            for record in driver.genArchiveRecords(end_period_ts):
                print("Record is: %s %s"
                      % (weeutil.weeutil.timestamp_to_string(record['dateTime']), to_sorted_string(record)))

            i += 1

    def simulate_driver_packet(driver, record_count):
        """ Simulate running MQTTSubscribe as a driver that generates loop packets. """
        i = 0
        for packet in driver.genLoopPackets():
            print("Packet is: %s %s"
                  % (weeutil.weeutil.timestamp_to_string(packet['dateTime']),
                     to_sorted_string(packet)))
            i += 1
            if i >= record_count:
                break

    def simulate_service(engine, config_dict, binding, record_count, interval, delay, units):
        # pylint: disable=too-many-arguments, too-many-locals
        """ Simulate running MQTTSubscribe as a service. """
        service = MQTTSubscribeService(engine, config_dict)
        i = 0
        while i < record_count:
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval
            end_delay_ts = end_period_ts + delay
            sleep_amount = end_delay_ts - current_time

            print("Sleeping %i seconds" % sleep_amount)
            time.sleep(sleep_amount)

            data = {}
            data['dateTime'] = end_period_ts
            data['usUnits'] = units

            if binding == 'archive':
                data['interval'] = interval / 60
                new_archive_record_event = weewx.Event(weewx.NEW_ARCHIVE_RECORD,
                                                       record=data,
                                                       origin='hardware')
                engine.dispatchEvent(new_archive_record_event)
                print("Archive Record is: %s %s"
                      % (weeutil.weeutil.timestamp_to_string(new_archive_record_event.record['dateTime']),
                         to_sorted_string(new_archive_record_event.record)))
            elif binding == 'loop':
                new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET,
                                                    packet=data)
                engine.dispatchEvent(new_loop_packet_event)
                print("Loop packet is: %s %s"
                      % (weeutil.weeutil.timestamp_to_string(new_loop_packet_event.packet['dateTime']),
                         to_sorted_string(new_loop_packet_event.packet)))

            i += 1

        service.shutDown()

    main()
