# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from chaco.scales.formatters import strftimeEx, TimeFormatter


# ----------------------------------------------------------------
# strftimeEx tests
# ----------------------------------------------------------------


class TestStrftimeEx(unittest.TestCase):
    def test_strftimeEx_01(self):
        t = 0.123
        fmt = "%(ms)"
        result = strftimeEx(fmt, t)
        self.assertEqual(result, "123")

    def test_strftimeEx_02(self):
        t = 0.123456
        fmt = "%(us)"
        result = strftimeEx(fmt, t)
        self.assertEqual(result, "456")

    def test_strftimeEx_03(self):
        t = 0.678910
        fmt = "%(ms)"
        # According to the code, the number that replaces (ms) is *rounded*,
        # so this formt should give "679".
        result = strftimeEx(fmt, t)
        self.assertEqual(result, "679")

    def test_strftimeEx_04(self):
        t = 0.678910
        fmt = "%(ms).%(us)ms"
        # According to the code, the number that replaces (ms) is *rounded*,
        # so this formt should give "679.910ms".  (See the next test case for the
        # correct way to do this.)
        result = strftimeEx(fmt, t)
        expected = "679.910ms"
        self.assertEqual(result, expected)

    def test_strftimeEx_04(self):
        t = 0.678910
        fmt = "%(ms_).%(us)ms"
        # The format "%(ms_)" uses floor().
        result = strftimeEx(fmt, t)
        expected = "678.910ms"
        self.assertEqual(result, expected)

    def test_strftimeEx_05(self):
        # Test rounding that affects the seconds.
        t = 7.9999999
        fmt = "%S %(ms_) %(us)"
        result = strftimeEx(fmt, t)
        expected = "08 000 000"
        self.assertEqual(result, expected)

    def test_strftimeEx_06(self):
        # Test rounding that affects the seconds.
        t = 7.9996
        fmt = "%S %(ms)"
        result = strftimeEx(fmt, t)
        expected = "08 000"
        self.assertEqual(result, expected)

    def test_strftimeEx_07(self):
        # Test rounding that affects the seconds.
        t = 7.9996
        fmt = "%S %(ms_)"
        result = strftimeEx(fmt, t)
        expected = "07 999"
        self.assertEqual(result, expected)


# ----------------------------------------------------------------
# TimeFormatter tests
# ----------------------------------------------------------------


class TestTimeFormatter(unittest.TestCase):
    def test_time_formatter_01(self):
        tf = TimeFormatter()
        ticks = [10.005, 10.0053, 10.0056]
        labels = tf.format(ticks, char_width=130)
        expected = ["5.000ms", "5.300ms", "5.600ms"]
        self.assertEqual(labels, expected)
