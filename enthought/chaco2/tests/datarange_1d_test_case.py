
import unittest

from numpy import arange, array, zeros, inf
from numpy.testing import assert_equal

from enthought.chaco2.api import DataRange1D, ArrayDataSource


class DataRangeTestCase(unittest.TestCase):
    
    def test_empty_range(self):
        r = DataRange1D()
        self.assert_(r.low == -inf)
        self.assert_(r.high == inf)
        self.assert_(r.low_setting == "auto")
        self.assert_(r.high_setting == "auto")
        r.low = 5.0
        r.high = 10.0
        self.assert_(r.low_setting == 5.0)
        self.assert_(r.high_setting == 10.0)
        self.assert_(r.low == 5.0)
        self.assert_(r.high == 10.0)
        return
    
    def test_single_source(self):
        r = DataRange1D()
        ary = arange(10.0)
        ds = ArrayDataSource(ary)
        r.sources.append(ds)
        self.assert_(r.low == 0.0)
        self.assert_(r.high == 9.0)

        r.low = 3.0
        r.high = 6.0
        self.assert_(r.low_setting == 3.0)
        self.assert_(r.high_setting == 6.0)
        self.assert_(r.low == 3.0)
        self.assert_(r.high == 6.0)
        
        r.refresh()
        self.assert_(r.low_setting == 3.0)
        self.assert_(r.high_setting == 6.0)
        self.assert_(r.low == 3.0)
        self.assert_(r.high == 6.0)
        
        r.low = "auto"
        self.assert_(r.low_setting == "auto")
        self.assert_(r.low == 0.0)
        return

    def test_constant_value(self):
        r = DataRange1D()
        ary = array([3.14])
        ds = ArrayDataSource(ary)
        r.add(ds)
        # A constant value > 1.0, by default, gets a range that brackets
        # it to the nearest power of ten above and below
        self.assert_(r.low == 1.0)
        self.assert_(r.high == 10.0)
        
        r.remove(ds)
        ds = ArrayDataSource(array([31.4]))
        r.add(ds)
        self.assert_(r.low == 10.0)
        self.assert_(r.high == 100.0)
        
        r.remove(ds)
        ds = ArrayDataSource(array([0.03]))
        r.add(ds)
        self.assert_(r.low == -1.0)
        self.assert_(r.high == 1.0)

        r.remove(ds)
        ds = ArrayDataSource(array([-0.03]))
        r.add(ds)
        self.assert_(r.low == -1.0)
        self.assert_(r.high == 1.0)
        return

    def test_multi_source(self):
        ds1 = ArrayDataSource(array([3, 4, 5, 6, 7]))
        ds2 = ArrayDataSource(array([5, 10, 15, 20]))
        r = DataRange1D(ds1, ds2)
        self.assert_(r.low == 3.0)
        self.assert_(r.high == 20.0)
        return

    def test_clip_data(self):
        r = DataRange1D(low=2.0, high=10.0)
        ary = array([1, 3, 4, 9.8, 10.2, 12])
        assert_equal(r.clip_data(ary) , array([3.0,4.0,9.8]))
        
        r = DataRange1D(low=10, high=20)
        ary = array([5, 10, 15, 20, 25, 30])
        assert_equal(r.clip_data(ary) , array([10, 15, 20]))
        assert_equal(r.clip_data(ary[::-1]) , array([20, 15, 10]))
        
        r = DataRange1D(low=2.0, high=2.5)
        assert_equal(len(r.clip_data(ary)) , 0)
        return

    def test_mask_data(self):
        r = DataRange1D(low=2.0, high=10.0)
        ary = array([1, 3, 4, 9.8, 10.2, 12])
        assert_equal(r.mask_data(ary) , array([0,1,1,1,0,0], 'b'))
        
        r = DataRange1D(low=10, high=20)
        ary = array([5, 10, 15, 20, 25, 30])
        target_mask = array([0,1,1,1,0,0], 'b')
        assert_equal(r.mask_data(ary) , target_mask)
        assert_equal(r.mask_data(ary[::-1]) , target_mask[::-1])
        
        r = DataRange1D(low=2.0, high=2.5)
        assert_equal(r.mask_data(ary) , zeros(len(ary)))
        return

    def test_bound_data(self):
        r = DataRange1D(low=2.9, high=6.1)
        ary = arange(10)
        assert_equal(r.bound_data(ary) , (3,6))
        
        # test non-monotonic data
        ary = array([-5,-4,-7,-8,-2,1,2,3,4,5,4,3,8,9,10,9,8])
        bounds = r.bound_data(ary)
        assert_equal(bounds , (7,11))
        return

    def test_custom_bounds_func(self):
        def custom_func(low, high, margin, tight_bounds):
            assert low==0.0
            assert high==9.0
            assert tight_bounds==False
            assert margin==1.0
            return -999., 999.
        
        r = DataRange1D(tight_bounds=False, margin=1.0, bounds_func=custom_func)
        ary = arange(10.0)
        ds = ArrayDataSource(ary)
        r.sources.append(ds)
        assert r.low==-999.
        assert r.high==999.

if __name__ == '__main__':
    import nose
    nose.run()
