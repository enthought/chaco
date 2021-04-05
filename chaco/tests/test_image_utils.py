import unittest

from numpy.testing import assert_allclose, assert_equal

from chaco.image_utils import trim_screen_rect, X_PARAMS, Y_PARAMS


SINGLE_PIXEL = (1, 1)
FOUR_PIXELS = (2, 2)


def midpoint(x, length):
    return x + length / 2.0


def assert_midpoints_equal(bounds_list):

    for i_pos, i_length in (X_PARAMS, Y_PARAMS):
        x_mid = [midpoint(bnd[i_pos], bnd[i_length]) for bnd in bounds_list]
        assert_equal(x_mid[0], x_mid[1])


class TestImageUtils(unittest.TestCase):
    def test_viewer_zoomed_into_single_pixel(self):
        screen_rect = [0, 0, 100, 100]
        view_rect = [10, 11, 1, 2]
        new_rect = trim_screen_rect(screen_rect, view_rect, SINGLE_PIXEL)
        assert_allclose(new_rect, view_rect)

    def test_viewer_at_corner_of_single_image(self):
        offset = 0.2
        screen_rect = [1, 1, 1, 1]
        new_size = [1 - offset, 1 - offset]

        down_right = [1 + offset, 1 + offset, 1, 1]
        new_rect = trim_screen_rect(screen_rect, down_right, SINGLE_PIXEL)
        expected_rect = down_right[:2] + new_size
        assert_midpoints_equal((new_rect, expected_rect))

        up_left = [1 - offset, 1 - offset, 1, 1]
        new_rect = trim_screen_rect(screen_rect, up_left, SINGLE_PIXEL)
        expected_rect = [1, 1] + new_size
        assert_midpoints_equal((new_rect, expected_rect))

    def test_viewer_zoomed_into_four_pixel_intersection(self):
        screen_rect = [0, 0, 100, 100]  # 4-pixel intersection at (50, 50)
        view_rectangles = (
            [49, 49, 2, 2],  # Centered pixel intersection
            [49, 49, 3, 3],  # Intersection at 1/3 of view
            [49, 49, 2, 3],  # Intersection at 1/2, 1/3 of view
        )
        for view_rect in view_rectangles:
            new_rect = trim_screen_rect(screen_rect, view_rect, FOUR_PIXELS)
            assert_midpoints_equal((new_rect, screen_rect))

    def test_viewer_at_corner_of_four_pixel_image(self):
        offset = 0.2
        screen_rect = [1, 1, 1, 1]
        view_rectangles = (
            [1 + offset, 1 + offset, 1, 1],  # Shifted down and right
            [1 - offset, 1 - offset, 1, 1],  # Shifted up and left
        )
        for view_rect in view_rectangles:
            new_rect = trim_screen_rect(screen_rect, view_rect, FOUR_PIXELS)
            assert_equal(new_rect, screen_rect)
