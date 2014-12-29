"""
Test of basic dataseries behavior.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from numpy import arange, array, allclose, empty, isnan, nan
import numpy as np

from chaco.array_data_source import ArrayDataSource
from chaco.point_data_source import PointDataSource


class ArrayDataTestCase(unittest.TestCase):
    def test_basic_set_get(self):
        myarray = arange(10)
        sd = ArrayDataSource(myarray)
        self.assertTrue(allclose(myarray, sd._data))
        self.assert_(sd.value_dimension == "scalar")
        return

    def test_bounds(self):
        # ascending
        myarray = arange(10)
        sd = ArrayDataSource(myarray, sort_order="ascending")
        bounds = sd.get_bounds()
        self.assert_(bounds == (0,9))

        # descending
        myarray = arange(10)[::-1]
        sd = ArrayDataSource(myarray, sort_order="descending")
        bounds = sd.get_bounds()
        self.assert_(bounds == (0,9))

        # no order
        myarray = array([12,3,0,9,2,18,3])
        sd = ArrayDataSource(myarray, sort_order="none")
        bounds = sd.get_bounds()
        self.assert_(bounds == (0,18))
        return

    def test_data_size(self):
        # We know that ScalarData always returns the exact length of its data
        myarray = arange(913)
        sd = ArrayDataSource(myarray)
        self.assert_(len(myarray) == sd.get_size())
        return

    def test_bounds_all_nans(self):
        myarray = empty(10)
        myarray[:] = nan
        sd = ArrayDataSource(myarray)
        bounds = sd.get_bounds()
        self.assertTrue(isnan(bounds[0]))
        self.assertTrue(isnan(bounds[1]))

    def test_bounds_non_numeric(self):
        myarray = np.array([u'abc', u'foo', u'bar', u'def'], dtype=unicode)
        sd = ArrayDataSource(myarray)
        bounds = sd.get_bounds()
        self.assertEqual(bounds, (u'abc', u'def'))


class PointDataTestCase(unittest.TestCase):
    # Since PointData is mostly the same as ScalarData, the key things to
    # test are functionality that use _compute_bounds() and reverse_map().
    def create_array(self):
        return array(zip(range(10), range(0, 100, 10)))

    def test_basic_set_get(self):
        myarray = self.create_array()
        pd = PointDataSource(myarray)
        self.assertTrue(allclose(myarray,pd._data))
        self.assert_(pd.value_dimension == "point")
        return

    def test_bounds(self):
        myarray = self.create_array()
        pd = PointDataSource(myarray)
        self.assertEqual(pd.get_bounds(),((0,0), (9,90)))
        return

if __name__ == '__main__':
    import nose
    nose.run()
