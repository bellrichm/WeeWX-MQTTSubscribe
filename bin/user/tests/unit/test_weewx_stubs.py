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
sys.modules['weeutil'].weeutil.startOfInterval = startOfInterval
sys.modules['weeutil.weeutil'].to_bool = to_bool
sys.modules['weeutil.weeutil'].to_float = to_float
sys.modules['weeutil.weeutil'].to_int = to_int
sys.modules['weeutil.weeutil'].timestamp_to_string = timestamp_to_string
sys.modules['weeutil.weeutil'].to_sorted_string = to_sorted_string
sys.modules['weeutil'].weeutil.option_as_list = option_as_list
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
