"""
Test of FunctionDataSource behavior.
"""

import unittest2 as unittest

from numpy import array, linspace, ones
from numpy.testing import assert_array_equal

from chaco.api import DataRange1D
from chaco.function_data_source import FunctionDataSource
from traits.testing.unittest_tools import UnittestTools


class FunctionDataSourceTestCase(UnittestTools, unittest.TestCase):

    def setUp(self):
        self.myfunc = lambda low, high: linspace(low, high, 101)**2
        self.data_source = FunctionDataSource(func=self.myfunc)


    def test_init_defaults(self):
        data_source = FunctionDataSource()
        assert_array_equal(data_source._data, [])
        self.assertEqual(data_source.value_dimension, "scalar")
        self.assertEqual(data_source.sort_order, "ascending")
        self.assertFalse(data_source.is_masked())

    def test_basic_setup(self):
        assert_array_equal(self.myfunc, self.data_source.func)
        self.assertEqual(self.data_source.value_dimension, "scalar")
        self.assertEqual(self.data_source.sort_order, "ascending")
        self.assertFalse(self.data_source.is_masked())

    def test_set_data(self):
        with self.assertRaises(RuntimeError):
            self.data_source.set_data(
                lambda low, high: linspace(low, high, 101))

    def test_range_high_changed(self):
        self.data_source.data_range = DataRange1D(low_setting=0.0,
                                                  high_setting=1.0)

        with self.assertTraitChanges(self.data_source, 'data_changed', count=1):
            self.data_source.data_range.high_setting = 2.0

        assert_array_equal(linspace(0.0, 2.0, 101)**2,
                           self.data_source.get_data())

    def test_range_low_changed(self):
        self.data_source.data_range = DataRange1D(low_setting=0.0,
                                                  high_setting=1.0)

        with self.assertTraitChanges(self.data_source, 'data_changed', count=1):
            self.data_source.data_range.low_setting = -1.0

        assert_array_equal(linspace(-1.0, 1.0, 101)**2,
                           self.data_source.get_data())

    def test_range_data_range_changed(self):
        self.data_source.data_range = DataRange1D(low_setting=0.0,
                                                  high_setting=1.0)

        with self.assertTraitChanges(self.data_source, 'data_changed', count=1):
            self.data_source.data_range = DataRange1D(low_setting=-2.0,
                                                      high_setting=2.0)

        assert_array_equal(linspace(-2.0, 2.0, 101)**2,
                           self.data_source.get_data())

    def test_set_mask(self):
        mymask = array([i % 2 for i in xrange(101)], dtype=bool)

        with self.assertRaises(NotImplementedError):
            self.data_source.set_mask(mymask)

    def test_remove_mask(self):
        with self.assertRaises(NotImplementedError):
            self.data_source.remove_mask()

    def test_get_data(self):
        self.data_source.data_range = DataRange1D(low_setting=0.0,
                                                  high_setting=1.0)

        assert_array_equal(linspace(0.0, 1.0, 101)**2,
                           self.data_source.get_data())

    def test_get_data_no_data(self):
        self.data_source = FunctionDataSource()

        assert_array_equal(self.data_source.get_data(), array([], dtype=float))

    def test_get_data_mask(self):
        self.data_source.data_range = DataRange1D(low_setting=0.0,
                                                  high_setting=1.0)

        data, mask = self.data_source.get_data_mask()
        assert_array_equal(data, linspace(0.0, 1.0, 101)**2)
        assert_array_equal(mask, ones(shape=101, dtype=bool))

    def test_bounds(self):
        self.data_source.data_range = DataRange1D(low_setting=0.0,
                                                  high_setting=2.0)

        bounds = self.data_source.get_bounds()
        self.assertEqual(bounds, (0.0, 4.0))

    @unittest.skip("default sort_order is ascending, which isn't right")
    def test_bounds_non_monotone(self):
        self.data_source.data_range = DataRange1D(low_setting=-2.0,
                                                  high_setting=2.0)

        bounds = self.data_source.get_bounds()
        self.assertEqual(bounds, (0.0, 4.0))

    def test_data_size(self):
        self.data_source.data_range = DataRange1D(low_setting=0.0,
                                                  high_setting=2.0)

        self.assertEqual(101, self.data_source.get_size())
