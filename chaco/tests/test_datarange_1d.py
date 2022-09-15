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
import warnings

from numpy import arange, array, zeros, inf
from numpy.testing import assert_equal

from traits.api import HasTraits, Instance, Bool, observe

from chaco.api import DataRange1D, ArrayDataSource

NAN = float("nan")


class Foo(HasTraits):
    """
    This class is used to test the firing of the `updated` event of DataRange1D.
    """

    range = Instance(DataRange1D)

    range_updated = Bool(False)

    @observe("range.updated")
    def range_changed(self, event):
        self.range_updated = True


class DataRangeTestCase(unittest.TestCase):
    def test_empty_range(self):
        r = DataRange1D()
        self.assertEqual(r.low, -inf)
        self.assertEqual(r.high, inf)
        self.assertEqual(r.low_setting, "auto")
        self.assertEqual(r.high_setting, "auto")
        r.low = 5.0
        r.high = 10.0
        self.assertEqual(r.low_setting, 5.0)
        self.assertEqual(r.high_setting, 10.0)
        self.assertEqual(r.low, 5.0)
        self.assertEqual(r.high, 10.0)

    def test_set_bounds1(self):
        """Change both low and high with set_bounds()."""
        foo = Foo(range=DataRange1D(low=0.0, high=1.0))
        # Paranoid check first (not the main point of this test):
        self.assertEqual(foo.range.low, 0.0)
        self.assertEqual(foo.range.high, 1.0)
        # Now reset foo's range_updated flag and set the bounds with set_bounds().
        foo.range_updated = False
        foo.range.set_bounds(-1.0, 2.0)
        # Verify the values.
        self.assertEqual(foo.range.low, -1.0)
        self.assertEqual(foo.range.high, 2.0)
        # Verify that the `updated` event fired.
        self.assertTrue(foo.range_updated)

    def test_set_bounds2(self):
        """Change only the high value with set_bounds()."""
        foo = Foo(range=DataRange1D(low=0.0, high=1.0))
        # Paranoid check first (not the main point of this test):
        self.assertEqual(foo.range.low, 0.0)
        self.assertEqual(foo.range.high, 1.0)
        # Now reset foo's range_updated flag and set the bounds with set_bounds().
        foo.range_updated = False
        foo.range.set_bounds(0.0, 2.0)
        # Verify the values.
        self.assertEqual(foo.range.low, 0.0)
        self.assertEqual(foo.range.high, 2.0)
        # Verify that the `updated` event fired.
        self.assertTrue(foo.range_updated)

    def test_set_bounds3(self):
        """Change only the low value with set_bounds()."""
        foo = Foo(range=DataRange1D(low=0.0, high=1.0))
        # Paranoid check first (not the main point of this test):
        self.assertEqual(foo.range.low, 0.0)
        self.assertEqual(foo.range.high, 1.0)
        # Now reset foo's range_updated flag and set the bounds with set_bounds().
        foo.range_updated = False
        foo.range.set_bounds(0.5, 1.0)
        # Verify the values.
        self.assertEqual(foo.range.low, 0.5)
        self.assertEqual(foo.range.high, 1.0)
        # Verify that the `updated` event fired.
        self.assertTrue(foo.range_updated)

    def test_set_bounds4(self):
        """Set set_bounds() with high='track'."""
        foo = Foo(range=DataRange1D(tracking_amount=1.0))
        foo.range.low_setting = 0.0
        foo.range.high_setting = "track"
        # Paranoid check first (not the main point of this test):
        self.assertEqual(foo.range.low, 0.0)
        self.assertEqual(foo.range.high, 1.0)
        # Now reset foo's range_updated flag and set the bounds with set_bounds().
        foo.range_updated = False
        foo.range.set_bounds(100.0, "track")
        # Verify the values.
        self.assertEqual(foo.range.low, 100.0)
        self.assertEqual(foo.range.high, 101.0)
        # Verify that the `updated` event fired.
        self.assertTrue(foo.range_updated)

    def test_set_bounds5(self):
        """Set set_bounds() with low='track'."""
        foo = Foo(range=DataRange1D(tracking_amount=1.0))
        foo.range.low_setting = "track"
        foo.range.high_setting = 1.0
        # Paranoid check first (not the main point of this test):
        self.assertEqual(foo.range.low, 0.0)
        self.assertEqual(foo.range.high, 1.0)
        # Now reset foo's range_updated flag and set the bounds with set_bounds().
        foo.range_updated = False
        foo.range.set_bounds("track", 100.0)
        # Verify the values.
        self.assertEqual(foo.range.low, 99.0)
        self.assertEqual(foo.range.high, 100.0)
        # Verify that the `updated` event fired.
        self.assertTrue(foo.range_updated)

    def test_set_tracking_amount(self):
        """Test setting the tracking amount using the set_tracking_amount() method."""
        foo = Foo(range=DataRange1D(tracking_amount=1.0))
        foo.range.low_setting = "track"
        foo.range.high_setting = 1.0
        # Paranoid check first (not the main point of this test):
        self.assertEqual(foo.range.low, 0.0)
        self.assertEqual(foo.range.high, 1.0)
        # Now reset foo's range_updated flag and change the tracking amount.
        foo.range_updated = False
        foo.range.set_tracking_amount(2.0)
        # Verify the values.
        self.assertEqual(foo.range.low, -1.0)
        self.assertEqual(foo.range.high, 1.0)
        # Verify that the `updated` event fired.
        self.assertTrue(foo.range_updated)

    def test_scale_tracking_amount(self):
        """Test setting the tracking amount using the scale_tracking_amount() method."""
        foo = Foo(range=DataRange1D(tracking_amount=1.0))
        foo.range.low_setting = "track"
        foo.range.high_setting = 1.0
        # Paranoid check first (not the main point of this test):
        self.assertEqual(foo.range.low, 0.0)
        self.assertEqual(foo.range.high, 1.0)
        # Now reset foo's range_updated flag and change the tracking amount.
        foo.range_updated = False
        foo.range.scale_tracking_amount(0.5)
        # Verify the values.
        self.assertEqual(foo.range.low, 0.5)
        self.assertEqual(foo.range.high, 1.0)
        # Verify that the `updated` event fired.
        self.assertTrue(foo.range_updated)

    def test_single_source(self):
        r = DataRange1D()
        ary = arange(10.0)
        ds = ArrayDataSource(ary)
        r.sources.append(ds)
        self.assertEqual(r.low, 0.0)
        self.assertEqual(r.high, 9.0)

        r.low = 3.0
        r.high = 6.0
        self.assertEqual(r.low_setting, 3.0)
        self.assertEqual(r.high_setting, 6.0)
        self.assertEqual(r.low, 3.0)
        self.assertEqual(r.high, 6.0)

        r.refresh()
        self.assertEqual(r.low_setting, 3.0)
        self.assertEqual(r.high_setting, 6.0)
        self.assertEqual(r.low, 3.0)
        self.assertEqual(r.high, 6.0)

        r.low = "auto"
        self.assertEqual(r.low_setting, "auto")
        self.assertEqual(r.low, 0.0)

    def test_constant_value(self):
        r = DataRange1D()
        ary = array([3.14])
        ds = ArrayDataSource(ary)
        r.add(ds)
        # A constant value > 1.0, by default, gets a range that brackets
        # it to the nearest power of ten above and below
        self.assertEqual(r.low, 1.0)
        self.assertEqual(r.high, 10.0)

        r.remove(ds)
        ds = ArrayDataSource(array([31.4]))
        r.add(ds)
        self.assertEqual(r.low, 10.0)
        self.assertEqual(r.high, 100.0)

        r.remove(ds)
        ds = ArrayDataSource(array([0.125]))
        r.add(ds)
        self.assertEqual(r.low, 0.0)
        self.assertEqual(r.high, 0.25)

        r.remove(ds)
        ds = ArrayDataSource(array([-0.125]))
        r.add(ds)
        self.assertEqual(r.low, -0.25)
        self.assertEqual(r.high, 0.0)

    def test_multi_source(self):
        ds1 = ArrayDataSource(array([3, 4, 5, 6, 7]))
        ds2 = ArrayDataSource(array([5, 10, 15, 20]))
        r = DataRange1D(ds1, ds2)
        self.assertEqual(r.low, 3.0)
        self.assertEqual(r.high, 20.0)

    def test_clip_data(self):
        r = DataRange1D(low=2.0, high=10.0)
        ary = array([1, 3, 4, 9.8, 10.2, 12])
        assert_equal(r.clip_data(ary), array([3.0, 4.0, 9.8]))

        r = DataRange1D(low=10, high=20)
        ary = array([5, 10, 15, 20, 25, 30])
        assert_equal(r.clip_data(ary), array([10, 15, 20]))
        assert_equal(r.clip_data(ary[::-1]), array([20, 15, 10]))

        r = DataRange1D(low=2.0, high=2.5)
        assert_equal(len(r.clip_data(ary)), 0)

        # Test the case with nans. Additionally require that no warnings are
        # emitted.
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            r = DataRange1D(low=2.0, high=10.0)
            ary = array([1, 3, NAN, 9.8, 10.2, 12])
            assert_equal(r.clip_data(ary), array([3.0, 9.8]))
        self.assertEqual(len(w), 0)

    def test_mask_data(self):
        r = DataRange1D(low=2.0, high=10.0)
        ary = array([1, 3, 4, 9.8, 10.2, 12])
        assert_equal(r.mask_data(ary), array([0, 1, 1, 1, 0, 0], "b"))

        r = DataRange1D(low=10, high=20)
        ary = array([5, 10, 15, 20, 25, 30])
        target_mask = array([0, 1, 1, 1, 0, 0], "b")
        assert_equal(r.mask_data(ary), target_mask)
        assert_equal(r.mask_data(ary[::-1]), target_mask[::-1])

        r = DataRange1D(low=2.0, high=2.5)
        assert_equal(r.mask_data(ary), zeros(len(ary)))

    def test_mask_data_containing_nans(self):
        # Given
        r = DataRange1D(low=2.0, high=10.0)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # When
            has_nans = array([1, 3, 9.8, NAN, 12])
            # Then
            assert_equal(r.mask_data(has_nans), array([0, 1, 1, 0, 0], "b"))

            # When
            all_nans = array([NAN, NAN, NAN])
            # Then
            assert_equal(r.mask_data(all_nans), array([0, 0, 0], "b"))

        # Then (treating nans should come with no warnings)
        # NOTE: This assertion may pass because the warning has been correctly
        # silenced by us (useful test), but it may also pass because the
        # warning has been inactivated by the "only warn once" Python rule
        # (test ineffective, false negative). Clearing the registry only for
        # test purposes is not feasible: https://bugs.python.org/issue21724
        self.assertEqual(len(w), 0)

    def test_bound_data(self):
        r = DataRange1D(low=2.9, high=6.1)
        ary = arange(10)
        assert_equal(r.bound_data(ary), (3, 6))

        # test non-monotonic data
        ary = array([-5, -4, -7, -8, -2, 1, 2, 3, 4, 5, 4, 3, 8, 9, 10, 9, 8])
        bounds = r.bound_data(ary)
        assert_equal(bounds, (7, 11))

        # test data with nan (expected: nan breaks a run)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ary = array([1, 2, 3, 4, NAN, 6, 7])
            bounds = r.bound_data(ary)
            assert_equal(bounds, (2, 3))
        self.assertEqual(len(w), 0)

    def test_custom_bounds_func(self):
        def custom_func(low, high, margin, tight_bounds):
            assert_equal(low, 0.0)
            assert_equal(high, 9.0)
            assert_equal(tight_bounds, False)
            assert_equal(margin, 1.0)
            return -999.0, 999.0

        r = DataRange1D(
            tight_bounds=False, margin=1.0, bounds_func=custom_func
        )
        ary = arange(10.0)
        ds = ArrayDataSource(ary)
        r.sources.append(ds)
        assert_equal(r.low, -999.0)
        assert_equal(r.high, 999.0)

    def test_inf_in_source(self):
        r = DataRange1D()
        ary1 = array([1.0, inf])
        ds1 = ArrayDataSource(ary1)
        r.sources.append(ds1)
        self.assertEqual(r.low, 1.0)
        self.assertEqual(r.high, inf)
        data = array([-100.0, 0.0, 100.0])
        assert_equal(r.clip_data(data), array([100.0]))

        r = DataRange1D()
        ary2 = array([-inf, 1.0])
        ds2 = ArrayDataSource(ary2)
        r.sources.append(ds2)
        self.assertEqual(r.low, -inf)
        self.assertEqual(r.high, 1.0)

        r.sources.append(ds1)
        self.assertEqual(r.low, -inf)
        self.assertEqual(r.high, inf)
