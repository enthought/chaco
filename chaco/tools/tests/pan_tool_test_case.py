import unittest

import numpy as np

from chaco.array_plot_data import ArrayPlotData
from chaco.plot import Plot
from chaco.tools.pan_tool import PanTool
from enable.testing import EnableTestAssistant


class PanToolTestCase(EnableTestAssistant, unittest.TestCase):

    def test_restrict_to_data_with_empty_source(self):
        # Regression test for #214.
        plot_data = ArrayPlotData()
        plot = Plot(plot_data)
        arr = np.arange(4.0)
        plot_data.set_data("x", arr)
        plot_data.set_data("y", arr)
        plot_data.set_data("z", np.array([], np.float64))
        plot.plot(('x', 'y'))
        plot.plot(('z', 'z'))
        tool = PanTool(plot, restrict_to_data=True)
        plot.tools.append(tool)

        x_range = plot.x_mapper.range
        y_range = plot.y_mapper.range

        x_bounds = (x_range.low, x_range.high)
        y_bounds = (y_range.low, y_range.high)
        self.mouse_down(tool, 0.0, 0.0)
        self.mouse_move(interactor=tool, x=1.0, y=1.0)
        self.mouse_up(interactor=tool, x=1.0, y=1.0)
        self.assertEqual((x_range.low, x_range.high), x_bounds)
        self.assertEqual((y_range.low, y_range.high), y_bounds)



if __name__ == '__main__':
    import nose
    nose.run()
