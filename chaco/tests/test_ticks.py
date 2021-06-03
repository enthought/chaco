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

from chaco.ticks import DefaultTickGenerator, MinorTickGenerator, auto_interval


class TestDefaultTickGenerator(unittest.TestCase):
    def setUp(self):
        self.tick_generator = DefaultTickGenerator()

    def test_default_tick_generator(self):

        high = 1.0
        low = 0.0
        interval = 0.1
        ticks = self.tick_generator.get_ticks(
            data_low=0,
            data_high=1,
            bounds_low=low,
            bounds_high=high,
            interval=interval,
        )
        expected_num_ticks = (high - low) / interval + 1
        self.assertEqual(len(ticks), expected_num_ticks)


class TestMinorTickGenerator(unittest.TestCase):
    def setUp(self):
        self.tick_generator = MinorTickGenerator()

    def test_minor_tick_generator_with_interval(self):
        """If the MinorTickGenerator is not given an interval of 'auto',
        it should return the same results as a DefaultTickGenerator
        """
        self.default_tick_generator = DefaultTickGenerator()

        high = 1.0
        low = 0.0

        intervals = [0.05, 0.1, 0.2, 0.25, 0.5]

        for i in intervals:
            ticksMinor = self.tick_generator.get_ticks(
                data_low=0,
                data_high=1,
                bounds_low=low,
                bounds_high=high,
                interval=i,
            )
            ticksDefault = self.default_tick_generator.get_ticks(
                data_low=0,
                data_high=1,
                bounds_low=low,
                bounds_high=high,
                interval=i,
            )
            self.assertEqual(ticksMinor.tolist(), ticksDefault.tolist())

    def test_minor_tick_generator_without_interval(self):
        """A minor tick generator should return more ticks than
        the default tick generator.
        """
        self.default_tick_generator = DefaultTickGenerator()

        high = 1.0
        low = 0.0

        ticksMinor = self.tick_generator.get_ticks(
            data_low=0,
            data_high=1,
            bounds_low=low,
            bounds_high=high,
            interval="auto",
        )
        ticksDefault = self.default_tick_generator.get_ticks(
            data_low=0,
            data_high=1,
            bounds_low=low,
            bounds_high=high,
            interval="auto",
        )

        self.assertGreater(len(ticksMinor), len(ticksDefault))


class TestAutoInterval(unittest.TestCase):
    def test_default_auto_interval(self):
        """test default interval computation range orders of magnitude

        By default, the interval tries to pick eye-friendly intervals so that
        there are between 2 and 8 tick marks.
        """
        data_low = 0.0
        for i in range(30):
            data_high = 10.0 ** (i / 10.0)
            interval = auto_interval(data_low=data_low, data_high=data_high)
            num_ticks = int((data_high - data_low) / interval)
            self.assertGreaterEqual(num_ticks, 3)
            self.assertLessEqual(num_ticks, 8)

    def test_auto_interval_max_ticks(self):
        data_low = 0.0
        data_high = 100.0
        for max_ticks in range(4, 11):
            interval = auto_interval(
                data_low=data_low, data_high=data_high, max_ticks=max_ticks
            )
            num_ticks = int((data_high - data_low) / interval)
            self.assertGreaterEqual(num_ticks, 3)
            self.assertLessEqual(num_ticks, max_ticks)
