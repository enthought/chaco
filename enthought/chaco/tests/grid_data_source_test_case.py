
import unittest

from numpy import alltrue, array, ravel, isinf

from enthought.chaco.api import GridDataSource


class GridDataSourceTestCase(unittest.TestCase):

    def test_empty(self):
        ds = GridDataSource()
        self.assert_(ds.sort_order == ('none', 'none'))
        self.assert_(ds.index_dimension == 'image')
        self.assert_(ds.value_dimension == 'scalar')
        self.assert_(ds.metadata == {"selections":[], "annotations":[]})
        xdata, ydata = ds.get_data()
        assert_ary_(xdata.get_data(), array([]))
        assert_ary_(ydata.get_data(), array([]))
        self.assert_(ds.get_bounds() == ((0,0),(0,0)))

    def test_init(self):
        test_xd = array([1,2,3])
        test_yd = array([1.5, 0.5, -0.5, -1.5])
        test_sort_order = ('ascending', 'descending')

        ds = GridDataSource(xdata=test_xd, ydata=test_yd,
                            sort_order=test_sort_order)

        self.assert_(ds.sort_order == test_sort_order)
        xd, yd = ds.get_data()
        assert_ary_(xd.get_data(), test_xd)
        assert_ary_(yd.get_data(), test_yd)
        self.assert_(ds.get_bounds() == ((min(test_xd),min(test_yd)),
                                         (max(test_xd),max(test_yd))))

    def test_set_data(self):
        ds = GridDataSource(xdata=array([1,2,3]), 
                            ydata=array([1.5, 0.5, -0.5, -1.5]),
                            sort_order=('ascending', 'descending'))
        
        test_xd = array([0,2,4])
        test_yd = array([0,1,2,3,4,5])
        test_sort_order = ('none', 'none')

        ds.set_data(xdata=test_xd, ydata=test_yd, sort_order=('none', 'none'))

        self.assert_(ds.sort_order == test_sort_order)
        xd, yd = ds.get_data()
        assert_ary_(xd.get_data(), test_xd)
        assert_ary_(yd.get_data(), test_yd)
        self.assert_(ds.get_bounds() == ((min(test_xd),min(test_yd)),
                                         (max(test_xd),max(test_yd))))




def assert_close_(desired,actual):
    diff_allowed = 1e-5
    diff = abs(ravel(actual) - ravel(desired))
    for d in diff:
        if not isinf(d):
            assert alltrue(d <= diff_allowed)
            return
    
def assert_ary_(desired, actual):
    if (desired == 'auto'):
        assert actual == 'auto'
    for d in range(len(desired)):
        assert desired[d] == actual[d]
    return    


if __name__ == '__main__':
    import nose
    nose.run()
