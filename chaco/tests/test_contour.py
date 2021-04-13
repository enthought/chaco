import unittest

import numpy as np
import numpy.testing as nptest

from chaco.contour.contour import Cntr


class TestContour(unittest.TestCase):
    def test_contour_trace_levels_no_mask(self):
        # Given
        xs = np.array([0, 1, 2, 3])
        ys = np.array([10, 20, 30, 40])
        xg, yg = np.meshgrid(xs, ys)
        data = np.array(
            [[0, 0, 1, 2], [0, 1, 2, 3], [1, 2, 0, 3], [2, 3, 3, 3]]
        )
        mask = np.ones(data.shape, dtype=bool)

        # When
        c = Cntr(xg, yg, data, ~mask)

        # Then
        levels = c.trace(0.0)
        self.assertEqual(len(levels), 2)
        self._check_level(
            levels[0], [1.0, 1.0, 0.0, 0.0], [10.0, 10.0, 20.0, 20.0]
        )
        self._check_level(
            levels[1],
            [2.0, 2.0, 2.0, 2.0, 2.0],
            [30.0, 30.0, 30.0, 30.0, 30.0],
        )

        levels = c.trace(1.0)
        self.assertEqual(len(levels), 2)
        self._check_level(
            levels[0],
            [2.0, 2.0, 1.0, 1.0, 0.0, 0.0],
            [10.0, 10.0, 20.0, 20.0, 30.0, 30.0],
        )

        self._check_level(
            levels[1],
            [2.0, 1.5, 2.0, 2.33333333, 2.0],
            [25.0, 30.0, 33.33333333, 30.0, 25.0],
        )

        levels = c.trace(2.0)
        self.assertEqual(len(levels), 1)
        self._check_level(
            levels[0],
            [3.0, 2.0, 2.66666667, 2.0, 1.0, 0.0],
            [10.0, 20.0, 30.0, 36.66666667, 30.0, 40.0],
        )

        levels = c.trace(2.5)
        self.assertEqual(len(levels), 1)
        self._check_level(
            levels[0],
            [3.0, 2.5, 2.83333333, 2.0, 1.0, 0.5],
            [15.0, 20.0, 30.0, 38.33333333, 35.0, 40.0],
        )

        # Note: the level for z = 3.0 lies entirely on the boundary of the
        # domain and the tracer will not pick it up.
        levels = c.trace(3.0)
        self.assertEqual(len(levels), 0)

    def _check_level(self, level, expected_x, expected_y):
        level_x, level_y = level
        nptest.assert_allclose(level_x, expected_x)
        nptest.assert_allclose(level_y, expected_y)

    def test_contour_init_bad_datatype(self):
        # Given
        xs = np.array([0])
        ys = np.array([1])
        xg, yg = np.meshgrid(xs, ys)
        data = np.array([[3]])

        mask_bad_datatype = np.ones(data.shape, dtype=np.uint8)

        # When/then
        with self.assertRaises(TypeError):
            Cntr(xg, yg, data, mask_bad_datatype)
