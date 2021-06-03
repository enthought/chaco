# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from contextlib import contextmanager

import sys
import traceback


# ######### Testing tools


@contextmanager
def store_exceptions_on_all_threads():
    """Context manager that captures all exceptions, even those coming from
    the UI thread. On exit, the first exception is raised (if any).
    """

    exceptions = []

    def excepthook(type, value, tb):
        exceptions.append(value)
        message = "Uncaught exception:\n"
        message += "".join(traceback.format_exception(type, value, tb))
        sys.stderr.write(message)

    try:
        sys.excepthook = excepthook
        yield
    finally:
        if len(exceptions) > 0:
            raise exceptions[0]
        sys.excepthook = sys.__excepthook__
