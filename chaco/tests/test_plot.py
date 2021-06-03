# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from numpy import alltrue, arange, array

from enable.api import ComponentEditor
from enable.testing import EnableTestAssistant
from traits.api import HasTraits, Instance
from traits.etsconfig.api import ETSConfig
from traitsui.api import Item, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot, DataRange1D, PlotGraphicsContext
from chaco.default_colormaps import viridis
from chaco.tools.api import PanTool, ZoomTool


def is_qt4():
    if not ETSConfig.toolkit.startswith('qt'):
        return False

    # Only AFTER confirming Qt's availability...
    # We lean on Pyface here since the check is complicated.
    import pyface.qt
    return pyface.qt.is_qt4


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
        renderer_2d = plot.plot(("x", "y"))[0]
        renderer_1d = plot.plot_1d(("x"))[0]
        new_range = DataRange1D()
        old_range = plot.index_range
        self.assertIsNot(old_range, new_range)
        self.assertIs(renderer_2d.index_range, old_range)
        self.assertIs(renderer_1d.index_range, old_range)
        plot.index_range = new_range
        self.assertIs(plot.index_range, new_range)
        self.assertIs(renderer_2d.index_range, new_range)
        self.assertIs(renderer_1d.index_range, new_range)

    def test_segment_plot(self):
        x = arange(10)
        y = arange(1, 11)
        data = ArrayPlotData(x=x, y=y)
        plot = Plot(data)
        plot.plot(("x", "y"), "segment")[0]

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
        plot.plot(("x", "y", "c"), "cmap_segment", color_mapper=viridis)[0]

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
        plot.plot(
            ("x", "y", "c", "w"), "cmap_segment", color_mapper=viridis
        )[0]

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
        plot.plot(("x", "y", "t"), "text")[0]

        plot.do_layout((250, 250))
        gc = PlotGraphicsContext((250, 250))
        gc.render_component(plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))


class EmptyLinePlot(HasTraits):
    plot = Instance(Plot)
    x = []
    y = []
    traits_view = View(
        Item('plot', editor=ComponentEditor(), show_label=False),
        width=500,
        height=500,
        resizable=True
    )

    def _plot_default(self):
        plot = Plot(ArrayPlotData(x=self.x, y=self.y))
        plot.plot(("x", "y"), type="line", color="blue")
        plot.tools.append(PanTool(plot))
        plot.overlays.append(ZoomTool(plot, zoom_factor=1.1))
        return plot


# regression test for enthought/chaco#529
@unittest.skipIf(ETSConfig.toolkit == "null", "Skip on 'null' toolkit")
class TestEmptyPlot(unittest.TestCase, EnableTestAssistant):

    @unittest.skipIf(is_qt4(), "Test breaks on pyqt")
    def test_dont_crash_on_click(self):
        from traitsui.testing.api import UITester
        tester = UITester()
        empty_plot = EmptyLinePlot()

        with tester.create_ui(empty_plot):
            self.press_move_release(
                empty_plot.plot,
                [(1, 1), (2, 2), (3, 3), (4, 4)],
            )
