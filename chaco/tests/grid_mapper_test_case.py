
import unittest
from numpy import array, transpose
from numpy.testing import assert_equal

from chaco.api import GridDataSource, DataRange2D, GridMapper

class GridMapperTestCase(unittest.TestCase):

    def test_basic(self):
        x_ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        y_ary = array([1.0, 1.0, 2.0, 2.0, 3.0, 3.0])
        ds = GridDataSource(xdata=x_ary, ydata=y_ary)
        r = DataRange2D(ds)
        mapper = GridMapper(range=r)
        mapper.x_low_pos=50
        mapper.x_high_pos=100
        mapper.y_low_pos=0
        mapper.y_high_pos=10
        result = mapper.map_screen(transpose((x_ary, y_ary)))
        assert_equal(result, [(50,0), (60,0), (70,5),
                              (80,5), (90,10), (100,10)])


if __name__ == '__main__':
    import nose
    nose.run()
