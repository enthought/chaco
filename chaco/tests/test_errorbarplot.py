import unittest

import numpy as np
from numpy import alltrue

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    DataRange1D,
    ErrorBarPlot,
    LinearMapper,
    PlotGraphicsContext,
)


class DrawErrorBarPlotCase(unittest.TestCase):
    def test_errorbarplot(self):
        """ Coverage test to check basic case works """
        size = (50, 50)
        x = np.array([1, 2])
        y = np.array([5, 10])
        errors = np.array([1, 2])
        low = ArrayDataSource(y - errors)
        high = ArrayDataSource(y + errors)
        errorbar_plot = ErrorBarPlot(
            index=ArrayDataSource(x),
            values=ArrayDataSource(y),
            index_mapper=LinearMapper(range=DataRange1D(low=0, high=3)),
            value_mapper=LinearMapper(range=DataRange1D(low=0, high=15)),
            value_low=low,
            value_high=high,
            color="blue",
            line_width=3.0,
        )
        errorbar_plot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(errorbar_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
