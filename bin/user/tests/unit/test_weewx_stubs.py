#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods

import locale
import random
import string
import sys
import time

from collections import ChainMap

import mock

def random_string(length=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)]) # pylint: disable=unused-variable

def random_ascii_letters(length=32):
    return''.join([random.choice(string.ascii_letters) for n in range(length)]) # pylint: disable=unused-variable

class ListOfDicts(ChainMap):
    # pylint: disable=too-many-ancestors
    def extend(self, m):
        self.maps.append(m)
    def prepend(self, m):
        self.maps.insert(0, m)

UNITS_CONSTANTS = {'US': 1}

class NEW_LOOP_PACKET:
    """Event issued when a new LOOP packet is available. The event contains
    attribute 'packet', which is the new LOOP packet."""
class NEW_ARCHIVE_RECORD:
    """Event issued when a new archive record is available. The event contains
    attribute 'record', which is the new archive record."""

class Event:
    """Represents an event."""
    def __init__(self, event_type, **argv):
        self.packet = None
        self.record = None

        self.event_type = event_type

        for key, value in argv.items():
            setattr(self, key, value)

    def __str__(self):
        """Return a string with a reasonable representation of the event."""
        et = f"Event type: {self.event_type} | "
        s = "; ".join(f"{k}: {v}" for k,v in self.__dict__.items() if k != "event_type")
        return et + s

try:
    import logging

    class Logger:
        """ The logging class. """
        def __init__(self, console=None):
            self._logmsg = logging.getLogger(__name__)
            if console:
                self._logmsg.addHandler(logging.StreamHandler(sys.stdout))

        def trace(self, msg):
            """ Log trace messages. """
            self._logmsg.debug(msg)

        def debug(self, msg):
            """ Log debug messages. """
            self._logmsg.debug(msg)

        def info(self, msg):
            """ Log informational messages. """
            self._logmsg.info(msg)

        def error(self, msg):
            """ Log error messages. """
            self._logmsg.error(msg)
except ImportError: # pragma: no cover
    import syslog

    class Logger:
        """ The logging class. """
        def __init__(self, console=None):
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_ERR))
            self.console = console

        def trace(self, msg):
            """ Log trace messages. """
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
            syslog.syslog(dst, f'{__name__}: {msg}')
            if self.console:
                print(f'{__name__}: {msg}')

class TimeSpan(tuple):
    """Represents a time span, exclusive on the left, inclusive on the right."""

    def __new__(cls, *args):
        if args[0] > args[1]:
            raise ValueError(f"start time ({int(args[0])}) is greater than stop time ({int(args[1])})")
        return tuple.__new__(cls, args)

def to_bool(value):
    # pylint: disable=no-else-return
    try:
        if value.lower() in ['true', 'yes']:
            return True
        elif value.lower() in ['false', 'no']:
            return False
    except AttributeError:
        pass
    try:
        return bool(int(value))
    except (ValueError, TypeError):
        pass
    raise ValueError(f"Unknown boolean specifier: '{value}'.")

def to_float(value):
    if isinstance(value, str) and value.lower() == 'none':
        value = None
    return float(value) if value is not None else None

def to_int(value):
    return int(value)

def timestamp_to_string(ts, format_str="%Y-%m-%d %H:%M:%S %Z"):
    # pylint: disable=no-else-return
    if ts is not None:
        return f"{time.strftime(format_str, time.localtime(ts))} ({int(ts)})"
    else:
        return "******* N/A *******     (    N/A   )"

def startOfInterval(time_ts, interval):
    start_interval_ts = int(time_ts / interval) * interval

    if time_ts == start_interval_ts:
        start_interval_ts -= interval
    return start_interval_ts

def to_sorted_string(rec):
    return ", ".join([f"{k}: {rec.get(k)}" for k in sorted(rec, key=locale.strxfrm)])

def option_as_list(option):
    if option is None:
        return None
    return [option] if not isinstance(option, list) else option

sys.modules['weecfg'] = mock.MagicMock()
sys.modules['weeutil'] = mock.MagicMock
sys.modules['weeutil.config'] = mock.MagicMock()
sys.modules['weeutil'].config = mock.MagicMock()

sys.modules['weeutil'].weeutil = mock.MagicMock()

sys.modules['weeutil.weeutil'] = mock.MagicMock()
sys.modules['weeutil.weeutil'].TimeSpan = TimeSpan
sys.modules['weeutil'].weeutil.TimeSpan = TimeSpan
sys.modules['weeutil'].weeutil.startOfInterval = lambda ts, interval: startOfInterval(ts, interval)
sys.modules['weeutil.weeutil'].to_bool = lambda val: to_bool(val)
sys.modules['weeutil.weeutil'].to_float = lambda val: to_float(val)
sys.modules['weeutil.weeutil'].to_int = lambda val: to_int(val)
sys.modules['weeutil.weeutil'].timestamp_to_string = lambda ts, fmt: timestamp_to_string(ts, fmt)
sys.modules['weeutil.weeutil'].to_sorted_string = lambda rec: to_sorted_string(rec)
sys.modules['weeutil'].weeutil.option_as_list = lambda opt: option_as_list(opt)
sys.modules['weeutil.logger'] = mock.MagicMock()

class units:
    METRIC = 0x10
    METRICWX = 0x11
    US = 0x01

    USUnits = ListOfDicts({})

    MetricUnits = ListOfDicts({})

    MetricWXUnits = ListOfDicts({})

    default_unit_format_dict = {}

    default_unit_label_dict = {}

    conversionDict = {}
    conversionDict['unit_name'] = {'foobar': lambda x: x / 1}

    unit_constants = {
        'US'       : US,
        'METRIC'   : METRIC,
        'METRICWX' : METRICWX
    }

    obs_group_dict = ListOfDicts({
        'barfoo' : {},
        'subfield1': {}
    })

    def to_std_system(self):
        pass

class accum:
    def Accum(self):
        pass

    class OutOfSpan(ValueError):
        """Raised when attempting to add a record outside of the timespan held by an acumulator"""

class WeeWxIOError(IOError):
    """Base class of exceptions thrown when encountering an input/output error
    with the hardware."""

class engine:
    class StdEngine:
        pass
    class StdService:
        def __init__(self, eng, config_dict):
            pass
        def bind(self, p1, p2):
            pass
class drivers: # pylint: disable=invalid-name
    class AbstractDevice:
        pass
    class AbstractConfEditor:
        pass

sys.modules['weewx'] = mock.MagicMock()
sys.modules['weewx'].drivers = drivers
sys.modules['weewx.drivers'] = mock.MagicMock()
sys.modules['weewx.engine'] = engine

sys.modules['weewx'].units = units
sys.modules['weewx'].accum = accum
sys.modules['weewx'].WeeWxIOError = WeeWxIOError
sys.modules['weewx'].__version__ = "unknown"
sys.modules['weewx'].debug = 2
