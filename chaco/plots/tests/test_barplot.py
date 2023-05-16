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

from numpy import alltrue, arange, nan

from traits.testing.api import UnittestTools

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    DataRange1D,
    LinearMapper,
    PlotGraphicsContext,
)
from chaco.plots.api import BarPlot


class BarPlotTest(UnittestTools, unittest.TestCase):
    def setUp(self):
        self.size = (250, 250)
        values = arange(10.0, 0.0, -1.0)
        values[2] = nan
        value_data_source = ArrayDataSource(values)
        value_range = DataRange1D()
        value_range.add(value_data_source)
        value_mapper = LinearMapper(range=value_range)
        starting_value_data_source = ArrayDataSource(-values)
        value_range.add(starting_value_data_source)
        indices = arange(10.0)
        indices[4] = nan
        index_data_source = ArrayDataSource(indices)
        index_range = DataRange1D()
        index_range.add(index_data_source)
        index_mapper = LinearMapper(range=index_range)
        self.barplot = BarPlot(
            index=index_data_source,
            value=value_data_source,
            starting_value=starting_value_data_source,
            index_mapper=index_mapper,
            value_mapper=value_mapper,
            border_visible=False,
        )
        self.barplot.outer_bounds = list(self.size)

    def test_barplot(self):
        self.assertEqual(self.barplot.origin, "bottom left")
        self.assertIs(
            self.barplot.x_mapper, self.barplot.index_mapper
        )
        self.assertIs(
            self.barplot.y_mapper, self.barplot.value_mapper
        )
        self.assertIs(
            self.barplot.index_range,
            self.barplot.index_mapper.range,
        )
        self.assertIs(
            self.barplot.value_range,
            self.barplot.value_mapper.range,
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.barplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))

    def test_barplot_horizontal(self):
        self.barplot.orientation = 'v'

        self.assertEqual(self.barplot.origin, "bottom left")
        self.assertIs(
            self.barplot.x_mapper, self.barplot.value_mapper
        )
        self.assertIs(
            self.barplot.y_mapper, self.barplot.index_mapper
        )
        self.assertIs(
            self.barplot.index_range,
            self.barplot.index_mapper.range,
        )
        self.assertIs(
            self.barplot.value_range,
            self.barplot.value_mapper.range,
        )

        gc = PlotGraphicsContext(self.size)
        gc.render_component(self.barplot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
