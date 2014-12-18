"""
Test of basic dataseries behavior.
"""

import unittest2 as unittest

from numpy import arange, array, empty, isnan, nan, ones
from numpy.testing import assert_array_equal

from chaco.api import MultiArrayDataSource
from traits.testing.unittest_tools import UnittestTools


class MultiArrayDataTestCase(UnittestTools, unittest.TestCase):

    def test_init_defaults(self):
        data_source = MultiArrayDataSource()
        assert_array_equal(data_source._data, empty(shape=(0, 1), dtype=float))
        # XXX this doesn't match AbstractDataSource's interface
        self.assertEqual(data_source.value_dimension, 1)
        self.assertEqual(data_source.sort_order, "ascending")
        self.assertFalse(data_source.is_masked())

    def test_basic_setup(self):
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)

        assert_array_equal(myarray, data_source._data)
        # XXX this doesn't match AbstractDataSource's interface
        self.assertEqual(data_source.index_dimension, 0)
        self.assertEqual(data_source.value_dimension, 1)
        self.assertEqual(data_source.sort_order, "ascending")
        self.assertFalse(data_source.is_masked())

    def test_set_data(self):
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)
        new_array = arange(0, 40, 2).reshape(10, 2)

        with self.assertTraitChanges(data_source, 'data_changed', count=1):
            data_source.set_data(new_array)

        assert_array_equal(new_array, data_source._data)
        self.assertEqual(data_source.get_bounds(), (0, 38))
        self.assertEqual(data_source.sort_order, "ascending")

    def test_get_data(self):
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)

        assert_array_equal(myarray, data_source.get_data())

    def test_get_data_axes(self):
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)

        assert_array_equal(arange(0, 20, 2), data_source.get_data(axes=0))

    def test_get_data_no_data(self):
        data_source = MultiArrayDataSource()

        assert_array_equal(data_source.get_data(),
                           empty(shape=(0, 1), dtype=float))

    def test_get_data_mask(self):
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)

        data, mask = data_source.get_data_mask()
        assert_array_equal(data, myarray)
        assert_array_equal(mask, ones(shape=(10, 2), dtype=bool))

    def test_bounds(self):
        # ascending
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0, 19))

        # descending
        myarray = arange(20)[::-1].reshape(10, 2)
        data_source = MultiArrayDataSource(myarray, sort_order='descending')
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0, 19))

        # no order
        myarray = array([[12, 3], [0, 9], [2, 18], [3, 10]])
        data_source = MultiArrayDataSource(myarray, sort_order="none")
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0, 18))

    def test_bounds_value(self):
        # ascending
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)
        bounds = data_source.get_bounds(value=0)
        self.assertEqual(bounds, (0, 18))

        # descending
        myarray = arange(20)[::-1].reshape(10, 2)
        data_source = MultiArrayDataSource(myarray, sort_order='descending')
        bounds = data_source.get_bounds(value=0)
        self.assertEqual(bounds, (1, 19))

        # no order
        myarray = array([[12, 3], [0, 9], [2, 18], [3, 10]])
        data_source = MultiArrayDataSource(myarray, sort_order="none")
        bounds = data_source.get_bounds(value=0)
        self.assertEqual(bounds, (0, 12))

    def test_bounds_index(self):
        # ascending
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)
        bounds = data_source.get_bounds(index=0)
        self.assertEqual(bounds, (0, 1))

        # descending
        myarray = arange(20)[::-1].reshape(10, 2)
        data_source = MultiArrayDataSource(myarray, sort_order='descending')
        bounds = data_source.get_bounds(index=0)
        self.assertEqual(bounds, (18, 19))

        # no order
        myarray = array([[12, 3], [0, 9], [2, 18], [3, 10]])
        data_source = MultiArrayDataSource(myarray, sort_order="none")
        bounds = data_source.get_bounds(index=0)
        self.assertEqual(bounds, (3, 12))

    def test_bounds_empty(self):
        data_source = MultiArrayDataSource()
        bounds = data_source.get_bounds()
        # XXX this is sort of inconsistent with test_bounds_all_nans()
        self.assertEqual(bounds, (0, 0))

    def test_bounds_all_nans(self):
        myarray = empty((10, 2))
        myarray[:, :] = nan
        data_source = MultiArrayDataSource(myarray)
        bounds = data_source.get_bounds()
        self.assertTrue(isnan(bounds[0]))
        self.assertTrue(isnan(bounds[1]))

    def test_metadata(self):
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)

        self.assertEqual(data_source.metadata,
                         {'annotations': [], 'selections': []})

    @unittest.skip('change handler missing from class')
    def test_metadata_changed(self):
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)

        with self.assertTraitChanges(data_source, 'metadata_changed', count=1):
            data_source.metadata = {'new_metadata': True}

    @unittest.skip('change handler missing from class')
    def test_metadata_items_changed(self):
        myarray = arange(20).reshape(10, 2)
        data_source = MultiArrayDataSource(myarray)

        with self.assertTraitChanges(data_source, 'metadata_changed', count=1):
            data_source.metadata['new_metadata'] = True
