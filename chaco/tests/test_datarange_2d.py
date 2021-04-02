
import unittest

from numpy import alltrue, arange, array, ravel, transpose, zeros, inf, isinf
from numpy.testing import assert_equal, assert_

from chaco.api import DataRange2D, GridDataSource, PointDataSource


class DataRange2DTestCase(unittest.TestCase):

    def test_empty_range(self):
        r = DataRange2D()
        assert_ary_(r.low,array([-inf,-inf]))
        assert_ary_(r.high,array([inf,inf]))
        self.assertTrue(r.low_setting == ('auto','auto'))
        self.assertTrue(r.high_setting == ('auto', 'auto'))
        r.low  = array([5.0,5.0])
        r.high = array([10.0,10.0])
        assert_ary_(r.low_setting, array([5.0,5.0]))
        assert_ary_(r.high_setting, array([10.0,10.0]))
        assert_ary_(r.low,array([5.0,5.0]))
        assert_ary_(r.high, array([10.0,10.0]))

    def test_single_source(self):
        r = DataRange2D()
        x = arange(10.)
        y = arange(0.,100.,10.)
        ds = PointDataSource(transpose(array([x,y])), sort_order="none")
        r.add(ds)
        assert_ary_(r.low, array([0.,0.]))
        assert_ary_(r.high, array([9.0,90.0]))

        r.low = [3.0,30.0]
        r.high = [6.0,60.0]
        assert_ary_(r.low_setting, array([3.0,30.0]))
        assert_ary_(r.high_setting, array([6.0,60.0]))
        assert_ary_(r.low, array([3.0,30.0]))
        assert_ary_(r.high, array([6.0,60.0]))

        r.refresh()
        assert_ary_(r.low_setting, array([3.0,30.0]))
        assert_ary_(r.high_setting, array([6.0,60.0]))
        assert_ary_(r.low, array([3.0,30.0]))
        assert_ary_(r.high, array([6.0,60.0]))

        r.low = ('auto', 'auto')
        self.assertTrue(r.low_setting == ('auto', 'auto'))
        assert_ary_(r.low, array([0.0,0.0]))

    def test_constant_values(self):
        r = DataRange2D()
        ds = PointDataSource(array([[5.0,5.0]]), sort_order="none")
        r.add(ds)
        # A constant value > 1.0, by default, gets a range that brackets
        # it to the nearest power of ten above and below
        assert_ary_(r.low, array([1.0,1.0]))
        assert_ary_(r.high, array([10.0,10.0]))

        r.remove(ds)
        ds = PointDataSource(array([[31.4,9.7]]))
        r.add(ds)

        assert_ary_(r.low, array([10.0,1.0]))
        assert_ary_(r.high, array([100.0,10.0]))

        r.remove(ds)
        ds = PointDataSource(array([[0.125,0.125]]))
        r.add(ds)
        assert_ary_(r.low, array([0.0, 0.0]))
        assert_ary_(r.high, array([0.25, 0.25]))

        r.remove(ds)
        ds = PointDataSource(array([[-0.125, -0.125]]))
        r.add(ds)
        assert_ary_(r.low, array([-0.25, -0.25]))
        assert_ary_(r.high, array([0.0, 0.0]))

    def test_multi_source(self):
        x = arange(10.)
        y = arange(0.,100.,10.)
        foo = transpose(array([x,y]))
        bar = transpose(array([y,x]))
        ds1 = PointDataSource(foo)
        ds2 = PointDataSource(bar)
        r = DataRange2D(ds1, ds2)
        assert_ary_(r.low, [0.0,0.0])
        assert_ary_(r.high, [90.,90.])

    def test_grid_source(self):
        test_xd1 = array([1,2,3])
        test_yd1 = array([1.5, 0.5, -0.5, -1.5])
        test_sort_order1 = ('ascending', 'descending')
        test_xd2 = array([0,50,100])
        test_yd2 = array([0.5, 0.75, 1])
        ds1 = GridDataSource(xdata=test_xd1, ydata=test_yd1,
                            sort_order=test_sort_order1)
        ds2 = GridDataSource(xdata=test_xd2, ydata=test_yd2)

        r = DataRange2D()

        r.add(ds1)
        assert_ary_(r.low, array([1,-1.5]))
        assert_ary_(r.high, array([3,1.5]))

        r.add(ds2)
        assert_ary_(r.low, array([0.0,-1.5]))
        assert_ary_(r.high, array([100,1.5]))

        r.remove(ds1)
        assert_ary_(r.low, array([0,0.5]))
        assert_ary_(r.high, array([100,1]))

        r.remove(ds2)
        assert_ary_(r.low, array([-inf,-inf]))
        assert_ary_(r.high, array([inf,inf]))


    def test_set_bounds(self):
        test_xd = array([-10,10])
        test_yd = array([-10,10])
        ds = GridDataSource(xdata=test_xd, ydata=test_yd)

        r = DataRange2D()

        r.set_bounds((-1,-2), (3,4))
        assert_ary_(r.low, array([-1,-2]))
        assert_ary_(r.high, array([3,4]))

        r.add(ds)
        assert_ary_(r.low, array([-1,-2]))

        r.low_setting = ('auto','auto')
        assert_ary_(r.low, array([-10,-10]))
        assert_ary_(r.high, array([3,4]))

        r.high_setting = ('auto','auto')
        assert_ary_(r.low, array([-10,-10]))
        assert_ary_(r.high, array([10,10]))

        r.set_bounds((-100,-100), (100,100))
        assert_ary_(r.low, array([-100,-100]))
        assert_ary_(r.high, array([100,100]))

    def test_reset_bounds(self):
        r = DataRange2D()

        low = (13, 42)
        high = (1337, 9001)

        r.set_bounds(low, high)
        self.assertEqual(r.low_setting, low)
        self.assertEqual(r.high_setting, high)

        r.reset()

        self.assertEqual(r.low_setting, ('auto', 'auto'))
        self.assertEqual(r.high_setting, ('auto', 'auto'))
        self.assertEqual(r.x_range.low_setting, 'auto')
        self.assertEqual(r.y_range.low_setting, 'auto')
        self.assertEqual(r.x_range.high_setting, 'auto')
        self.assertEqual(r.y_range.high_setting, 'auto')


    def test_clip_data(self):
        r = DataRange2D(low=[2.0,5.0], high=[10.0,8.0])
        x= arange(10.0)
        y= arange(0.,20.,2.)
        ary= transpose(array([x,y]))
        assert_equal(r.clip_data(ary) , array([[3.,6.],[4.,8.]]))

        r = DataRange2D(low=[10.,10.], high=[20.,20.])
        x= arange(10.0,30.,2.)
        y= arange(0.,40.,4.)
        ary = transpose(array([x,y]))
        assert_equal(r.clip_data(ary) , array([[16.,12.],[18.,16.],[20.,20.]]))
        assert_equal(r.clip_data(ary[::-1]) , array([[20,20], [18,16], [16,12]]))

    def test_mask_data(self):
        r = DataRange2D(low=[2.0,5.0], high=[10.0,18.0])
        x = array([1, 3, 4, 9.8, 10.2, 12])
        y = array([5, 3, 7, 12, 18, 6])
        ary = transpose(array([x,y]))
        assert_equal(r.mask_data(ary) , array([0,0,1,1,0,0], 'b'))

        r = DataRange2D(low=[10.,15.], high=[20.,25.])
        x = array([5, 10, 15, 20, 25, 30])
        y = array([5, 10, 15, 20, 25, 30])
        ary = transpose(array([x,y]))
        target_mask = array([0,0,1,1,0,0], 'b')
        assert_equal(r.mask_data(ary) , target_mask)
        assert_equal(r.mask_data(ary[::-1]) , target_mask[::-1])

        r = DataRange2D(low=[2.0,5.0], high=[2.5,9.0])
        assert_equal(r.mask_data(ary) , zeros(len(ary)))


def assert_close_(desired,actual):
    diff_allowed = 1e-5
    diff = abs(ravel(actual) - ravel(desired))
    for d in diff:
        if not isinf(d):
            assert_(alltrue(d <= diff_allowed))
            return

def assert_ary_(desired, actual):
    if (desired == 'auto'):
        assert_equal(actual, 'auto')
    for d in range(len(desired)):
        assert_equal(desired[d], actual[d])
