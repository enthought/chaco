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
from numpy import array, nan
from numpy.testing import assert_array_almost_equal, assert_equal

from chaco.api import ArrayDataSource, DataRange1D, LogMapper


class LogMapperTestCase(unittest.TestCase):
    def test_basic(self):
        ary = array([1.0, 10.0, 100.0, 1000.0, 10000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=50, high_pos=90)
        result = mapper.map_screen(ary)
        assert_equal(result, array([50, 60, 70, 80, 90]))

    def test_reversed(self):
        ary = array([1.0, 10.0, 100.0, 1000.0, 10000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=100, high_pos=0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([100, 75, 50, 25, 0]))

    def test_fractional(self):
        ary = array([0.0001, 0.001, 0.01])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=20)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 10, 20])

    def test_zero(self):
        ary = array([0.0, 1.0, 10.0, 100.0, 1000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=30)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 0, 10, 20, 30])

    def test_negative(self):
        ary = array([1.0, -1.0, -2.0, 10.0, 100.0, 1000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=30)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 0, 0, 10, 20, 30])

    def test_fill_value(self):
        ary = array([1.0, -1.0, -2.0, 10.0, 100.0, 1000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=30)
        # This causes out-of-bounds values to be treated as the value 100.0
        mapper.fill_value = 100.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 20, 20, 10, 20, 30])

    def test_nan(self):
        ary = array([1.0, nan, 10.0, nan, 100.0, 1000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=30)
        mapper.fill_value = 100.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 20, 10, 20, 20, 30])
