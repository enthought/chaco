"""
Unit tests for utility functions in chaco.base
"""
import unittest
from math import sqrt
from numpy import arange, array, linspace, nan, ones
from numpy.testing import assert_equal, assert_almost_equal, assert_array_equal

from chaco.base import (arg_find_runs, arg_true_runs, bin_search, find_runs,
                       intersect_range, reverse_map_1d, point_line_distance)


class BinSearchTestCase(unittest.TestCase):
    def test_ascending_data(self):
        ary = arange(10.0)

        # inside bounds
        self.assertEqual(bin_search(ary, 0.0, 1), 0)
        self.assertEqual(bin_search(ary, 5.0, 1), 5)
        self.assertEqual(bin_search(ary, 9.0, 1), 9)

        # out of bounds
        self.assertEqual(bin_search(ary, 10.0, 1), -1)
        self.assertEqual(bin_search(ary, -1.0, 1), -1)
        self.assertEqual(bin_search(ary, 9.00001, 1), -1)
        self.assertEqual(bin_search(ary, -0.00001, 1), -1)

        # rounding
        self.assertEqual(bin_search(ary, 5.1, 1), 5)
        self.assertEqual(bin_search(ary, 4.9, 1), 4)

    def test_descending_data(self):
        ary = arange(10.0, 0.0, -1.0)

        # inside bounds
        self.assertEqual(bin_search(ary, 10.0, -1), 0)
        self.assertEqual(bin_search(ary, 5.0, -1), 5)
        self.assertEqual(bin_search(ary, 1.0, -1), 9)

        # out of bounds
        self.assertEqual(bin_search(ary, 10.1, -1), -1)
        self.assertEqual(bin_search(ary, 0.9, -1), -1)

        # rounding
        self.assertEqual(bin_search(ary, 5.1, -1), 4)
        self.assertEqual(bin_search(ary, 4.9, -1), 5)

class ReverseMap1DTestCase(unittest.TestCase):

    def test_ascending(self):
        ary = arange(10.0)
        rmap = lambda x: reverse_map_1d(ary, x, 'ascending')

        # inside bounds
        self.assertEqual(rmap(0.0), 0)
        self.assertEqual(rmap(5.0), 5)
        self.assertEqual(rmap(9.0), 9)

        # out of bounds
        self.assertRaises(IndexError, rmap, 10.0)
        self.assertRaises(IndexError, rmap, -1.0)

        # rounding
        self.assertEqual(rmap(3.4), 3)
        self.assertEqual(rmap(3.5), 3)
        self.assertEqual(rmap(3.6), 4)
        return

    def test_ascending_floor(self):
        ary = arange(10.0)
        rmap = lambda x: reverse_map_1d(ary, x, 'ascending', floor_only=True)

        # test rounding
        self.assertEqual(rmap(3.4), 3)
        self.assertEqual(rmap(3.5), 3)
        self.assertEqual(rmap(3.6), 3)
        return

    def test_descending(self):
        ary = arange(10.0, 0.0, -1.0)
        rmap = lambda x: reverse_map_1d(ary, x, 'descending')

        # inside bounds
        self.assertEqual(rmap(10.0), 0)
        self.assertEqual(rmap(5.0), 5)
        self.assertEqual(rmap(1.0), 9)

        # out of bounds
        self.assertRaises(IndexError, rmap, 0.0)
        self.assertRaises(IndexError, rmap, 11.0)

        # rounding
        self.assertEqual(rmap(8.6), 1)
        self.assertEqual(rmap(8.5), 1)
        self.assertEqual(rmap(8.4), 2)
        return

    def test_descending_floor(self):
        ary = arange(10.0, 0.0, -1.0)
        rmap = lambda x: reverse_map_1d(ary, x, 'descending', floor_only=True)

        # test rounding
        self.assertEqual(rmap(8.6), 1)
        self.assertEqual(rmap(8.5), 1)
        self.assertEqual(rmap(8.4), 1)
        return


class FindRunsTestCase(unittest.TestCase):
    def test_find_runs_middle(self):
        x = array([0, 8, 7, 8, 9, 2, 3, 4, 10])
        assert_equal(find_runs(x), [[0], [8], [7, 8, 9], [2, 3, 4], [10]])

    def test_find_runs_start(self):
        x = array([3, 4, 5, 12, 9, 17])
        assert_equal(find_runs(x), [[3, 4, 5], [12], [9], [17]])

    def test_find_runs_end(self):
        x = array([18, 23, 24, 25])
        assert_equal(find_runs(x) , [[18], [23, 24, 25]])

    def test_find_runs_offset(self):
        # because of the nature of the find_runs algorithm, there may be
        # fencepost errors with runs that start at x[1] or x[-2]
        x = array([10, 12, 13, 14, 28, 16])
        assert_equal(find_runs(x), [[10], [12, 13, 14], [28], [16]])
        x = array([10, 15, 16, 17, 34])
        assert_equal(find_runs(x), [[10], [15, 16, 17], [34]])

    def test_find_runs_none(self):
        x = array([])
        assert_equal(find_runs(x), [])
        x = array([12, 15, 27])
        assert_equal(find_runs(x), [[12], [15], [27]])

    def test_find_runs_descending(self):
        x = array([30, 41, 40, 39, 38, 37, 12])
        assert_equal(find_runs(x, order='descending'), \
                    [[30], [41, 40, 39, 38, 37], [12]])

    def test_find_runs_flat(self):
        x = array([0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0])
        assert_equal(find_runs(x, order='flat'), \
                     [[0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]])


class ArgFindRunsTestCase(unittest.TestCase):
    def test_arg_find_runs_middle(self):
        x = array([0, 8, 7, 8, 9, 2, 3, 4, 10])
        assert_equal(arg_find_runs(x),
                     [[0, 1], [1, 2], [2, 5], [5, 8], [8, 9]])

    def test_arg_find_runs_start(self):
        x = array([3, 4, 5, 12, 9, 17])
        assert_equal(arg_find_runs(x) , [[0, 3], [3, 4], [4, 5], [5, 6]])

    def test_arg_find_runs_end(self):
        x = array([18, 23, 24, 25])
        assert_equal(arg_find_runs(x) , [[0, 1], [1, 4]])

    def test_arg_find_runs_offset(self):
        # because of the nature of the find_runs algorithm, there may be
        # fencepost errors with runs that start at x[1] or x[-2]
        x = array([10, 12, 13, 14, 28, 16])
        assert_equal(arg_find_runs(x) , [[0, 1], [1, 4], [4, 5], [5, 6]])
        x = array([10, 15, 16, 17, 34])
        assert_equal(arg_find_runs(x) , [[0, 1], [1, 4], [4, 5]])

    def test_arg_find_runs_none(self):
        x = array([])
        assert_equal(arg_find_runs(x) , [])
        x = array([12, 15, 27])
        assert_equal(arg_find_runs(x) , [[0, 1], [1, 2], [2, 3]])

    def test_arg_find_runs_descending(self):
        x = array([30, 41, 40, 39, 38, 37, 12])
        assert_equal(arg_find_runs(x, order='descending'), \
                     [[0, 1], [1, 6], [6, 7]])

    def test_arg_find_runs_flat(self):
        x = array([0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0])
        assert_equal(arg_find_runs(x, order='flat'), \
                     [[0, 3], [3, 7], [7, 11]])


class TestArgTrueRuns(unittest.TestCase):

      def test_none(self):
        x = array([], dtype=bool)
        assert_equal(arg_true_runs(x), [])

      def test_even(self):
        x = array([1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0], dtype=bool)
        assert_equal(arg_true_runs(x), [[0, 3], [7, 9]])

      def test_odd(self):
        x = array([0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1], dtype=bool)
        assert_equal(arg_true_runs(x), [[3, 7], [9, 11]])

      def test_all_true(self):
        x = array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=bool)
        assert_equal(arg_true_runs(x), [[0, 11]])

      def test_all_false(self):
        x = array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=bool)
        assert_equal(arg_true_runs(x), [])



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


class IntersectRangeTestCase(unittest.TestCase):

    # zero point test

    def test_empty(self):
        x = array([])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [])

    # single point tests

    def test_in(self):
        x = array([0.5])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True])

    def test_lower_bound(self):
        x = array([0.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True])

    def test_upper_bound(self):
        x = array([1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True])

    def test_low(self):
        x = array([-1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False])

    def test_high(self):
        x = array([2.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False])

    # two point tests

    def test_low_low(self):
        x = array([-2.0, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False]*2)

    def test_low_in(self):
        x = array([-1.0, 0.5])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*2)

    def test_low_lower_bound(self):
        x = array([-1.0, 0.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*2)

    def test_low_high(self):
        x = array([-2.0, 2.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*2)

    def test_in_in(self):
        x = array([0.75, 0.5])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*2)

    def test_in_high(self):
        x = array([-0.5, 2.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*2)

    def test_high_low(self):
        x = array([2.0, -2.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*2)

    def test_high_high(self):
        x = array([3.0, 2.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False]*2)

    # three point tests

    def test_low_low_low(self):
        x = array([-3.0, -2.0, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False]*3)

    def test_in_low_low(self):
        x = array([0.5, -2.0, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, True, False])

    def test_high_low_low(self):
        x = array([2.0, -2.0, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, True, False])

    def test_low_in_low(self):
        x = array([-3.0, 0.5, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_in_in_low(self):
        x = array([0.75, 0.5, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_high_in_low(self):
        x = array([2.0, 0.5, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_low_high_low(self):
        x = array([-3.0, 2, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_in_high_low(self):
        x = array([0.5, 2, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_high_high_low(self):
        x = array([2.5, 2, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False, True, True])

    def test_low_low_in(self):
        x = array([-3.0, -2.0, 0.5])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False, True, True])

    def test_in_low_in(self):
        x = array([0.5, -2.0, 0.5])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, True, True])

    def test_high_low_in(self):
        x = array([2.0, -2.0, 0.5])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, True, True])

    def test_low_in_in(self):
        x = array([-3.0, 0.5, 0.75])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_in_in_in(self):
        x = array([0.75, 0.5, 0.25])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_high_in_in(self):
        x = array([2.0, 0.5, 0.75])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_low_high_in(self):
        x = array([-3.0, 2, 0.5])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_in_high_in(self):
        x = array([0.5, 2, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_high_high_in(self):
        x = array([2.5, 2, 0.5])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False, True, True])

    def test_low_low_high(self):
        x = array([-3.0, -2.0, 2])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False, True, True])

    def test_in_low_high(self):
        x = array([0.5, -2.0, 2])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, True, True])

    def test_high_low_high(self):
        x = array([2.0, -2.0, 2])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, True, True])

    def test_low_in_high(self):
        x = array([-3.0, 0.5, 2])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_in_in_high(self):
        x = array([0.75, 0.5, 2])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_high_in_high(self):
        x = array([2.0, 0.5, 2])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True]*3)

    def test_low_high_high(self):
        x = array([-3.0, 2, 3])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, True, False])

    def test_in_high_high(self):
        x = array([0.5, 2, 3])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, True, False])

    def test_high_high_high(self):
        x = array([2.5, 2, 3])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False, False, False])

    # some mask tests (not comprehensive)

    def test_mask_low_low(self):
        x = array([1, 2, 3])
        mask = array([False, True, True])
        result = intersect_range(x, 0.0, 1.0, mask)
        assert_array_equal(result, [False, False, False])

    def test_mask_high_low(self):
        x = array([1, 2, -1.0])
        mask = array([False, True, True])
        result = intersect_range(x, 0.0, 1.0, mask)
        assert_array_equal(result, [False, True, True])

    def test_in_mask_low(self):
        x = array([0.5, 0, -1.0])
        mask = array([True, False, True])
        result = intersect_range(x, 0.0, 1.0, mask)
        assert_array_equal(result, [True, False, False])

    def test_in_mask_in(self):
        x = array([0.5, 0.25, 0.75])
        mask = array([True, False, True])
        result = intersect_range(x, 0.0, 1.0, mask)
        assert_array_equal(result, [True, False, True])

    def test_in_low_mask(self):
        x = array([0.5, -1.0, 0.5])
        mask = array([True, True, False])
        result = intersect_range(x, 0.0, 1.0, mask)
        assert_array_equal(result, [True, True, False])

    def test_low_low_mask(self):
        x = array([-0.5, -1.0, 0.5])
        mask = array([True, True, False])
        result = intersect_range(x, 0.0, 1.0, mask)
        assert_array_equal(result, [False, False, False])

    # some nan tests (not comprehensive)

    def test_nan_low_low(self):
        x = array([nan, 2, 3])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False, False, False])

    def test_nan_high_low(self):
        x = array([nan, 2, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False, True, True])

    def test_in_nan_low(self):
        x = array([0.5, nan, -1.0])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, False, False])

    def test_in_nan_in(self):
        x = array([0.5, nan, 0.75])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, False, True])

    def test_in_low_nan(self):
        x = array([0.5, -1.0, nan])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [True, True, False])

    def test_low_low_nan(self):
        x = array([-0.5, -1.0, nan])
        result = intersect_range(x, 0.0, 1.0)
        assert_array_equal(result, [False, False, False])

    # other tests

    def test_all_inside(self):
        x = linspace(1, 2, 101)
        result = intersect_range(x, 0.0, 3.0)
        assert_array_equal(result, ones(101, dtype=bool))

    def test_all_inside_mask(self):
        x = linspace(1, 2, 101)
        mask = (x <= 1.4) | (x >= 1.6)
        result = intersect_range(x, 0.0, 3.0, mask)
        assert_array_equal(result, mask)
