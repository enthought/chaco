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

from numpy import alltrue
from enable.compiled_path import CompiledPath

# Chaco imports
from chaco.api import create_scatter_plot, PlotGraphicsContext


class DrawScatterplotCase(unittest.TestCase):
    def test_scatter_fast(self):
        """ Coverage test to check basic case works """
        size = (50, 50)
        scatterplot = create_scatter_plot(
            data=[list(range(10)), list(range(10))],
            border_visible=False,
        )
        scatterplot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_circle(self):
        """ Coverage test to check circles work """
        size = (50, 50)
        scatterplot = create_scatter_plot(
            data=[list(range(10)), list(range(10))],
            marker="circle",
            border_visible=False,
        )
        scatterplot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_custom(self):
        """ Coverage test to check custom markers work """
        # build path
        path = CompiledPath()
        path.move_to(-5, -5)
        path.line_to(5, 5)
        path.line_to(5, -5)
        path.line_to(-5, 5)
        path.line_to(-5, -5)

        size = (50, 50)
        scatterplot = create_scatter_plot(
            data=[list(range(10)), list(range(10))],
            marker="custom",
            border_visible=False,
        )
        scatterplot.custom_symbol = path
        scatterplot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_scatter_slow(self):
        """ Coverage test to check multiple marker size works """
        size = (50, 50)
        scatterplot = create_scatter_plot(
            data=[list(range(10)), list(range(10))],
            marker="circle",
            border_visible=False,
            marker_size=list(range(1, 11)),
        )
        scatterplot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(scatterplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
