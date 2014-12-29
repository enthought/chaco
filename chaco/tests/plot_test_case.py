
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from numpy import arange

# Chaco imports
from chaco.array_plot_data import ArrayPlotData
from chaco.plot import Plot


class PlotTestCase(unittest.TestCase):

    def test_plot_from_unsupported_array_shape(self):
        arr = arange(8).reshape(2, 2, 2)
        data = ArrayPlotData(x=arr, y=arr)
        plot = Plot(data)
        self.assertRaises(ValueError, plot.plot, ("x", "y"))

        arr = arange(16).reshape(2, 2, 2, 2)
        data.update_data(x=arr, y=arr)
        self.assertRaises(ValueError, plot.plot, ("x", "y"))

if __name__ == "__main__":
    unittest.main()
