# pylint: disable=import-outside-toplevel
# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# need to be python 2 compatible pylint: disable=bad-option-value, raise-missing-from
# pylint: enable=bad-option-value
from __future__ import print_function

import locale
import random
import string
import sys
import time

def random_string(length=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)]) # pylint: disable=unused-variable

class weeutil(object):
    class config(object):
        def merge_config(self):
            pass
    class logger(object):
        pass

    try:
        # Python 3
        from collections import ChainMap

        class ListOfDicts(ChainMap):
            # pylint: disable=too-many-ancestors
            def extend(self, m):
                self.maps.append(m)
            def prepend(self, m):
                self.maps.insert(0, m)

    except ImportError:

        # Python 2. We'll have to supply our own
        class ListOfDicts(object):
            """A near clone of ChainMap"""

            def __init__(self, *maps):
                self.maps = list(maps) or [{}]

            def __missing__(self, key):
                raise KeyError(key)

            def __getitem__(self, key):
                for mapping in self.maps:
                    try:
                        return mapping[key]
                    except KeyError:
                        pass
                return self.__missing__(key)

            def get(self, key, default=None):
                return self[key] if key in self else default

            def __len__(self):
                return len(set().union(*self.maps))

            def __iter__(self):
                return iter(set().union(*self.maps))

            def __contains__(self, key):
                return any(key in m for m in self.maps)

            def __bool__(self):
                return any(self.maps)

            def __setitem__(self, key, value):
                """Set a key, value on the first map. """
                self.maps[0][key] = value

            def __delitem__(self, key):
                try:
                    del self.maps[0][key]
                except KeyError:
                    raise KeyError('Key not found in the first mapping: {!r}'.format(key))

            def popitem(self):
                'Remove and return an item pair from maps[0]. Raise KeyError is maps[0] is empty.'
                try:
                    return self.maps[0].popitem()
                except KeyError:
                    raise KeyError('No keys found in the first mapping.')

            def pop(self, key, *args):
                'Remove *key* from maps[0] and return its value. Raise KeyError if *key* not in maps[0].'
                try:
                    return self.maps[0].pop(key, *args)
                except KeyError:
                    raise KeyError('Key not found in the first mapping: {!r}'.format(key))

            def extend(self, m):
                self.maps.append(m)

            def prepend(self, m):
                self.maps.insert(0, m)
    class weeutil(object):
        class TimeSpan(tuple):
            """Represents a time span, exclusive on the left, inclusive on the right."""

            def __new__(cls, *args):
                if args[0] > args[1]:
                    raise ValueError("start time (%d) is greater than stop time (%d)" % (args[0], args[1]))
                return tuple.__new__(cls, args)

        @staticmethod
        def timestamp_to_string(ts, format_str="%Y-%m-%d %H:%M:%S %Z"):
            # pylint: disable=no-else-return
            if ts is not None:
                return "%s (%d)" % (time.strftime(format_str, time.localtime(ts)), ts)
            else:
                return "******* N/A *******     (    N/A   )"

        @staticmethod
        def _get_object(module_class):
            """Given a string with a module class name, it imports and returns the class."""
            # Split the path into its parts
            parts = module_class.split('.')
            # Strip off the classname:
            module = '.'.join(parts[:-1])
            # Import the top level module
            mod = __import__(module)
            # Recursively work down from the top level module to the class name.
            # Be prepared to catch an exception if something cannot be found.
            try:
                for part in parts[1:]:
                    mod = getattr(mod, part)
            except AttributeError:
                # Can't find something. Give a more informative error message:
                raise AttributeError(
                    "Module '%s' has no attribute '%s' when searching for '%s'" % (mod.__name__, part, module_class))
            return mod

        @staticmethod
        def option_as_list(option):
            if option is None:
                return None
            return [option] if not isinstance(option, list) else option

        @staticmethod
        def to_sorted_string(rec):
            return ", ".join(["%s: %s" % (k, rec.get(k)) for k in sorted(rec, key=locale.strxfrm)])

        @staticmethod
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
            raise ValueError("Unknown boolean specifier: '%s'." % value)

        @staticmethod
        def to_float(value):
            if isinstance(value, str) and value.lower() == 'none':
                value = None
            return float(value) if value is not None else None

        @staticmethod
        def to_int(value):
            return int(value)

        @staticmethod
        def startOfInterval(time_ts, interval):
            start_interval_ts = int(time_ts / interval) * interval

            if time_ts == start_interval_ts:
                start_interval_ts -= interval
            return start_interval_ts

class weewx(object): # pylint: disable=invalid-name
    __version__ = "unknown"
    debug = 2

    class WeeWxIOError(IOError):
        """Base class of exceptions thrown when encountering an input/output error
        with the hardware."""

    class units(object):
        METRIC = 0x10
        METRICWX = 0x11
        US = 0x01

        USUnits = weeutil.ListOfDicts({})

        MetricUnits = weeutil.ListOfDicts({})

        MetricWXUnits = weeutil.ListOfDicts({})

        default_unit_format_dict = {}

        default_unit_label_dict = {}

        conversionDict = {}
        conversionDict['unit_name'] = {'foobar': lambda x: x / 1}

        unit_constants = {
            'US'       : US,
            'METRIC'   : METRIC,
            'METRICWX' : METRICWX
        }

        obs_group_dict = weeutil.ListOfDicts({'barfoo' : {}})

        def to_std_system(self):
            pass

    class accum(object):
        def Accum(self):
            pass

        class OutOfSpan(ValueError):
            """Raised when attempting to add a record outside of the timespan held by an acumulator"""

    class NEW_LOOP_PACKET(object):
        """Event issued when a new LOOP packet is available. The event contains
        attribute 'packet', which is the new LOOP packet."""

    class NEW_ARCHIVE_RECORD(object):
        """Event issued when a new archive record is available. The event contains
        attribute 'record', which is the new archive record."""

    class engine(object):
        class StdEngine:
            pass
        class StdService(object):
            def __init__(self, engine, config_dict):
                pass
            def bind(self, p1, p2):
                pass
    class drivers(object): # pylint: disable=invalid-name
        class AbstractDevice(object):
            pass
        class AbstractConfEditor(object):
            pass


UNITS_CONSTANTS = {'US': 1}

class NEW_LOOP_PACKET(object):
    """Event issued when a new LOOP packet is available. The event contains
    attribute 'packet', which is the new LOOP packet."""
class NEW_ARCHIVE_RECORD(object):
    """Event issued when a new archive record is available. The event contains
    attribute 'record', which is the new archive record."""

class Event(object):
    """Represents an event."""
    def __init__(self, event_type, **argv):
        self.event_type = event_type

        for key in argv:
            setattr(self, key, argv[key])

    def __str__(self):
        """Return a string with a reasonable representation of the event."""
        et = "Event type: %s | " % self.event_type
        s = "; ".join("%s: %s" %(k, self.__dict__[k]) for k in self.__dict__ if k != "event_type")
        return et + s

try:
    import logging

    class Logger(object):
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

    class Logger(object):
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
            syslog.syslog(dst, '%s: %s' % (__name__, msg))
            if self.console:
                print('%s: %s' % (__name__, msg))


sys.modules['weewx'] = weewx
sys.modules['weewx.drivers'] = weewx.drivers
sys.modules['weewx.engine'] = weewx.engine
sys.modules['weeutil'] = weeutil
sys.modules['weeutil.config'] = weeutil.config
sys.modules['weeutil.weeutil'] = weeutil.weeutil
sys.modules['weeutil.logger'] = weeutil.logger
