import unittest

from numpy import alltrue, arange
from enable.compiled_path import CompiledPath

# Chaco imports
from chaco.api import (ArrayDataSource, DataRange1D, LinearMapper,
                       PlotGraphicsContext)
from chaco.line_scatterplot_1d import LineScatterPlot1D


class LineScatterPlot1DTest(unittest.TestCase):

    def setUp(self):
        self.size = (250, 250)
        data_source = ArrayDataSource(arange(10))
        index_range = DataRange1D()
        index_range.add(data_source)
        index_mapper = LinearMapper(range=index_range)
        self.scatterplot = LineScatterPlot1D(
            index=data_source,
            index_mapper=index_mapper,
            border_visible=False,
        )
        self.scatterplot.outer_bounds = list(self.size)

    def test_scatter_1d(self):
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_1d_thicker(self):
        self.scatterplot.line_width = 2.0
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_1d_color(self):
        self.scatterplot.color = 'orange'
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_1d_line_style(self):
        self.scatterplot.line_style = 'dash'
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
