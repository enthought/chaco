from math import isinf
import unittest
from chaco.ticks import auto_ticks

__author__ = 'Rustam Safin'


def get_near_inf_value():
    x = 1e300
    prev_x = x
    increment = 1024
    while increment > 1:
        prev_x = x

        if isinf(x * increment):
            increment = increment / 2
        else:
            x *= increment

    return prev_x


class TestTicks(unittest.TestCase):

    def testAutoTicksOnInfinity(self):
        inf = 1e308 * 1e308
        self.assertEquals([], auto_ticks(inf, 10, 'fit', 'fit', 1, True))
        self.assertEquals([], auto_ticks(0, inf, 'fit', 'fit', 1, True))
        self.assertEquals([], auto_ticks(0, 10, 'fit', 'fit', inf, True))

    def testTicksOverFlow(self):
        bottom = 0
        top = get_near_inf_value()
        print("Bottom: {0} Top: {1}".format(bottom, top))

        # Can raise ValueError
        #
        # Traceback (most recent call last):
        #   File "ets/chaco/chaco/tests/test_ticks.py", line 30, in testTicksOverFlow
        #     ticks = auto_ticks(bottom, top, bottom, top, 100, True)
        #   File "ets/chaco/chaco/ticks.py", line 213, in auto_ticks
        #     ticks = arange( start, end + (tick_interval / 2.0), tick_interval )
        # ValueError: Maximum allowed size exceeded

        ticks = auto_ticks(bottom, top, bottom, top, 100, True)
        self.assertEqual(ticks, [])

        bottom = 1e300
        top = get_near_inf_value()
        tick_interval = (top - bottom)
        print("Bottom: {0} Top: {1} Interval: {2}".format(bottom, top, tick_interval))

        # Can raise RuntimeWarning:
        # ets/chaco/chaco/ticks.py: RuntimeWarning: invalid value encountered in double_scalars
        # start = floor( lower / tick_interval ) * tick_interval
        # ets/chaco/chaco/ticks.py: RuntimeWarning: invalid value encountered in double_scalars
        # end   = floor( upper / tick_interval ) * tick_interval

        ticks = auto_ticks(bottom, top, bottom, top, tick_interval, True)
        self.assertEqual(ticks, [])
