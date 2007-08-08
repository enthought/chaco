
import unittest

from numpy import alltrue, arange, array, ravel, transpose, ones, zeros, inf, isinf
from enthought.util.testingx import *

from enthought.chaco2.api import DataRange2D, DataView, GridDataSource 


class DataViewTestCase(unittest.TestCase):
    
    def test_empty(self):
        dv = DataView()
        self.assert_(dv.orientation=="h")
        self.assert_(dv.index_direction=="normal")
        self.assert_(dv.index_direction=="normal")
        self.assert_(dv.index_scale=="linear")
        self.assert_(dv.index_scale=="linear")
        self.assert_(dv.bgcolor=="white")
        self.assert_(dv.overlay_border==False)

        self.assert_(dv.range2d.x_range==dv.index_range)
        self.assert_(dv.range2d.y_range==dv.value_range)

    def test_orientation(self):
        dv = DataView()
        x_mapper_start = dv.x_mapper
        y_mapper_start = dv.y_mapper
        dv.orientation = "v"
        self.assert_(dv.x_mapper is y_mapper_start)
        self.assert_(dv.y_mapper is x_mapper_start)

    def test_range2d_changed(self):
        dv = DataView()
        ds = GridDataSource()
        dv.range2d.add(ds)
        old_range = dv.range2d
        r = DataRange2D()

        self.assert_(dv.range2d.sources==[ds])
        dv.range2d = r
        self.assert_(dv.range2d.sources==[ds])
        self.assert_(old_range.sources==[])
        self.assert_(dv.range2d.x_range is dv.index_mapper.range)
        self.assert_(dv.range2d.y_range is dv.value_mapper.range)

        


def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(DataViewTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

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



if __name__ == "__main__":
    test()



# EOF
