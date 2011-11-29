
import unittest
from numpy import array, ndarray
from numpy.testing import assert_equal


from chaco.api import ArrayDataSource, DataRange1D, LinearMapper

class LinearMapperTestCase(unittest.TestCase):

    def test_basic(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, low_pos=50, high_pos=100)
        result = mapper.map_screen(ary)
        assert_equal(result , array([50, 60, 70, 80, 90, 100]))


    def test_reversed(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, low_pos=100, high_pos=0)
        result = mapper.map_screen(ary)
        assert_equal(result, array([100, 80, 60, 40, 20, 0]))


    def test_scalar(self):
        # test for bug: when passed a scalar, LinearMapper.map_screen returns
        # a scalar instead of an array with 1 element. This is inconsistent
        # with the behavior of LogMapper, and causes the code that relies
        # on it to raise exceptions (e.g., the example demo/shell/loglog.py
        # raises an exception when left-clicking)
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, low_pos=50, high_pos=100)
        result = mapper.map_screen(7.)
        self.assertEqual(type(result), ndarray)
        assert_equal(result, array([70]))

if __name__ == '__main__':
    import nose
    nose.run()
