
import unittest2 as unittest

from numpy import alltrue, array, ravel, isinf
from numpy.testing import assert_array_equal, assert_almost_equal

from chaco.api import GridDataSource
from traits.testing.unittest_tools import UnittestTools


class GridDataSourceTestCase(UnittestTools, unittest.TestCase):

    def test_empty(self):
        data_source = GridDataSource()
        self.assertEqual(data_source.sort_order, ('none', 'none'))
        self.assertEqual(data_source.index_dimension, 'image')
        self.assertEqual(data_source.value_dimension, 'scalar')
        self.assertEqual(data_source.metadata,
                         {"selections":[], "annotations":[]})
        xdata, ydata = data_source.get_data()
        assert_array_equal(xdata.get_data(), array([]))
        assert_array_equal(ydata.get_data(), array([]))
        self.assertEqual(data_source.get_bounds(), ((0,0),(0,0)))

    def test_init(self):
        test_xd = array([1,2,3])
        test_yd = array([1.5, 0.5, -0.5, -1.5])
        test_sort_order = ('ascending', 'descending')

        data_source = GridDataSource(xdata=test_xd, ydata=test_yd,
                                     sort_order=test_sort_order)

        self.assertEqual(data_source.sort_order, test_sort_order)
        xd, yd = data_source.get_data()
        assert_array_equal(xd.get_data(), test_xd)
        assert_array_equal(yd.get_data(), test_yd)
        self.assertEqual(data_source.get_bounds(),
                         ((min(test_xd),min(test_yd)),
                          (max(test_xd),max(test_yd))))

    def test_set_data(self):
        data_source = GridDataSource(xdata=array([1,2,3]),
                                     ydata=array([1.5, 0.5, -0.5, -1.5]),
                                     sort_order=('ascending', 'descending'))

        test_xd = array([0,2,4])
        test_yd = array([0,1,2,3,4,5])
        test_sort_order = ('none', 'none')

        data_source.set_data(xdata=test_xd, ydata=test_yd,
                             sort_order=('none', 'none'))

        self.assertEqual(data_source.sort_order, test_sort_order)
        xd, yd = data_source.get_data()
        assert_array_equal(xd.get_data(), test_xd)
        assert_array_equal(yd.get_data(), test_yd)
        self.assertEqual(data_source.get_bounds(),
                         ((min(test_xd),min(test_yd)),
                          (max(test_xd),max(test_yd))))

    def test_metadata(self):
        data_source = GridDataSource(xdata=array([1,2,3]),
                                     ydata=array([1.5, 0.5, -0.5, -1.5]),
                                     sort_order=('ascending', 'descending'))

        self.assertEqual(data_source.metadata,
                         {'annotations': [], 'selections': []})

    def test_metadata_changed(self):
        data_source = GridDataSource(xdata=array([1,2,3]),
                                     ydata=array([1.5, 0.5, -0.5, -1.5]),
                                     sort_order=('ascending', 'descending'))

        with self.assertTraitChanges(data_source, 'metadata_changed', count=1):
            data_source.metadata = {'new_metadata': True}

    def test_metadata_items_changed(self):
        data_source = GridDataSource(xdata=array([1,2,3]),
                                     ydata=array([1.5, 0.5, -0.5, -1.5]),
                                     sort_order=('ascending', 'descending'))

        with self.assertTraitChanges(data_source, 'metadata_changed', count=1):
            data_source.metadata['new_metadata'] = True



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
