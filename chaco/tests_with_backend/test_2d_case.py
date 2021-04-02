import unittest

from chaco.api import Plot, ArrayPlotData

from traits.api import HasTraits, Instance
from traits.etsconfig.api import ETSConfig
from enable.component_editor import ComponentEditor
from traitsui.api import Item, View

import numpy as np

from chaco.tests._tools import store_exceptions_on_all_threads, assert_raises


class PlotViewer(HasTraits):
    plot = Instance(Plot)
    traits_view = View(Item("plot", editor=ComponentEditor()))


@unittest.skipIf(ETSConfig.toolkit == "null", "Skip on 'null' toolkit")
class Test2DCase(unittest.TestCase):
    def test_bounds_2d_case(self):
        # test for bug: contour and image plots should support the case where
        # xbounds and ybounds are 2d arrays resulting from meshgrids

        xs = np.linspace(-10, 10, 200)
        ys = np.linspace(-10, 10, 400)
        x, y = np.meshgrid(xs, ys)
        z = x + y

        plotdata = ArrayPlotData()
        plotdata.set_data("z", z)

        plot = Plot(plotdata)
        plot.contour_plot("z", xbounds=x, ybounds=y)

        # try to display it, that's when the exception is raised
        with store_exceptions_on_all_threads():
            pv = PlotViewer(plot=plot)
            pv.edit_traits()

    def test_process_2d_bounds_cell_plot(self):
        # behavior: _process_2d_bounds accepts all possible ways to set x and y
        # bounds in 2d plots and returns a 1d array with equally spaced
        # intervals between the lower and upper bound of the data. The number
        # of elements in the 1d array must be of one element larger than the
        # shape of the data, because this is cell data.

        height, width = 20, 10
        array_data = np.ones(shape=(height, width))
        plot = Plot()

        # bounds is None : infer from array_data shape
        xs = plot._process_2d_bounds(None, array_data, 1, cell_plot=True)
        self.assertEqual(xs.shape[0], width + 1)
        ys = plot._process_2d_bounds(None, array_data, 0, cell_plot=True)
        self.assertEqual(ys.shape[0], height + 1)

        # bounds is a tuple : it defines lower and upper range
        bounds = (1.0, 100.0)
        xs = plot._process_2d_bounds(bounds, array_data, 1, cell_plot=True)
        self.assertEqual(xs.shape[0], width + 1)
        self.assertEqual(xs[0], bounds[0])
        self.assertEqual(xs[-1], bounds[1])

        # bounds is a 1D array: the first and last elements are used to create
        # equally spaced intervals. Bounds must be of one element larger than the
        # corresponding axis in array_data, or it will raise a Value error
        bounds = np.zeros((height + 1,))
        bounds[0], bounds[-1] = 0.2, 21.3
        ys = plot._process_2d_bounds(bounds, array_data, 0, cell_plot=True)
        self.assertEqual(ys.shape[0], height + 1)
        self.assertEqual(ys[0], bounds[0])
        self.assertEqual(ys[-1], bounds[-1])
        with assert_raises(ValueError):
            bounds = np.zeros((width // 2,))
            plot._process_2d_bounds(bounds, array_data, 0, cell_plot=True)

        # bounds is a 2D array: the first and last elements along the appropriate
        # axis are used to create equally spaced intervals.
        # The size of the bounds must be the same as the data array, or this
        # sill raise a ValueError
        xbounds, ybounds = np.meshgrid(
            np.arange(width + 1), np.arange(height + 1)
        )

        xs = plot._process_2d_bounds(xbounds, array_data, 1, cell_plot=True)
        self.assertEqual(xs.shape[0], width + 1)
        self.assertEqual(xs[0], xbounds[0, 0])
        self.assertEqual(xs[-1], xbounds[0, -1])
        with assert_raises(ValueError):
            plot._process_2d_bounds(
                xbounds[:, :5], array_data, 1, cell_plot=True
            )

        ys = plot._process_2d_bounds(ybounds, array_data, 0, cell_plot=True)
        self.assertEqual(ys.shape[0], height + 1)
        self.assertEqual(ys[0], ybounds[0, 0])
        self.assertEqual(ys[-1], ybounds[-1, 0])
        with assert_raises(ValueError):
            plot._process_2d_bounds(
                ybounds[:5, :], array_data, 0, cell_plot=True
            )

    def test_process_2d_bounds_vertex_data(self):
        # behavior: _process_2d_bounds accepts all possible ways to set x and y
        # bounds in 2d plots and returns a 1d array with equally spaced
        # intervals between the lower and upper bound of the data. The number
        # of elements in the 1d array must be the same as the shape of the data,
        # because this is vertex data.

        height, width = 20, 10
        array_data = np.ones(shape=(height, width))
        plot = Plot()

        # bounds is None : infer from array_data shape
        xs = plot._process_2d_bounds(None, array_data, 1, cell_plot=False)
        self.assertEqual(xs.shape[0], width)
        ys = plot._process_2d_bounds(None, array_data, 0, cell_plot=False)
        self.assertEqual(ys.shape[0], height)

        # bounds is a tuple : it defines lower and upper range
        bounds = (1.0, 100.0)
        xs = plot._process_2d_bounds(bounds, array_data, 1, cell_plot=False)
        self.assertEqual(xs.shape[0], width)
        self.assertEqual(xs[0], bounds[0])
        self.assertEqual(xs[-1], bounds[1])

        # bounds is a 1D array: the first and last elements are used to create
        # equally spaced intervals. Bounds must be of one element larger than the
        # corresponding axis in array_data, or it will raise a Value error
        bounds = np.zeros((height,))
        bounds[0], bounds[-1] = 0.2, 21.3
        ys = plot._process_2d_bounds(bounds, array_data, 0, cell_plot=False)
        self.assertEqual(ys.shape[0], height)
        self.assertEqual(ys[0], bounds[0])
        self.assertEqual(ys[-1], bounds[-1])
        with assert_raises(ValueError):
            bounds = np.zeros((width // 2,))
            plot._process_2d_bounds(bounds, array_data, 0, cell_plot=False)

        # bounds is a 2D array: the first and last elements along the appropriate
        # axis are used to create equally spaced intervals.
        # The size of the bounds must be the same as the data array, or this
        # sill raise a ValueError
        xbounds, ybounds = np.meshgrid(np.arange(width), np.arange(height))

        xs = plot._process_2d_bounds(xbounds, array_data, 1, cell_plot=False)
        self.assertEqual(xs.shape[0], width)
        self.assertEqual(xs[0], xbounds[0, 0])
        self.assertEqual(xs[-1], xbounds[0, -1])
        with assert_raises(ValueError):
            plot._process_2d_bounds(
                xbounds[:, :5], array_data, 1, cell_plot=False
            )

        ys = plot._process_2d_bounds(ybounds, array_data, 0, cell_plot=False)
        self.assertEqual(ys.shape[0], height)
        self.assertEqual(ys[0], ybounds[0, 0])
        self.assertEqual(ys[-1], ybounds[-1, 0])
        with assert_raises(ValueError):
            plot._process_2d_bounds(
                ybounds[:5, :], array_data, 0, cell_plot=False
            )
