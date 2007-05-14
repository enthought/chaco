
import pdb, unittest
from numpy import array, arange, nan

from enthought.util.testingx import *

from enthought.chaco2.api import ArrayDataSource, DataRange1D, LogMapper

class LogMapperTestCase(unittest.TestCase):
    
    def test_basic(self):
        ary = array([1.0, 10.0, 100.0, 1000.0, 10000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=50, high_pos=90)
        result = mapper.map_screen(ary)
        pdb
        assert_equal(result, array([50, 60, 70, 80, 90]))
        return

    def test_reversed(self):
        ary = array([1.0, 10.0, 100.0, 1000.0, 10000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=100, high_pos=0)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, array([100, 75, 50, 25, 0]))
        return

    def test_fractional(self):
        ary = array([0.0001, 0.001, 0.01])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=20)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 10, 20])
        return

    def test_zero(self):
        ary = array([0.0, 1.0, 10.0, 100.0, 1000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=30)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 0, 10, 20, 30])
        return

    def test_negative(self):
        ary = array([1.0, -1.0, -2.0, 10.0, 100.0, 1000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=30)
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 0, 0, 10, 20, 30])
        return

    def test_fill_value(self):
        ary = array([1.0, -1.0, -2.0, 10.0, 100.0, 1000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=30)
        # This causes out-of-bounds values to be treated as the value 100.0
        mapper.fill_value = 100.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 20, 20, 10, 20, 30])
        return

    def test_nan(self):
        ary = array([1.0, nan, 10.0, nan, 100.0, 1000.0])
        ds = ArrayDataSource(ary)
        r = DataRange1D(ds)
        mapper = LogMapper(range=r, low_pos=0, high_pos=30)
        mapper.fill_value = 100.0
        result = mapper.map_screen(ary)
        assert_array_almost_equal(result, [0, 20, 10, 20, 20, 30])
        return
        

def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(LogMapperTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()


# EOF
