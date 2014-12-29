""" Needed Tests

    Component.draw_border() tests
    --------------------
        DONE *. draw_border output should match a similar draw_rect output
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import nose
import unittest

from numpy import array, alltrue, ravel

# Chaco imports
from chaco.plot import Plot
from chaco.plot_graphics_context import PlotGraphicsContext


class DrawBorderTestCase(unittest.TestCase):
    def assertRavelEqual(self, x, y):
        self.assert_(alltrue(ravel(x) == ravel(y)), "\n%s\n !=\n%s" % (x, y))

    def test_draw_border_simple(self):
        """ Borders should have the correct height and width.
        """
        size = (5,5)
        container = Plot(padding=1, border_visible=True)
        container.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(container)

        desired = array(((255, 255, 255, 255, 255, 255),
                         (255,   0,   0,   0,   0, 255),
                         (255,   0, 255, 255,   0, 255),
                         (255,   0, 255, 255,   0, 255),
                         (255,   0,   0,   0,   0, 255),
                         (255, 255, 255, 255, 255, 255)))

        actual = gc.bmp_array[:,:,0]
        self.assertRavelEqual(actual, desired)


if __name__ == "__main__":
    unittest.main()
