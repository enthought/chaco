
import pdb, unittest
from numpy import array, arange

from enthought.util.testingx import *

from enthought.chaco2.api import ArrayDataSource, DataRange1D, LinearMapper

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


def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(LinearMapperTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()


# EOF
