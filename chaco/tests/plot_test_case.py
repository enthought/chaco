import unittest

from numpy import arange

# Chaco imports
from chaco.api import ArrayPlotData, Plot, DataRange1D


class PlotTestCase(unittest.TestCase):

    def test_plot_from_unsupported_array_shape(self):
        arr = arange(8).reshape(2, 2, 2)
        data = ArrayPlotData(x=arr, y=arr)
        plot = Plot(data)
        self.assertRaises(ValueError, plot.plot, ("x", "y"))

        arr = arange(16).reshape(2, 2, 2, 2)
        data.update_data(x=arr, y=arr)
        self.assertRaises(ValueError, plot.plot, ("x", "y"))

    def test_range_change(self):
        arr = arange(10)
        data = ArrayPlotData(x=arr, y=arr)
        plot = Plot(data)
        renderer = plot.plot(('x', 'y'))[0]
        new_range = DataRange1D()
        old_range = plot.index_range
        self.assertIsNot(old_range, new_range)
        self.assertIs(renderer.index_range, old_range)
        plot.index_range = new_range
        self.assertIs(plot.index_range, new_range)
        self.assertIs(renderer.index_range, new_range)

if __name__ == "__main__":
    unittest.main()
