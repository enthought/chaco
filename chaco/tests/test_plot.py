import unittest

from numpy import alltrue, arange, array

# Chaco imports
from chaco.api import ArrayPlotData, Plot, DataRange1D, PlotGraphicsContext
from chaco.default_colormaps import viridis


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

    def test_segment_plot(self):
        x = arange(10)
        y = arange(1, 11)
        data = ArrayPlotData(x=x, y=y)
        plot = Plot(data)
        plot.plot(('x', 'y'), "segment")[0]

        plot.do_layout((250, 250))
        gc = PlotGraphicsContext((250, 250))
        gc.render_component(plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_plot_color(self):
        x = arange(10)
        y = arange(1, 11)
        c = arange(2, 7)
        data = ArrayPlotData(x=x, y=y, c=c)
        plot = Plot(data)
        plot.plot(('x', 'y', 'c'), "cmap_segment", color_mapper=viridis)[0]

        plot.do_layout((250, 250))
        gc = PlotGraphicsContext((250, 250))
        gc.render_component(plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_segment_plot_color_width(self):
        x = arange(10)
        y = arange(1, 11)
        c = arange(2, 7)
        w = arange(3, 8)
        data = ArrayPlotData(x=x, y=y, c=c, w=w)
        plot = Plot(data)
        plot.plot(('x', 'y', 'c', 'w'), "cmap_segment",
                  color_mapper=viridis)[0]

        plot.do_layout((250, 250))
        gc = PlotGraphicsContext((250, 250))
        gc.render_component(plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_text_plot(self):
        x = arange(10)
        y = arange(1, 11)
        t = array(["one", "two", "three", "four", "five"])
        data = ArrayPlotData(x=x, y=y, t=t)
        plot = Plot(data)
        plot.plot(('x', 'y', 't'), "text")[0]

        plot.do_layout((250, 250))
        gc = PlotGraphicsContext((250, 250))
        gc.render_component(plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))


if __name__ == "__main__":
    unittest.main()
