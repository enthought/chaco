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

from numpy import linspace, sin

from traits.api import Enum, HasTraits, Instance
from traitsui.api import UItem, View
from chaco.api import (
    ArrayPlotData, DataRange2D, DataView, GridDataSource, Plot
)
from enable.api import ComponentEditor


class DummyPaddingPlot(HasTraits):
    orientation = Enum("top", "bottom", "left", "right")
    plot = Instance(Plot)

    traits_view = View(
        UItem(
            'plot',
            editor=ComponentEditor()
        ),
    )

    def _plot_default(self):
        x = linspace(0, 10, 10)
        plotdata = ArrayPlotData(x=x, y=x)

        plot = Plot(plotdata)
        plot.plot(("x", "y"), type="line", color="blue")

        plot.x_axis.title = "X AXIS"
        plot.x_axis.orientation = self.orientation

        return plot


class DataViewTestCase(unittest.TestCase):
    def test_empty(self):
        dv = DataView()
        self.assertTrue(dv.orientation == "h")
        self.assertTrue(dv.index_scale == "linear")
        self.assertTrue(dv.bgcolor == "white")
        self.assertTrue(dv.overlay_border == True)

        self.assertTrue(dv.range2d.x_range == dv.index_range)
        self.assertTrue(dv.range2d.y_range == dv.value_range)

    def test_orientation(self):
        dv = DataView()
        x_mapper_start = dv.x_mapper
        y_mapper_start = dv.y_mapper
        dv.orientation = "v"
        self.assertTrue(dv.x_mapper is y_mapper_start)
        self.assertTrue(dv.y_mapper is x_mapper_start)

    def test_range2d_changed(self):
        dv = DataView()
        ds = GridDataSource()
        dv.range2d.add(ds)
        old_range = dv.range2d
        r = DataRange2D()

        self.assertTrue(dv.range2d.sources == [ds])
        dv.range2d = r
        self.assertTrue(dv.range2d.sources == [ds])
        self.assertTrue(old_range.sources == [])
        self.assertTrue(dv.range2d.x_range is dv.index_mapper.range)
        self.assertTrue(dv.range2d.y_range is dv.value_mapper.range)

    # regression test for enthought/chaco#735
    def test_padding_with_axis_title(self):
        for orientation in ["top", "bottom", "left", "right"]:
            dummy_plot = DummyPaddingPlot(orientation=orientation)
            self.assertEqual(
                getattr(dummy_plot.plot, "padding_" + orientation), 80
            )
