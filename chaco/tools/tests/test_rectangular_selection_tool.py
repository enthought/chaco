import unittest

import numpy as np

from chaco.array_plot_data import ArrayPlotData
from chaco.plot import Plot
from chaco.tools.rectangular_selection import RectangularSelection
from enable.testing import EnableTestAssistant


class RectangularSelectionTestCase(EnableTestAssistant, unittest.TestCase):
    def test_selection_mask(self):

        plot_data = ArrayPlotData()
        plot = Plot(plot_data)
        arr = np.array([-2, -1, 1, 2])
        plot_data.set_data("x", arr)
        plot_data.set_data("y", arr)
        splot = plot.plot(("x", "y"), type="scatter")[0]
        tool = RectangularSelection(
            component=splot,
            selection_datasource=splot.index,
            metadata_name="selections",
        )
        splot.tools.append(tool)

        # Set the cursor start and stop positions to be such
        # that the middle two points of the four possible are selected.
        cursor_start = splot.map_screen([-1.5, -1.5])[0]
        cursor_stop = splot.map_screen([1.5, 1.5])[0]

        self.mouse_down(interactor=tool, x=cursor_start[0], y=cursor_start[1])

        self.mouse_move(interactor=tool, x=cursor_stop[0], y=cursor_stop[1])

        self.mouse_up(interactor=tool, x=cursor_stop[0], y=cursor_stop[1])

        expected_mask = [False, True, True, False]
        selection_mask = list(splot.index.metadata["selections"])
        self.assertEqual(expected_mask, selection_mask)
