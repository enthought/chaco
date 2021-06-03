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
from numpy import array, ndarray
from numpy.testing import assert_array_almost_equal, assert_equal


from chaco.api import ArrayDataSource, DataRange1D, LinearMapper


class LinearMapperTestCase(unittest.TestCase):
    def test_basic(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r)
        self.assertFalse(mapper._low_bound_initialized)
        self.assertFalse(mapper._high_bound_initialized)
        mapper.low_pos = 50
        self.assertTrue(mapper._low_bound_initialized)
        mapper.high_pos = 100
        self.assertTrue(mapper._high_bound_initialized)
        result = mapper.map_screen(ary)
        assert_equal(result, array([50, 60, 70, 80, 90, 100]))

    def test_reversed(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r)
        self.assertFalse(mapper._low_bound_initialized)
        self.assertFalse(mapper._high_bound_initialized)
        mapper.low_pos = 100
        self.assertTrue(mapper._low_bound_initialized)
        mapper.high_pos = 0
        self.assertTrue(mapper._high_bound_initialized)
        result = mapper.map_screen(ary)
        assert_equal(result, array([100, 80, 60, 40, 20, 0]))

    def test_set_screen_bounds(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r)
        self.assertFalse(mapper._low_bound_initialized)
        self.assertFalse(mapper._high_bound_initialized)
        mapper.screen_bounds = (50.0, 100.0)
        self.assertTrue(mapper._low_bound_initialized)
        self.assertTrue(mapper._high_bound_initialized)
        result = mapper.map_screen(ary)
        assert_equal(result, array([50, 60, 70, 80, 90, 100]))

    def test_reversed_set_screen_bounds(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r)
        self.assertFalse(mapper._low_bound_initialized)
        self.assertFalse(mapper._high_bound_initialized)
        mapper.screen_bounds = (100.0, 0.0)
        self.assertTrue(mapper._low_bound_initialized)
        self.assertTrue(mapper._high_bound_initialized)
        result = mapper.map_screen(ary)
        assert_equal(result, array([100, 80, 60, 40, 20, 0]))

    def test_update_screen_bounds_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.screen_bounds = (40.0, 120.0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([40.0, 56.0, 72.0, 88.0, 104.0, 120.0])
        )

    def test_update_screen_bounds_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.screen_bounds = (40.0, 120.0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([40.0, 50.0, 60.0, 70.0, 80.0, 90.0])
        )

    def test_reversed_update_screen_bounds_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 0.0)
        mapper.screen_bounds = (120.0, -10.0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([120.0, 94.0, 68.0, 42.0, 16.0, -10.0])
        )

    def test_reversed_update_screen_bounds_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 0.0)
        mapper.screen_bounds = (120.0, -10.0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([120.0, 100.0, 80.0, 60.0, 40.0, 20.0])
        )

    def test_update_low_pos_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.low_pos = 40.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([40, 52, 64, 76, 88, 100]))

    def test_update_low_pos_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.low_pos = 40.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([40, 50, 60, 70, 80, 90]))

    def test_reversed_update_low_pos_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 50.0)
        mapper.low_pos = 110.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([110, 98, 86, 74, 62, 50]))

    def test_reversed_update_low_pos_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 50.0)
        mapper.low_pos = 110.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([110, 100, 90, 80, 70, 60]))

    def test_update_high_pos_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.high_pos = 110.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([50, 62, 74, 86, 98, 110]))

    def test_update_high_pos_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.high_pos = 110.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([50, 60, 70, 80, 90, 100]))

    def test_reversed_update_high_pos_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 50.0)
        mapper.high_pos = 40.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([100, 88, 76, 64, 52, 40]))

    def test_reversed_update_high_pos_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 50.0)
        mapper.high_pos = 40.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([100, 90, 80, 70, 60, 50]))

    def test_update_low_pos_stretch_data_with_reverse(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.low_pos = 150.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([150, 140, 130, 120, 110, 100])
        )

    def test_update_low_pos_dont_stretch_data_with_reverse(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.low_pos = 150.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([150, 160, 170, 180, 190, 200])
        )

    def test_update_high_pos_stretch_data_with_reverse(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.high_pos = 0.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([50, 40, 30, 20, 10, 0]))

    def test_update_high_pos_dont_stretch_data_with_reverse(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.high_pos = 0.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([50, 60, 70, 80, 90, 100]))

    def test_update_low_pos_stretch_data_with_zero(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.low_pos = 100.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([100, 100, 100, 100, 100, 100])
        )

    def test_update_low_pos_dont_stretch_data_with_zero(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.low_pos = 100.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([100, 100, 100, 100, 100, 100])
        )

    def test_update_high_pos_stretch_data_with_zero(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.high_pos = 50.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([50, 50, 50, 50, 50, 50]))

    def test_update_high_pos_dont_stretch_data_with_zero(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.high_pos = 100.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([50, 60, 70, 80, 90, 100]))

    def test_map_screen_with_null_data_range(self):
        r = DataRange1D()
        mapper = LinearMapper(range=r)
        low_pos = mapper.low_pos

        data = array([5.6])
        result = mapper.map_screen(data)
        self.assertIsInstance(result, ndarray)
        self.assertEqual(result.shape, (1,))
        assert_array_almost_equal(result, array([low_pos]))

        # Test support for lists and tuples
        data = [5.6]
        result = mapper.map_screen(data)
        self.assertIsInstance(result, ndarray)
        self.assertEqual(result.shape, (1,))
        assert_array_almost_equal(result, array([low_pos]))

        data = (5.6,)
        result = mapper.map_screen(data)
        self.assertIsInstance(result, ndarray)
        self.assertEqual(result.shape, (1,))
        assert_array_almost_equal(result, array([low_pos]))
