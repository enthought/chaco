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


@contextmanager
def assert_raises(ExceptionClass):
    try:
        yield
    except ExceptionClass:
        pass
    else:
        msg = "Test should have failed with {}."
        raise Exception(msg.format(ExceptionClass.__name__))
