import unittest

from numpy import alltrue, arange, array
from numpy.testing import assert_almost_equal

from traits.testing.unittest_tools import UnittestTools

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    DataRange1D,
    LinearMapper,
    PlotGraphicsContext,
)
from chaco.text_plot_1d import TextPlot1D


class TextPlot1DTest(UnittestTools, unittest.TestCase):
    def setUp(self):
        self.size = (250, 250)
        data_source = ArrayDataSource(arange(10))
        text_data = ArrayDataSource(
            [
                "one",
                "two",
                "three",
                "four",
                "five",
                "six",
                "seven",
                "eight",
                "nine",
                "ten",
            ]
        )
        index_range = DataRange1D()
        index_range.add(data_source)
        index_mapper = LinearMapper(range=index_range)
        self.textplot = TextPlot1D(
            index=data_source,
            index_mapper=index_mapper,
            value=text_data,
            border_visible=False,
        )
        self.textplot.outer_bounds = list(self.size)

    def test_text_1d(self):
        self.assertEqual(self.textplot.origin, "bottom left")
        self.assertIsNone(self.textplot.x_mapper)
        self.assertEqual(self.textplot.y_mapper, self.textplot.index_mapper)
        self.assertIs(
            self.textplot.index_range, self.textplot.index_mapper.range
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.textplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_text_1d_horizontal(self):
        self.textplot.orientation = "h"

        self.assertEqual(self.textplot.origin, "bottom left")
        self.assertEqual(self.textplot.x_mapper, self.textplot.index_mapper)
        self.assertIsNone(self.textplot.y_mapper)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.textplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_text_1d_flipped(self):
        self.textplot.direction = "flipped"

        self.assertEqual(self.textplot.origin, "top left")
        self.assertIsNone(self.textplot.x_mapper)
        self.assertEqual(self.textplot.y_mapper, self.textplot.index_mapper)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.textplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_text_1d_horizontal_flipped(self):
        self.textplot.direction = "flipped"
        self.textplot.orientation = "h"

        self.assertEqual(self.textplot.origin, "bottom right")
        self.assertEqual(self.textplot.x_mapper, self.textplot.index_mapper)
        self.assertIsNone(self.textplot.y_mapper)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.textplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_text_1d_rotated(self):
        self.textplot.text_rotate_angle = 45
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.textplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_text_1d_map_data(self):
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(self.textplot.map_data(points), array([4.5, 0]))

    def test_text_1d_map_data_horizontal(self):
        self.textplot.orientation = "h"
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(self.textplot.map_data(points), array([0, 4.5]))

    def test_text_1d_map_data_flipped(self):
        self.textplot.direction = "flipped"
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(self.textplot.map_data(points), array([4.5, 9.0]))

    def test_text_1d_map_data_horizontal_flipped(self):
        self.textplot.direction = "flipped"
        self.textplot.orientation = "h"
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(self.textplot.map_data(points), array([9.0, 4.5]))

    def test_text_1d_set_index_range(self):
        new_range = DataRange1D(low=0.42, high=1.42)
        self.textplot.index_range = new_range
        self.assertEqual(self.textplot.index_mapper.range, new_range)

    def test_text_1d_set_index_mapper_notifies_index_range(self):
        new_range = DataRange1D(low=0.42, high=1.42)

        with self.assertTraitChanges(self.textplot, "index_range", count=1):
            self.textplot.index_mapper = LinearMapper(range=new_range)

        self.assertIs(self.textplot.index_range, new_range)
