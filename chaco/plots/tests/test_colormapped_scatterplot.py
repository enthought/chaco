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

from numpy import alltrue, arange
from enable.compiled_path import CompiledPath

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    ColormappedScatterPlot,
    DataRange1D,
    LinearMapper,
    PlotGraphicsContext,
    jet,
)


class TestColormappedScatterplot(unittest.TestCase):
    def setUp(self):
        self.index = ArrayDataSource(arange(10))
        self.value = ArrayDataSource(arange(10))
        self.color_data = ArrayDataSource(arange(10))
        self.size_data = arange(10)

        self.index_range = DataRange1D()
        self.index_range.add(self.index)
        self.index_mapper = LinearMapper(range=self.index_range)

        self.value_range = DataRange1D()
        self.value_range.add(self.value)
        self.value_mapper = LinearMapper(range=self.value_range)

        self.color_range = DataRange1D()
        self.color_range.add(self.color_data)
        self.color_mapper = jet(self.color_range)

        self.scatterplot = ColormappedScatterPlot(
            index=self.index,
            value=self.value,
            index_mapper=self.index_mapper,
            value_mapper=self.value_mapper,
            color_data=self.color_data,
            marker_size=self.size_data,
            color_mapper=self.color_mapper,
        )
        self.scatterplot.outer_bounds = [50, 50]
        self.gc = PlotGraphicsContext((50, 50))

    def test_scatter_render(self):
        """ Coverage test to check basic case works """
        self.gc.render_component(self.scatterplot)
        actual = self.gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_circle(self):
        """ Coverage test to check circles work """
        self.scatterplot.marker = "circle"

        self.gc.render_component(self.scatterplot)
        actual = self.gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_custom(self):
        """Coverage test to check custom markers work.
        """

        # build path
        path = CompiledPath()
        path.begin_path()
        path.move_to(-5, -5)
        path.line_to(-5, 5)
        path.line_to(5, 5)
        path.line_to(5, -5)
        path.line_to(-5, -5)

        self.scatterplot.marker = "custom"
        self.scatterplot.custom_symbol = path

        self.gc.render_component(self.scatterplot)
        actual = self.gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_colormap_updated(self):
        """ If colormapper updated then we need to redraw """
        self.color_mapper.updated = True
        self.assertFalse(self.scatterplot.draw_valid)

    # regression test for enthought/chaco#425
    def test_non_kiva_marker(self):
        self.scatterplot.marker = "star"

        self.gc.render_component(self.scatterplot)
        actual = self.gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
