
import unittest
from numpy import array
from numpy.testing import assert_array_almost_equal, assert_equal


from chaco.api import ArrayDataSource, DataRange1D, LinearMapper

class LinearMapperTestCase(unittest.TestCase):

    def test_basic(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, low_pos=50, high_pos=100)
        result = mapper.map_screen(ary)
        assert_equal(result , array([50, 60, 70, 80, 90, 100]))
        return

    def test_reversed(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, low_pos=100, high_pos=0)
        result = mapper.map_screen(ary)
        assert_equal(result , array([100, 80, 60, 40, 20, 0]))
        return

    def test_update_screen_bounds_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.screen_bounds = (40.0, 120.0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([40.0, 56.0, 72.0, 88.0, 104.0, 120.0]))

    def test_update_screen_bounds_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.screen_bounds = (40.0, 120.0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([40.0, 50.0, 60.0, 70.0, 80.0, 90.0]))

    def test_reversed_update_screen_bounds_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 0.0)
        mapper.screen_bounds = (120.0, -10.0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([120.0, 94.0, 68.0, 42.0, 16.0, -10.0]))

    def test_reversed_update_screen_bounds_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 0.0)
        mapper.screen_bounds = (120.0, -10.0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(
            result, array([120.0, 100.0, 80.0, 60.0, 40.0, 20.0]))

    def test_update_low_pos_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.low_pos = 40.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([40, 52, 64, 76, 88, 100]))

    def test_update_low_pos_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.low_pos = 40.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([40, 50, 60, 70, 80, 90]))

    def test_reversed_update_low_pos_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 50.0)
        mapper.low_pos = 110.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([110, 98, 86, 74, 62, 50]))

    def test_reversed_update_low_pos_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 50.0)
        mapper.low_pos = 110.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([100, 90, 80, 70, 60, 50]))

    def test_update_high_pos_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.high_pos = 110.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([50, 62, 74, 86, 98, 110]))

    def test_update_high_pos_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (50.0, 100.0)
        mapper.high_pos = 110.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([50, 60, 70, 80, 90, 100]))

    def test_reversed_update_high_pos_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=True)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 50.0)
        mapper.high_pos = 40.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([100, 88, 76, 64, 52, 40]))

    def test_reversed_update_high_pos_dont_stretch_data(self):
        ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LinearMapper(range=r, stretch_data=False)
        # Initialize the bounds, then modify them.
        mapper.screen_bounds = (100.0, 50.0)
        mapper.high_pos = 40.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([90, 80, 70, 60, 50, 40]))



if __name__ == '__main__':
    import nose
    nose.run()
