# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from unittest import TestCase
import numpy as np

from chaco.plot_factory import (
    create_bar_plot,
    create_line_plot,
    create_polar_plot,
    create_scatter_plot,
)
from chaco.api import (
    BarPlot, LinePlot, PlotAxis, PlotGrid, PolarLineRenderer, ScatterPlot
)

x = np.array([1, 2, 3, 4])

y = np.array([1, 2, 3, 4])


class BaseTestRenderer:
    def test_create_renderer_default(self):
        renderer = self.factory((x, y))
        self.assertIsInstance(renderer, self.renderer_klass)

    def test_create_renderer_additional_traits(self):
        renderer = self.factory((x, y), alpha=0.5)
        self.assertIsInstance(renderer, self.renderer_klass)

    def test_create_renderer_add_axis(self):
        renderer = self.factory((x, y), add_axis=True)
        self.assertIsInstance(renderer, self.renderer_klass)
        self.assertEqual(len(renderer.underlays), 2)
        for underlay in renderer.underlays:
            self.assertIsInstance(underlay, PlotAxis)

    def test_create_renderer_add_grids(self):
        renderer = self.factory((x, y), add_grid=True)
        self.assertIsInstance(renderer, self.renderer_klass)
        self.assertEqual(len(renderer.underlays), 2)
        for underlay in renderer.underlays:
            self.assertIsInstance(underlay, PlotGrid)


class TestCreateLineRenderer(BaseTestRenderer, TestCase):
    def setUp(self):
        self.factory = create_line_plot
        self.renderer_klass = LinePlot


class TestCreateScatterRenderer(BaseTestRenderer, TestCase):
    def setUp(self):
        self.factory = create_scatter_plot
        self.renderer_klass = ScatterPlot


class TestCreateBarRenderer(BaseTestRenderer, TestCase):
    def setUp(self):
        self.factory = create_bar_plot
        self.renderer_klass = BarPlot


class TestCreatePolarRenderer(BaseTestRenderer, TestCase):
    def setUp(self):
        self.factory = create_polar_plot
        self.renderer_klass = PolarLineRenderer

    def test_create_renderer_add_grids(self):
        # Unsupported option
        pass

    def test_create_renderer_add_axis(self):
        # Unsupported option
        pass
