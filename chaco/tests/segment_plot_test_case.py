import unittest

from numpy import alltrue, arange, array
from numpy.testing import assert_almost_equal, assert_array_equal

# Chaco imports
from chaco.api import (
    ArrayDataSource, DataRange1D, LinearMapper, PlotGraphicsContext
)
from chaco.base import rgba_dtype
from chaco.segment_plot import SegmentPlot
from chaco.default_colormaps import viridis


class SegmentPlotTest(unittest.TestCase):
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

        self.segment_plot = SegmentPlot(
            index=index_data_source,
            index_mapper=index_mapper,
            value=value_data_source,
            value_mapper=value_mapper,
            border_visible=False,
        )
        self.segment_plot.outer_bounds = list(self.size)

    def set_color_data(self):
        color_data_source = ArrayDataSource(arange(2, 7))
        color_range = DataRange1D()
        color_range.add(color_data_source)
        color_mapper = viridis(range=color_range)

        self.segment_plot.color_by_data = True
        self.segment_plot.color_data = color_data_source
        self.segment_plot.color_mapper = color_mapper

    def set_width_data(self):
        width_data_source = ArrayDataSource(arange(3, 8))
        width_range = DataRange1D()
        width_range.add(width_data_source)
        width_mapper = LinearMapper(low_pos=1, high_pos=10, range=width_range)

        self.segment_plot.width_by_data = True
        self.segment_plot.width_data = width_data_source
        self.segment_plot.width_mapper = width_mapper

    def test_segment(self):
        self.assertEqual(self.segment_plot.origin, 'bottom left')
        self.assertEqual(
            self.segment_plot.x_mapper, self.segment_plot.index_mapper
        )
        self.assertEqual(
            self.segment_plot.y_mapper, self.segment_plot.value_mapper
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_orthogonal(self):
        self.segment_plot.render_style = 'orthogonal'

        self.assertEqual(self.segment_plot.origin, 'bottom left')
        self.assertEqual(
            self.segment_plot.x_mapper, self.segment_plot.index_mapper
        )
        self.assertEqual(
            self.segment_plot.y_mapper, self.segment_plot.value_mapper
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_quad(self):
        self.segment_plot.render_style = 'quad'

        self.assertEqual(self.segment_plot.origin, 'bottom left')
        self.assertEqual(
            self.segment_plot.x_mapper, self.segment_plot.index_mapper
        )
        self.assertEqual(
            self.segment_plot.y_mapper, self.segment_plot.value_mapper
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_cubic(self):
        self.segment_plot.render_style = 'cubic'

        self.assertEqual(self.segment_plot.origin, 'bottom left')
        self.assertEqual(
            self.segment_plot.x_mapper, self.segment_plot.index_mapper
        )
        self.assertEqual(
            self.segment_plot.y_mapper, self.segment_plot.value_mapper
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_color(self):
        self.set_color_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_color_orthogonal(self):
        self.segment_plot.render_style = 'orthogonal'
        self.set_color_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_color_quad(self):
        self.segment_plot.render_style = 'quad'
        self.set_color_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_color_cubic(self):
        self.segment_plot.render_style = 'cubic'
        self.set_color_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_width(self):
        self.set_width_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_width_orthogonal(self):
        self.segment_plot.render_style = 'orthogonal'
        self.set_width_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_width_quad(self):
        self.segment_plot.render_style = 'quad'
        self.set_width_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_width_cubic(self):
        self.segment_plot.render_style = 'cubic'
        self.set_width_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_width_color(self):
        self.set_width_data()
        self.set_color_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_width_orthogonal_color(self):
        self.segment_plot.render_style = 'orthogonal'
        self.set_width_data()
        self.set_color_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_width_quad_color(self):
        self.segment_plot.render_style = 'quad'
        self.set_width_data()
        self.set_color_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_width_cubic_color(self):
        self.segment_plot.render_style = 'cubic'
        self.set_width_data()
        self.set_color_data()

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_alpha(self):
        self.segment_plot.alpha = 0.5

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_orthogonal_alpha(self):
        self.segment_plot.render_style = 'orthogonal'
        self.segment_plot.alpha = 0.5

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_quad_alpha(self):
        self.segment_plot.render_style = 'quad'
        self.segment_plot.alpha = 0.5

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_cubic_alpha(self):
        self.segment_plot.render_style = 'cubic'
        self.segment_plot.alpha = 0.5

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_selection(self):
        mask = array([True, True, False, False, True])
        self.segment_plot.index.metadata['selections'] = [mask]

        black = self.segment_plot.color_
        yellow = self.segment_plot.selection_color_
        expected_colors = array([yellow, yellow, black, black, yellow])
        expected_colors = expected_colors.astype('float32').view(rgba_dtype)
        expected_colors.shape = (5, )
        expected_colors['a'][~mask] *= 0.3

        assert_array_equal(mask, self.segment_plot.selected_mask)
        assert_array_equal(expected_colors, self.segment_plot.effective_colors)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_selection_color(self):
        mask = array([True, True, False, False, True])
        self.segment_plot.index.metadata['selections'] = [mask]
        self.set_color_data()

        color_data = self.segment_plot.color_data.get_data()
        colors = self.segment_plot.color_mapper.map_screen(color_data)
        expected_colors = colors.astype('float32').view(rgba_dtype)
        expected_colors.shape = (5, )
        expected_colors['a'][~mask] *= 0.3

        assert_array_equal(mask, self.segment_plot.selected_mask)
        assert_array_equal(expected_colors, self.segment_plot.effective_colors)

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.segment_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
