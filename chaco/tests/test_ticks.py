from math import isinf
from numpy import int32, float32
import sys
import unittest
from chaco.ticks import auto_ticks

__author__ = 'Rustam Safin'


def get_near_inf_value():
    """
    :rtype: double
    :return: closest to infinity float value
    """
    return sys.float_info.max


class TestTicks(unittest.TestCase):
    def testIsInf(self):
        # assert does not throw TypeError
        isinf(10)
        isinf(10.0)
        isinf(int32(100))
        isinf(float32(100))
        self.assertTrue(isinf(float32('inf')))

    def testAutoTicksOnInfinity(self):
        inf = float("inf")
        self.assertEquals([], auto_ticks(inf, 10, 'fit', 'fit', 1, True))
        self.assertEquals([], auto_ticks(0, inf, 'fit', 'fit', 1, True))
        self.assertEquals([], auto_ticks(0, 10, 'fit', 'fit', inf, True))

    def testTicksWithIntegers(self):
        self.assertEquals(range(11), auto_ticks(0, 10, 0, 10, 1, True))

    def testTicksOverFlow(self):
        bottom = 0
        top = get_near_inf_value()
        print("Bottom: {0} Top: {1}".format(bottom, top))

        # Can raise ValueError
        #
        # Traceback (most recent call last):
        # File "ets/chaco/chaco/tests/test_ticks.py", line 30, in testTicksOverFlow
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
