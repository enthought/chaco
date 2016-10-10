import unittest

import numpy as np

from chaco.array_plot_data import ArrayPlotData
from chaco.plot import Plot
from chaco.tools.range_selection import RangeSelection
from enable.testing import EnableTestAssistant


class RangeSelectionTestCase(EnableTestAssistant, unittest.TestCase):

    def test_selecting_mouse_leave_clipping(self):
        # Regression test for #216.
        plot_data = ArrayPlotData()
        arr = np.arange(4.0)
        plot_data.set_data("x", arr)
        plot_data.set_data("y", arr)

        for origin in ('bottom left', 'top left', 'bottom right', 'top right'):
            for orientation in ('h', 'v'):
                for axis in ('index', 'value'):
                    plot = Plot(
                        plot_data, orientation=orientation, origin='top right'
                    )

                    renderer = plot.plot(('x', 'y'))[0]
                    renderer.bounds = [10, 20]
                    tool = RangeSelection(
                        renderer, left_button_selects=True, axis=axis,
                    )
                    renderer.tools.append(tool)

                    low_x, low_y = plot.position
                    high_x = low_x + renderer.bounds[0] - 1
                    high_y = low_y + renderer.bounds[1] - 1

                    cx = 5
                    cy = 5

                    bounds = (
                        (low_x - 1, low_y),
                        (high_x + 1, low_y),
                        (low_x, low_y - 1),
                        (low_x, high_y + 1),
                    )
                    for x, y in bounds:
                        self.mouse_down(tool, x=cx, y=cy)
                        self.mouse_leave(tool, x=x, y=y)
                        selection = tool.selection
                        self.assertTrue(selection[0] <= selection[1])
                        self.mouse_up(tool, x=x, y=y)


if __name__ == '__main__':
    import nose
    nose.run()
