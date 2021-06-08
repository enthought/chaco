# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests of ArrayDataSource behavior.
"""

import pickle

import unittest

from numpy import arange, array, allclose, empty, isnan, nan, ones
from numpy.testing import assert_array_equal
import numpy as np

from chaco.api import ArrayDataSource, PointDataSource
from traits.testing.api import UnittestTools


class ArrayDataSourceTestCase(UnittestTools, unittest.TestCase):
    def setUp(self):
        self.myarray = arange(10)
        self.mymask = array([i % 2 for i in self.myarray], dtype=bool)
        self.data_source = ArrayDataSource(self.myarray)

    def test_init_defaults(self):
        data_source = ArrayDataSource()
        assert_array_equal(data_source._data, [])
        self.assertEqual(data_source.value_dimension, "scalar")
        self.assertEqual(data_source.index_dimension, "scalar")
        self.assertEqual(data_source.sort_order, "none")
        self.assertFalse(data_source.is_masked())
        self.assertEqual(data_source.persist_data, True)

    def test_basic_setup(self):
        assert_array_equal(self.myarray, self.data_source._data)
        self.assertEqual(self.data_source.value_dimension, "scalar")
        self.assertEqual(self.data_source.sort_order, "none")
        self.assertFalse(self.data_source.is_masked())

    def test_set_data(self):
        new_array = arange(0, 20, 2)

        with self.assertTraitChanges(
            self.data_source, "data_changed", count=1
        ):
            self.data_source.set_data(new_array)

        assert_array_equal(new_array, self.data_source._data)
        self.assertEqual(self.data_source.get_bounds(), (0, 18))
        self.assertEqual(self.data_source.sort_order, "none")

    def test_set_data_ordered(self):
        new_array = arange(20, 0, -2)

        with self.assertTraitChanges(
            self.data_source, "data_changed", count=1
        ):
            self.data_source.set_data(new_array, sort_order="descending")

        assert_array_equal(new_array, self.data_source._data)
        self.assertEqual(self.data_source.get_bounds(), (2, 20))
        self.assertEqual(self.data_source.sort_order, "descending")

    def test_set_mask(self):
        with self.assertTraitChanges(
            self.data_source, "data_changed", count=1
        ):
            self.data_source.set_mask(self.mymask)

        assert_array_equal(self.myarray, self.data_source._data)
        assert_array_equal(self.mymask, self.data_source._cached_mask)
        self.assertTrue(self.data_source.is_masked())
        self.assertEqual(self.data_source.get_bounds(), (0, 9))

    def test_remove_mask(self):
        self.data_source.set_mask(self.mymask)
        self.assertTrue(self.data_source.is_masked())

        with self.assertTraitChanges(
            self.data_source, "data_changed", count=1
        ):
            self.data_source.remove_mask()

        assert_array_equal(self.myarray, self.data_source._data)
        self.assertIsNone(self.data_source._cached_mask, None)
        self.assertFalse(self.data_source.is_masked())
        self.assertEqual(self.data_source.get_bounds(), (0, 9))

    def test_get_data(self):
        assert_array_equal(self.myarray, self.data_source.get_data())

    def test_get_data_no_data(self):
        data_source = ArrayDataSource(None)

        assert_array_equal(data_source.get_data(), 0.0)

    def test_get_data_mask(self):
        self.data_source.set_mask(self.mymask)

        data, mask = self.data_source.get_data_mask()
        assert_array_equal(data, self.myarray)
        assert_array_equal(mask, self.mymask)

    def test_get_data_mask_no_data(self):
        data_source = ArrayDataSource(None)

        data, mask = data_source.get_data_mask()
        self.assertEqual(data, None)
        assert_array_equal(mask, ones(shape=0, dtype=bool))

    def test_get_data_mask_no_mask(self):
        data, mask = self.data_source.get_data_mask()
        assert_array_equal(data, self.myarray)
        assert_array_equal(mask, ones(shape=10, dtype=bool))

    def test_bounds(self):
        # ascending
        bounds = self.data_source.get_bounds()
        self.assertEqual(bounds, (0, 9))

        # descending
        myarray = arange(10)[::-1]
        data_source = ArrayDataSource(myarray, sort_order="descending")
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0, 9))

        # no order
        myarray = array([12, 3, 0, 9, 2, 18, 3])
        data_source = ArrayDataSource(myarray, sort_order="none")
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0, 18))

    def test_bounds_length_one(self):
        # this is special-cased in the code, so exercise the code path
        data_source = ArrayDataSource(array([1.0]))
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (1.0, 1.0))

    def test_bounds_length_zero(self):
        # this is special-cased in the code, so exercise the code path
        data_source = ArrayDataSource(array([]))
        bounds = data_source.get_bounds()
        # XXX this is sort of inconsistent with test_bounds_all_nans()
        self.assertEqual(bounds, (0, 0))

    def test_bounds_empty(self):
        data_source = ArrayDataSource()
        bounds = data_source.get_bounds()
        # XXX this is sort of inconsistent with test_bounds_all_nans()
        self.assertEqual(bounds, (0, 0))

    def test_bounds_all_nans(self):
        myarray = empty(10)
        myarray[:] = nan
        sd = ArrayDataSource(myarray)
        bounds = sd.get_bounds()
        self.assertTrue(isnan(bounds[0]))
        self.assertTrue(isnan(bounds[1]))

    def test_bounds_some_nan(self):
        data_source = ArrayDataSource(array([np.nan, 3, 0, 9, np.nan, 18, 3]))
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0, 18))

    def test_bounds_negative_inf(self):
        data_source = ArrayDataSource(array([12, 3, -np.inf, 9, 2, 18, 3]))
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (-np.inf, 18))

    def test_bounds_positive_inf(self):
        data_source = ArrayDataSource(array([12, 3, 0, 9, 2, np.inf, 3]))
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0, np.inf))

    def test_bounds_negative_positive_inf(self):
        data_source = ArrayDataSource(array([12, 3, -np.inf, 9, 2, np.inf, 3]))
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (-np.inf, np.inf))

    def test_bounds_non_numeric(self):
        myarray = np.array([u"abc", u"foo", u"bar", u"def"], dtype=str)
        data_source = ArrayDataSource(myarray)
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (u"abc", u"def"))

    def test_data_size(self):
        # We know that ArrayDataTestCase always returns the exact length of
        # its data
        myarray = arange(913)
        data_source = ArrayDataSource(myarray)
        self.assertEqual(len(myarray), data_source.get_size())

    def test_reverse_map(self):
        # sort_order ascending
        myarray = arange(10)
        data_source = ArrayDataSource(myarray, sort_order="ascending")

        self.assertEqual(data_source.reverse_map(4.0), 4)

        # sort_order descending
        myarray = arange(10)[::-1]
        data_source = ArrayDataSource(myarray, sort_order="descending")

        self.assertEqual(data_source.reverse_map(4.0), 5)

        # sort_order none
        myarray = array([12, 3, 0, 9, 2, 18, 3])
        data_source = ArrayDataSource(myarray, sort_order="none")

        with self.assertRaises(NotImplementedError):
            data_source.reverse_map(3)

    def test_metadata(self):
        self.assertEqual(
            self.data_source.metadata, {"annotations": [], "selections": []}
        )

    def test_metadata_changed(self):
        with self.assertTraitChanges(
            self.data_source, "metadata_changed", count=1
        ):
            self.data_source.metadata = {"new_metadata": True}

    def test_metadata_items_changed(self):
        with self.assertTraitChanges(
            self.data_source, "metadata_changed", count=1
        ):
            self.data_source.metadata["new_metadata"] = True

    def test_serialization_state(self):
        state = self.data_source.__getstate__()
        self.assertNotIn("value_dimension", state)
        self.assertNotIn("index_dimension", state)
        self.assertNotIn("persist_data", state)
        for key in [
            "_data",
            "_cached_mask",
            "_cached_bounds",
            "_min_index",
            "_max_index",
        ]:
            self.assertIn(key, state)

    def test_serialization_state_no_persist(self):
        self.data_source.persist_data = False

        state = self.data_source.__getstate__()
        self.assertNotIn("value_dimension", state)
        self.assertNotIn("index_dimension", state)
        self.assertNotIn("persist_data", state)
        for key in [
            "_data",
            "_cached_mask",
            "_cached_bounds",
            "_min_index",
            "_max_index",
        ]:
            self.assertNotIn(key, state)

    @unittest.skip("I think this is just broken")
    def test_serialization_post_load(self):
        self.data_source.set_mask(self.mymask)

        pickled_data_source = pickle.dumps(self.data_source)
        unpickled_data_source = pickle.loads(pickled_data_source)
        unpickled_data_source._post_load()

        self.assertEqual(unpickled_data_source._cached_bounds, ())
        self.assertEqual(unpickled_data_source._cached_mask, None)

        assert_array_equal(
            self.data_source.get_data(), unpickled_data_source.get_data()
        )

        mask = unpickled_data_source.get_data_mask()[1]
        assert_array_equal(mask, ones(10))


class PointDataTestCase(unittest.TestCase):
    # Since PointData is mostly the same as ScalarData, the key things to
    # test are functionality that use _compute_bounds() and reverse_map().
    def create_array(self):
        return array(list(zip(list(range(10)), list(range(0, 100, 10)))))

    def test_basic_set_get(self):
        myarray = self.create_array()
        pd = PointDataSource(myarray)
        self.assertTrue(allclose(myarray, pd._data))
        self.assertTrue(pd.value_dimension == "point")

    def test_bounds(self):
        myarray = self.create_array()
        pd = PointDataSource(myarray)
        self.assertEqual(pd.get_bounds(), ((0, 0), (9, 90)))
