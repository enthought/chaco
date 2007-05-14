"""
Unit tests for utility functions in chaco2.base
"""

import unittest
from math import sqrt
from enthought.util.testingx import *
from numpy import arange, array
from enthought.chaco2.api import bin_search, find_runs, reverse_map_1d, point_line_distance

class BinSearchTestCase(unittest.TestCase):
    def test_ascending_data(self):
        ary = arange(10.0)
        # inside bounds
        self.assert_(bin_search(ary, 0.0, 1) == 0)
        self.assert_(bin_search(ary, 5.0, 1) == 5)
        self.assert_(bin_search(ary, 9.0, 1) == 9)
        # out of bounds
        self.assert_(bin_search(ary, 10.0, 1) == -1)
        self.assert_(bin_search(ary, -1.0, 1) == -1)
        self.assert_(bin_search(ary, 9.00001, 1) == -1)
        self.assert_(bin_search(ary, -0.00001, 1) == -1)
        # rounding
        self.assert_(bin_search(ary, 5.1, 1) == 5)
        self.assert_(bin_search(ary, 4.9, 1) == 4)
        return
    
    def test_descending_data(self):
        ary = arange(10.0, 0.0, -1.0)
        # inside bounds
        self.assert_(bin_search(ary, 10.0, -1) == 0)
        self.assert_(bin_search(ary, 5.0, -1) == 5)
        self.assert_(bin_search(ary, 1.0, -1) == 9)
        # out of bounds
        self.assert_(bin_search(ary, 10.1, -1) == -1)
        self.assert_(bin_search(ary, 0.9, -1) == -1)
        # rounding
        self.assert_(bin_search(ary, 5.1, -1) == 4)
        self.assert_(bin_search(ary, 4.9, -1) == 5)
        return

class ReverseMap1DTestCase(unittest.TestCase):
    # TODO: Implement these
    pass


class FindRunsTestCase(unittest.TestCase):
    def test_find_runs_middle(self):
        x = array([0,8,7,8,9,2,3,4,10])
        assert_equal(find_runs(x) , [[0], [8], [7,8,9], [2,3,4], [10]])
    
    def test_find_runs_start(self):
        x = array([3,4,5,12,9,17])
        assert_equal(find_runs(x) , [[3,4,5],[12],[9],[17]])
    
    def test_find_runs_end(self):
        x = array([18,23,24,25])
        assert_equal(find_runs(x) , [[18],[23,24,25]])
    
    def test_find_runs_offset(self):
        # because of the nature of the find_runs algorithm, there may be
        # fencepost errors with runs that start at x[1] or x[-2]
        x = array([10,12,13,14,28,16])
        assert_equal(find_runs(x) , [[10],[12,13,14],[28],[16]])
        x = array([10,15,16,17,34])
        assert_equal(find_runs(x) , [[10],[15,16,17],[34]])
    
    def test_find_runs_none(self):
        x = array([])
        assert_equal(find_runs(x) , [])
        x = array([12,15,27])
        assert_equal(find_runs(x) , [[12],[15],[27]])
    
    def test_find_runs_descending(self):
        x = array([30,41,40,39,38,37,12])
        assert_equal(find_runs(x, order='descending') , \
                            [[30], [41,40,39,38,37], [12]])


class PointLineDistanceTestCase(unittest.TestCase):

    def test_horizontal_line(self):
        p1 = (10.0, 10.0)
        p2 = (60.0, 10.0)
        test = (35.0, 30.0)
        dist = point_line_distance(test, p1, p2)
        assert_equal(dist, 20.0)

    def test_vertical_line(self):
        p1 = (10.0, 10.0)
        p2 = (10.0, 60.0)
        test = (30.0, 35.0)
        dist = point_line_distance(test, p1, p2)
        assert_equal(dist, 20.0)

    def test_diag_lines(self):
        p1 = (0.0, 0.0)
        p2 = (10.0, 10.0)
        test = (0.0, 5.0)
        dist = point_line_distance(test, p1, p2)
        assert_almost_equal(dist, 2.5 * sqrt(2.0))

    def test_point_on_line(self):
        p1 = (-5.0, 5.0)
        p2 = (10.0, -10.0)
        test = (3.0, -3.0)
        dist = point_line_distance(test, p1, p2)
        assert_almost_equal(dist, 0.0)
    


def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(BinSearchTestCase, "test_"))
    suites.append(unittest.makeSuite(FindRunsTestCase, "test_"))
    suites.append(unittest.makeSuite(PointLineDistanceTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()
