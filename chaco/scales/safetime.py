""" This module wraps the standard library time module to gracefully
handle bad input values for time.
"""

import warnings
import time as stdlib_time
# Yup, we're exposing everything from time.
from time import *
from datetime import datetime, timedelta, MINYEAR, MAXYEAR

__all__ = ([x for x in dir(stdlib_time) if not x.startswith('_')]
    + ['safe_fromtimestamp', 'datetime', 'timedelta', 'MINYEAR', 'MAXYEAR',
        'EPOCH'])


# On Windows 10, datetime.fromtimestamp fails with an OSError for timestamps
# less than 86400s (1 day). We work around this by initializing the epoch to
# some time past that, and then going back that many seconds to arrive at "time
# 0". See the discussion in GH #376 (as well as Python issue 29097).
DAY_SECONDS = 24 * 60 * 60
EPOCH = datetime.fromtimestamp(DAY_SECONDS) - timedelta(seconds=DAY_SECONDS)


# Can't monkeypatch methods of anything in datetime, so we have to wrap them
def safe_fromtimestamp(timestamp, *args, **kwds):
    """ safe_fromtimestamp(timestamp) -> UTC time from POSIX timestamp.

    Timestamps outside of the valid range will be assigned datetime objects of
    Jan 1 of either MINYEAR or MAXYEAR, whichever appears closest.

    WARNING: This function does not behave properly with Daylight Savings Time,
    due to a documented issue with datetime arithmetic.
    """
    try:
        return EPOCH + timedelta(seconds=timestamp)
    except (ValueError, OverflowError) as e:
        warnings.warn("Timestamp out of range.  Returning safe default value.")
        if timestamp <= 0:
            return datetime(MINYEAR, 1, 1, 0, 0, 0)
        else:
            return datetime(MAXYEAR, 1, 1, 0, 0, 0)

def mktime(t):
    """ mktime(tuple) -> floating point number

    Convert a time tuple in local time to seconds since the Epoch. Invalid time
    tuples will be assigned the value 0.0 and a warning will be issued.
    """
    try:
        return stdlib_time.mktime(t)
    except (ValueError, OverflowError):
        warnings.warn("Bad time for mktime().  Returning 0.")
        # mktime() returns a float
        return 0.0

def doy(dt):
    """ Find the day of year of the datetime.

    The returned DoY is in the range [1-366].
    """
    date = dt.date()
    jan01 = date.replace(month=1, day=1)
    doy = (date - jan01).days + 1
    return doy

struct_time = type(stdlib_time.localtime())

def localtime(t=None):
    """
    localtime([seconds]) -> (tm_year,tm_mon,tm_day,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst)

    Convert seconds since the Epoch to a time tuple expressing local time.
    When 'seconds' is not passed in, convert the current time instead.

    Modified to accept timestamps before the Epoch.
    """
    if t is None:
        dt = datetime.now()
    else:
        dt = safe_fromtimestamp(t)
    timetuple = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
        dt.weekday(), doy(dt), -1)
    return struct_time(timetuple)

