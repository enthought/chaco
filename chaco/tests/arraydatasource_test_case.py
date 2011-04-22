"""
Test of basic dataseries behavior.
"""

import unittest

from numpy import arange, array, allclose
from enthought.chaco.api import ArrayDataSource, PointDataSource


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
