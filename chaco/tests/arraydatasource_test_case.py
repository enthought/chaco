"""
Test of basic dataseries behavior.
"""

import pickle

import unittest2 as unittest
from numpy import arange, array, allclose, empty, isnan, nan, ones
from numpy.testing import assert_array_equal
import numpy as np

from chaco.api import ArrayDataSource, PointDataSource
from traits.testing.unittest_tools import UnittestTools


class ArrayDataTestCase(UnittestTools, unittest.TestCase):

    def test_init_defaults(self):
        data_source = ArrayDataSource()
        assert_array_equal(data_source._data, [])
        self.assertEqual(data_source.value_dimension, "scalar")
        self.assertEqual(data_source.sort_order, "none")
        self.assertFalse(data_source.is_masked())

    def test_basic_setup(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)
        assert_array_equal(myarray, data_source._data)
        self.assertEqual(data_source.value_dimension, "scalar")
        self.assertEqual(data_source.sort_order, "none")
        self.assertFalse(data_source.is_masked())

    def test_set_data(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)
        new_array = arange(0, 20, 2)

        with self.assertTraitChanges(data_source, 'data_changed', count=1):
            data_source.set_data(new_array)

        assert_array_equal(new_array, data_source._data)
        self.assertEqual(data_source.get_bounds(), (0, 18))
        self.assertEqual(data_source.sort_order, "none")

    def test_set_data_ordered(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)
        new_array = arange(20, 0, -2)

        with self.assertTraitChanges(data_source, 'data_changed', count=1):
            data_source.set_data(new_array, sort_order='descending')

        assert_array_equal(new_array, data_source._data)
        self.assertEqual(data_source.get_bounds(), (2, 20))
        self.assertEqual(data_source.sort_order, "descending")

    def test_set_mask(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)
        mymask = array([i % 2 for i in myarray], dtype=bool)

        with self.assertTraitChanges(data_source, 'data_changed', count=1):
            data_source.set_mask(mymask)

        assert_array_equal(myarray, data_source._data)
        assert_array_equal(mymask, data_source._cached_mask)
        self.assertTrue(data_source.is_masked())
        self.assertEqual(data_source.get_bounds(), (0, 9))

    def test_remove_mask(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)
        mymask = array([i % 2 for i in myarray], dtype=bool)
        data_source.set_mask(mymask)
        self.assertTrue(data_source.is_masked())

        with self.assertTraitChanges(data_source, 'data_changed', count=1):
            data_source.remove_mask()

        assert_array_equal(myarray, data_source._data)
        self.assertIsNone(data_source._cached_mask, None)
        self.assertFalse(data_source.is_masked())
        self.assertEqual(data_source.get_bounds(), (0, 9))

    def test_get_data(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)

        assert_array_equal(myarray, data_source.get_data())

    def test_get_data_no_data(self):
        data_source = ArrayDataSource(None)

        # XXX A _scalar_?  Not array([]) or None?
        assert_array_equal(data_source.get_data(), 0.0)

    def test_get_data_mask(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)
        mymask = array([i % 2 for i in myarray], dtype=bool)
        data_source.set_mask(mymask)

        data, mask = data_source.get_data_mask()
        assert_array_equal(data, myarray)

    @unittest.skip('get_data_mask() fails in this case')
    def test_get_data_mask_no_data(self):
        data_source = ArrayDataSource(None)

        data, mask = data_source.get_data_mask()
        # XXX this is what I would expect, given get_data() behaviour
        assert_array_equal(data, 0.0)
        assert_array_equal(data, True)

    def test_get_data_mask_no_mask(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)

        data, mask = data_source.get_data_mask()
        assert_array_equal(data, myarray)
        assert_array_equal(mask, ones(shape=10, dtype=bool))

    def test_bounds(self):
        # ascending
        myarray = arange(10)
        data_source = ArrayDataSource(myarray, sort_order="ascending")
        bounds = data_source.get_bounds()
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
        myarray = np.array([u'abc', u'foo', u'bar', u'def'], dtype=unicode)
        data_source = ArrayDataSource(myarray)
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (u'abc', u'def'))

    def test_data_size(self):
        # We know that ArrayDataTestCase always returns the exact length of
        # its data
        myarray = arange(913)
        data_source = ArrayDataSource(myarray)
        self.assertEqual(len(myarray), data_source.get_size())

    def test_reverse_map(self):
        # sort_order ascending
        myarray = arange(10)
        data_source = ArrayDataSource(myarray, sort_order='ascending')

        self.assertEqual(data_source.reverse_map(4.0), 4)

        # sort_order descending
        myarray = arange(10)[::-1]
        data_source = ArrayDataSource(myarray, sort_order='descending')

        self.assertEqual(data_source.reverse_map(4.0), 5)

        # sort_order none
        myarray = array([12, 3, 0, 9, 2, 18, 3])
        data_source = ArrayDataSource(myarray, sort_order='ascending')

        self.assertEqual(data_source.reverse_map(3), None)

    def test_metadata(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)

        self.assertEqual(data_source.metadata,
                         {'annotations': [], 'selections': []})

    def test_metadata_changed(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)

        with self.assertTraitChanges(data_source, 'metadata_changed', count=1):
            data_source.metadata = {'new_metadata': True}

    def test_metadata_items_changed(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)

        with self.assertTraitChanges(data_source, 'metadata_changed', count=1):
            data_source.metadata['new_metadata'] = True

    def test_serialization_state(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)

        state = data_source.__getstate__()
        self.assertTrue('value_dimension' not in state)
        self.assertTrue('index_dimension' not in state)
        self.assertTrue('persist_data' not in state)

    @unittest.skip("persist_data probably shouldn't be persisted")
    def test_serialization_state_no_persist(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)
        data_source.persist_data = False

        state = data_source.__getstate__()
        self.assertTrue('value_dimension' not in state)
        self.assertTrue('index_dimension' not in state)
        self.assertTrue('persist_data' not in state)
        for key in ["_data", "_cached_mask", "_cached_bounds", "_min_index",
                    "_max_index"]:
            self.assertTrue(key not in state)

    @unittest.skip("I think this is just broken")
    def test_serialization_post_load(self):
        myarray = arange(10)
        data_source = ArrayDataSource(myarray)
        mymask = array([i % 2 for i in myarray], dtype=bool)
        data_source.set_mask(mymask)

        pickled_data_source = pickle.dumps(data_source)
        unpickled_data_source = pickle.loads(pickled_data_source)
        unpickled_data_source._post_load()

        self.assertEqual(unpickled_data_source._cached_bounds, ())
        self.assertEqual(unpickled_data_source._cached_mask, None)

        assert_array_equal(data_source.get_data(),
                           unpickled_data_source.get_data())

        mask = unpickled_data_source.get_data_mask()[1]
        assert_array_equal(mask, ones(10))


class PointDataTestCase(unittest.TestCase):
    # Since PointData is mostly the same as ScalarData, the key things to
    # test are functionality that use _compute_bounds() and reverse_map().
    def create_array(self):
        return array(zip(range(10), range(0, 100, 10)))

    def test_basic_set_get(self):
        myarray = self.create_array()
        pd = PointDataSource(myarray)
        self.assertTrue(allclose(myarray, pd._data))
        self.assert_(pd.value_dimension == "point")
        return

    def test_bounds(self):
        myarray = self.create_array()
        pd = PointDataSource(myarray)
        self.assertEqual(pd.get_bounds(), ((0, 0), (9, 90)))
        return


if __name__ == '__main__':
    import nose
    nose.run()
