import unittest

from numpy import alltrue, arange, array
from numpy.testing import assert_almost_equal

from traits.testing.api import UnittestTools

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    DataRange1D,
    LinearMapper,
    LineScatterPlot1D,
    PlotGraphicsContext,
)


class LineScatterPlot1DTest(UnittestTools, unittest.TestCase):
    def setUp(self):
        self.size = (250, 250)
        data_source = ArrayDataSource(arange(10))
        index_range = DataRange1D()
        index_range.add(data_source)
        index_mapper = LinearMapper(range=index_range)
        self.linescatterplot = LineScatterPlot1D(
            index=data_source,
            index_mapper=index_mapper,
            border_visible=False,
        )
        self.linescatterplot.outer_bounds = list(self.size)

    def test_linescatter_1d(self):
        self.assertEqual(self.linescatterplot.origin, "bottom left")
        self.assertIsNone(self.linescatterplot.x_mapper)
        self.assertEqual(
            self.linescatterplot.y_mapper, self.linescatterplot.index_mapper
        )
        self.assertIs(
            self.linescatterplot.index_range,
            self.linescatterplot.index_mapper.range,
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_horizontal(self):
        self.linescatterplot.orientation = "h"

        self.assertEqual(self.linescatterplot.origin, "bottom left")
        self.assertEqual(
            self.linescatterplot.x_mapper, self.linescatterplot.index_mapper
        )
        self.assertIsNone(self.linescatterplot.y_mapper)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_flipped(self):
        self.linescatterplot.direction = "flipped"

        self.assertEqual(self.linescatterplot.origin, "top left")
        self.assertIsNone(self.linescatterplot.x_mapper)
        self.assertEqual(
            self.linescatterplot.y_mapper, self.linescatterplot.index_mapper
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_horizontal_flipped(self):
        self.linescatterplot.direction = "flipped"
        self.linescatterplot.orientation = "h"

        self.assertEqual(self.linescatterplot.origin, "bottom right")
        self.assertEqual(
            self.linescatterplot.x_mapper, self.linescatterplot.index_mapper
        )
        self.assertIsNone(self.linescatterplot.y_mapper)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_thicker(self):
        self.linescatterplot.line_width = 2.0
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_color(self):
        self.linescatterplot.color = "orange"
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_line_style(self):
        self.linescatterplot.line_style = "dash"
        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_map_data(self):
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(
            self.linescatterplot.map_data(points), array([4.5, 0])
        )

    def test_linescatter_1d_map_data_horizontal(self):
        self.linescatterplot.orientation = "h"
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(
            self.linescatterplot.map_data(points), array([0, 4.5])
        )

    def test_linescatter_1d_map_data_flipped(self):
        self.linescatterplot.direction = "flipped"
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(
            self.linescatterplot.map_data(points), array([4.5, 9.0])
        )

    def test_linescatter_1d_map_data_horizontal_flipped(self):
        self.linescatterplot.direction = "flipped"
        self.linescatterplot.orientation = "h"
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(
            self.linescatterplot.map_data(points), array([9.0, 4.5])
        )

    def test_linescatter_1d_selection(self):
        self.linescatterplot.index.metadata["selections"] = [
            (arange(10) % 2 == 0),
        ]

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_selection_mask_name(self):
        # select with a mask
        self.linescatterplot.selection_metadata_name = "highlight_masks"
        self.linescatterplot.index.metadata["highlight_masks"] = [
            (arange(10) % 2 == 0),
        ]

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_selection_alpha(self):
        # test with different alpha
        self.linescatterplot.unselected_alpha = 0.4
        self.linescatterplot.index.metadata["selections"] = [
            (arange(10) % 2 == 0),
        ]

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.linescatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_linescatter_1d_set_index_range(self):
        new_range = DataRange1D(low=0.42, high=1.42)
        self.linescatterplot.index_range = new_range
        self.assertEqual(self.linescatterplot.index_mapper.range, new_range)

    def test_linescatter_1d_set_index_mapper_notifies_index_range(self):
        new_range = DataRange1D(low=0.42, high=1.42)

        with self.assertTraitChanges(
            self.linescatterplot, "index_range", count=1
        ):
            self.linescatterplot.index_mapper = LinearMapper(range=new_range)

        self.assertIs(self.linescatterplot.index_range, new_range)
