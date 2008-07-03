""" This module wraps the standard library time module to gracefully
handle bad input values for time.
"""

import warnings
import time as stdlib_time
# Yup, we're exposing everything from time.
from time import *
from datetime import datetime, timedelta, MINYEAR, MAXYEAR

__all__ = ([x for x in dir(stdlib_time) if not x.startswith('_')]
    + ['safe_fromtimestamp', 'datetime', 'timedelta', 'MINYEAR', 'MAXYEAR'])

# Can't monkeypatch methods of anything in datetime, so we have to wrap them
def safe_fromtimestamp(timestamp, *args, **kwds):
    """ safe_fromtimestamp(timestamp[, tz]) -> tz's local time from POSIX timestamp.

    Timestamps outside of the valid range will be assigned datetime objects of
    Jan 1 of either MINYEAR or MAXYEAR, whichever appears closest.
    """    
    try:
        return datetime.fromtimestamp(timestamp, *args, **kwds)
    except (ValueError, OverflowError):
        warnings.warn("Bad timestamp: %s" % str(timestamp) + ".  Returning safe default value.")
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
        warnings.warn("Bad time for mktime(): %s" % str(t) + ".  Returning 0.")
        # mktime() returns a float
        return 0.0


