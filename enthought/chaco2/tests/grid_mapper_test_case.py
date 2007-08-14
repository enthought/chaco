
import pdb, unittest
from numpy import array, arange, transpose

from enthought.util.testingx import *

from enthought.chaco2.api import GridDataSource, DataRange2D, GridMapper

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

#    def test_reversed(self):
#        x_ary = array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
#        ds = GridDataSource(ary)
#        r = DataRange2D(ds)
#        mapper = GridMapper(range=r, low_pos=100, high_pos=0)
#        result = mapper.map_screen(ary)
#        assert_equal(result , array([100, 80, 60, 40, 20, 0]))
#        return


def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(GridMapperTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()


# EOF
