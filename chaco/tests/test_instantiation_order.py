"""
Tests that various plot and data objects can be instantiated, assigned, and
re-assigned in any order.
"""

import unittest

from numpy import array
from chaco.api import ArrayDataSource, DataRange1D, \
                                 LinearMapper

class DataPipelineTestCase(unittest.TestCase):
    def test_piecewise_construction(self):
        ary = array([1,2,3,4,5,6,7])
        ds = ArrayDataSource()
        ds.set_data(ary)
        r = DataRange1D()
        r.add(ds)
        self.assertTrue(r.low_setting == "auto")
        self.assertTrue(r.high_setting == "auto")
        self.assertTrue(r.low == 1)
        self.assertTrue(r.high == 7)

        mapper = LinearMapper()
        mapper.range = r
        mapper.low_pos = 1.0
        mapper.high_pos = 7.0
        screen_pts = mapper.map_screen(array([1,3,7]))
        self.assertTrue(tuple(screen_pts) == (1.0, 3.0, 7.0))
        return

    def test_reverse_construction(self):
        mapper = LinearMapper()
        r = DataRange1D()
        ds = ArrayDataSource()
        ary = array([1,2,3,4,5,6,7])

        mapper.range = r
        mapper.low_pos = 1.0
        mapper.high_pos = 7.0
        r.add(ds)
        ds.set_data(ary)

        self.assertTrue(r.low == 1)
        self.assertTrue(r.high == 7)
        screen_pts = mapper.map_screen(array([1,3,7]))
        self.assertTrue(tuple(screen_pts) == (1.0, 3.0, 7.0))
        return


if __name__ == '__main__':
    import nose
    nose.run()
