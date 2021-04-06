import unittest

from numpy import alltrue, arange, array

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    DataRange1D,
    LinearMapper,
    PlotGraphicsContext,
)
from chaco.text_plot import TextPlot


class TextPlotTest(unittest.TestCase):
    def setUp(self):
        self.size = (250, 250)
        index_data_source = ArrayDataSource(arange(10))
        index_range = DataRange1D()
        index_range.add(index_data_source)
        index_mapper = LinearMapper(range=index_range)

        value_data_source = ArrayDataSource(arange(1, 11))
        value_range = DataRange1D()
        value_range.add(value_data_source)
        value_mapper = LinearMapper(range=value_range)

        text_data_source = ArrayDataSource(
            array(["one", "two", "three", "four", "five"])
        )

        self.text_plot = TextPlot(
            index=index_data_source,
            index_mapper=index_mapper,
            value=value_data_source,
            value_mapper=value_mapper,
            border_visible=False,
            text=text_data_source,
        )
        self.text_plot.outer_bounds = list(self.size)

    def test_text(self):
        self.assertEqual(self.text_plot.origin, "bottom left")
        self.assertEqual(self.text_plot.x_mapper, self.text_plot.index_mapper)
        self.assertEqual(self.text_plot.y_mapper, self.text_plot.value_mapper)
        self.assertIs(
            self.text_plot.index_range, self.text_plot.index_mapper.range
        )
        self.assertIs(
            self.text_plot.value_range, self.text_plot.value_mapper.range
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.text_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
