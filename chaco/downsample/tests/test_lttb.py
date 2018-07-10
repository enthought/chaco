import unittest
import timeit

import numpy as np
from numpy.testing import assert_array_equal, assert_almost_equal

from ..lttb import largest_triangle_three_buckets


TIMING_SETUP = """
import numpy as np
from chaco.downsample.lttb import largest_triangle_three_buckets

a = np.empty(shape=(1000001,2))
a[:, 0] = np.linspace(0, 10*np.pi, 1000001)
a[:, 1] = np.sin(a[:, 0])
n_buckets = 1000
"""


class TestLargestTriangleThreeBuckets(unittest.TestCase):

    def test_timing(self):
        statement = 'largest_triangle_three_buckets(a, n_buckets)'

        timer = timeit.Timer(statement, setup=TIMING_SETUP)

        t = min(timer.repeat(repeat=3, number=100))/100.

        # Fairly arbitrary, but if we can't do a million points in 0.1 seconds
        # then this isn't worth it.  A capable machine should be able to do
        # about 10 times better than that limit.
        # For reference:
        #    Time               Notes
        #    0.0112847280502    2016/10/18, 2.8 GHz 16 GB mid-2014 MacBook Pro
        self.assertLess(t, 0.1)

    def test_linear(self):
        a = np.empty(shape=(101,2))
        a[:, 0] = np.linspace(0.0, 10.0, 101)
        a[:, 1] = np.linspace(0.0, 10.0, 101)
        n_buckets = 12

        result = largest_triangle_three_buckets(a, n_buckets)

        self.assertEqual(result.shape, (12, 2))
        assert_almost_equal(result, [
            [0.0, 0.0],
            [0.1, 0.1],
            [1.0, 1.0],
            [2.0, 2.0],
            [3.0, 3.0],
            [4.0, 4.0],
            [5.0, 5.0],
            [6.0, 6.0],
            [7.0, 7.0],
            [8.0, 8.0],
            [9.0, 9.0],
            [10.0, 10.0],
        ])

    def test_spike(self):
        a = np.empty(shape=(31,2))
        a[:, 0] = np.linspace(0.0, 3.0, 31)
        a[:, 1] = np.linspace(0.0, 3.0, 31)
        a[15, 1] = 100.0
        n_buckets = 5

        result = largest_triangle_three_buckets(a, n_buckets)

        self.assertEqual(result.shape, (5, 2))
        assert_almost_equal(result, [
            [0.0, 0.0],
            [0.9, 0.9],
            [1.5, 100],
            [2.0, 2.0],
            [3.0, 3.0],
        ])

    def test_concave_up(self):
        a = np.empty(shape=(101,2))
        a[:, 0] = np.linspace(0.0, 10.0, 101)
        a[:, 1] = np.linspace(0.0, 10.0, 101)**2
        n_buckets = 12

        result = largest_triangle_three_buckets(a, n_buckets)

        expected_points = np.array(
            [0.0, 0.8, 1.7, 2.6, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.2, 10.0]
        )
        self.assertEqual(result.shape, (12, 2))
        assert_almost_equal(result[:, 0], expected_points)

    def test_concave_down(self):
        a = np.empty(shape=(101,2))
        a[:, 0] = np.linspace(0.0, 10.0, 101)
        a[:, 1] = -np.linspace(0.0, 10.0, 101)**2
        n_buckets = 12

        result = largest_triangle_three_buckets(a, n_buckets)

        expected_points = np.array(
            [0.0, 0.8, 1.7, 2.6, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.2, 10.0]
        )
        self.assertEqual(result.shape, (12, 2))
        assert_almost_equal(result[:, 0], expected_points)
        assert_almost_equal(result[:, 1], -expected_points**2)

    def test_empty(self):
        a = np.zeros(shape=(0,2))
        n_buckets = 0

        result = largest_triangle_three_buckets(a, n_buckets)

        self.assertEqual(result.shape, (0, 2))

    def test_negative_buckets(self):
        a = np.zeros(shape=(10,2))
        n_buckets = -10

        result = largest_triangle_three_buckets(a, n_buckets)

        assert_array_equal(result, a)

    def test_zero_buckets(self):
        a = np.zeros(shape=(10,2))
        n_buckets = 0

        result = largest_triangle_three_buckets(a, n_buckets)

        assert_array_equal(result, a)

    def test_single_bucket(self):
        a = np.zeros(shape=(10,2))
        n_buckets = 1

        result = largest_triangle_three_buckets(a, n_buckets)

        assert_array_equal(result, a)

    def test_two_buckets(self):
        a = np.zeros(shape=(10,2))
        n_buckets = 2

        result = largest_triangle_three_buckets(a, n_buckets)

        assert_array_equal(result, a)

    def test_three_buckets(self):
        a = np.zeros(shape=(10,2))
        n_buckets = 3

        result = largest_triangle_three_buckets(a, n_buckets)

        assert_array_equal(result, [[0.0, 0.0]]*3)
