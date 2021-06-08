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

import numpy as np
from numpy import alltrue

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    DataRange1D,
    ErrorBarPlot,
    LinearMapper,
    PlotGraphicsContext,
)


class DrawErrorBarPlotCase(unittest.TestCase):
    def test_errorbarplot(self):
        """ Coverage test to check basic case works """
        size = (50, 50)
        x = np.array([1, 2])
        y = np.array([5, 10])
        errors = np.array([1, 2])
        low = ArrayDataSource(y - errors)
        high = ArrayDataSource(y + errors)
        errorbar_plot = ErrorBarPlot(
            index=ArrayDataSource(x),
            values=ArrayDataSource(y),
            index_mapper=LinearMapper(range=DataRange1D(low=0, high=3)),
            value_mapper=LinearMapper(range=DataRange1D(low=0, high=15)),
            value_low=low,
            value_high=high,
            color="blue",
            line_width=3.0,
        )
        errorbar_plot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(errorbar_plot)
        actual = gc.bmp_array[:, :, :]
        self.assertFalse(alltrue(actual == 255))
