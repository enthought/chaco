
import unittest
from numpy import array, transpose
from numpy.testing import assert_equal

from chaco.api import GridDataSource, DataRange2D, GridMapper

class GridMapperTestCase(unittest.TestCase):

    def setUp(self):
        self.x_ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        self.y_ary = array([1.0, 1.0, 2.0, 2.0, 3.0, 3.0])
        ds = GridDataSource(xdata=self.x_ary, ydata=self.y_ary)
        r = DataRange2D(ds)
        self.mapper = GridMapper(range=r)

    def test_basic(self):
        self.mapper.x_low_pos=50
        self.mapper.x_high_pos=100
        self.mapper.y_low_pos=0
        self.mapper.y_high_pos=10
        result = self.mapper.map_screen(transpose((self.x_ary, self.y_ary)))
        assert_equal(result, [(50,0), (60,0), (70,5),
                              (80,5), (90,10), (100,10)])

    def test_map_screen_scalar(self):
        self.mapper.x_low_pos=50
        self.mapper.x_high_pos=100
        self.mapper.y_low_pos=0
        self.mapper.y_high_pos=10
        result = self.mapper.map_screen(transpose((6.0, 1.0)))
        assert_equal(result, [[60, 0]])

    def test_map_data(self):
        self.mapper.x_low_pos=50
        self.mapper.x_high_pos=100
        self.mapper.y_low_pos=0
        self.mapper.y_high_pos=10
        screen_ary = array([(50,0), (60,0), (70,5), (80,5), (90,10), (100,10)])
        result = self.mapper.map_data(screen_ary)
        assert_equal(result, transpose((self.x_ary, self.y_ary)))

    def test_map_data_scalar(self):
        self.mapper.x_low_pos=50
        self.mapper.x_high_pos=100
        self.mapper.y_low_pos=0
        self.mapper.y_high_pos=10
        screen_ary = (60, 0)
        result = self.mapper.map_data(screen_ary)
        assert_equal(result, [[6.0, 1.0]])
