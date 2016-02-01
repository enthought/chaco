import unittest2 as unittest

from numpy import alltrue, arange, array
from numpy.testing import assert_almost_equal

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
        self.assertEqual(self.scatterplot.origin, 'bottom left')
        self.assertIsNone(self.scatterplot.x_mapper)
        self.assertEqual(self.scatterplot.y_mapper,
                         self.scatterplot.index_mapper)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_1d_horizontal(self):
        self.scatterplot.orientation = 'h'

        self.assertEqual(self.scatterplot.origin, 'bottom left')
        self.assertEqual(self.scatterplot.x_mapper,
                         self.scatterplot.index_mapper)
        self.assertIsNone(self.scatterplot.y_mapper)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_1d_flipped(self):
        self.scatterplot.direction = 'flipped'

        self.assertEqual(self.scatterplot.origin, 'top left')
        self.assertIsNone(self.scatterplot.x_mapper)
        self.assertEqual(self.scatterplot.y_mapper,
                         self.scatterplot.index_mapper)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_1d_horizontal_flipped(self):
        self.scatterplot.direction = 'flipped'
        self.scatterplot.orientation = 'h'

        self.assertEqual(self.scatterplot.origin, 'bottom right')
        self.assertEqual(self.scatterplot.x_mapper,
                         self.scatterplot.index_mapper)
        self.assertIsNone(self.scatterplot.y_mapper)

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

    def test_scatter_1d_map_data(self):
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(self.scatterplot.map_data(points),
                            array([4.5, 0]))

    def test_scatter_1d_map_data_horizontal(self):
        self.scatterplot.orientation = 'h'
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(self.scatterplot.map_data(points),
                            array([0, 4.5]))

    def test_scatter_1d_map_data_flipped(self):
        self.scatterplot.direction = 'flipped'
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(self.scatterplot.map_data(points),
                            array([4.5, 9.0]))

    def test_scatter_1d_map_data_horizontal_flipped(self):
        self.scatterplot.direction = 'flipped'
        self.scatterplot.orientation = 'h'
        points = array([[0, 124.5], [124.5, 0]])
        assert_almost_equal(self.scatterplot.map_data(points),
                            array([9.0, 4.5]))

    def test_scatter_1d_selection(self):
        self.scatterplot.index.metadata['selections'] = [
            (arange(10) % 2 == 0),
        ]

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_1d_selection_name(self):
        self.scatterplot.index.metadata['highlight_masks'] = [
            (arange(10) % 2 == 0),
        ]
        self.scatterplot.selection_metadata_name = 'highlight_masks'

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_1d_selection_name(self):
        self.scatterplot.index.metadata['selections'] = [
            (arange(10) % 2 == 0),
        ]
        self.scatterplot.selection_alpha = 0.4

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
