""" This module wraps the standard library time module to gracefully
handle bad input values for time.
"""

import warnings
import time as stdlib_time
from time import *
from datetime import datetime, timedelta, MINYEAR, MAXYEAR


# Can't monkeypatch methods of anything in datetime, so we have to wrap them
def safe_fromtimestamp(timestamp):
    try:
        return datetime.fromtimestamp(timestamp)
    except (ValueError, OverflowError):
        warnings.warn("Bad timestamp: %s" % str(timestamp) + ".  Returning safe default value.")
        if timestamp <= 0:
            return datetime(MINYEAR, 1, 1, 0, 0, 0)
        else:
            return datetime(MAXYEAR, 1, 1, 0, 0, 0)

def mktime(t):
    try:
        return stdlib_time.mktime(t)
    except (ValueError, OverflowError):
        warnings.warn("Bad time for mktime(): %s" % str(t) + ".  Returning 0.")
        # mktime() returns a float
        return 0.0


