import unittest

from numpy import alltrue, arange
from enable.compiled_path import CompiledPath

# Chaco imports
from chaco.api import (ArrayDataSource, DataRange1D, LinearMapper,
                       PlotGraphicsContext)
from chaco.text_plot_1d import TextPlot1D


class TextPlot1DTest(unittest.TestCase):

    def setUp(self):
        self.size = (250, 250)
        data_source = ArrayDataSource(arange(10))
        text_data = ArrayDataSource(['one', 'two', 'three', 'four', 'five',
                                     'six', 'seven', 'eight', 'nine', 'ten'])
        index_range = DataRange1D()
        index_range.add(data_source)
        index_mapper = LinearMapper(range=index_range)
        self.scatterplot = TextPlot1D(
            index=data_source,
            index_mapper=index_mapper,
            value=text_data,
            border_visible=False,
        )
        self.scatterplot.outer_bounds = list(self.size)

    def test_scatter_1d(self):
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_1d_rotated(self):
        self.scatterplot.text_rotate_angle = 45
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
