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
import warnings

import numpy as np

from chaco.array_data_source import ArrayDataSource
from chaco.axis import PlotAxis
from chaco.data_range_1d import DataRange1D
from chaco.label_axis import LabelAxis
from chaco.linear_mapper import LinearMapper
from chaco.overlays.data_label import DataLabel
from chaco.overlays.legend import Legend
from chaco.plots.scatterplot import ScatterPlot


class TestArrayOrNone(unittest.TestCase):
    """Test that the FutureWarning from numpy concerning comparison of arrays
    against None are not issued.

    These warnings began with numpy 1.9.
    """

    def test_array_data_source(self):
        with warnings.catch_warnings(record=True) as w:
            src = ArrayDataSource(np.arange(5))
        self.assertEqual(w, [])

    def test_scatter_plot(self):
        x = np.linspace(0.0, 1.0, 5)
        sp = ScatterPlot()
        with warnings.catch_warnings(record=True) as w:
            sp._cached_selected_pts = None
            sp._cached_selected_pts = np.column_stack([x, x])
        self.assertEqual(w, [])

    def test_plot_axis(self):
        axis = PlotAxis()
        with warnings.catch_warnings(record=True) as w:
            axis._tick_positions = np.arange(10)
            axis._tick_label_list = np.arange(10)
            axis._tick_label_positions = np.arange(10)
        self.assertEqual(w, [])

    def test_legend(self):
        legend = Legend()
        with warnings.catch_warnings(record=True) as w:
            legend._cached_label_sizes = np.arange(10)
            legend._cached_label_positions = np.arange(10)
        self.assertEqual(w, [])

    def test_data_label(self):
        label = DataLabel()
        with warnings.catch_warnings(record=True) as w:
            label.data_point = np.array([10.0, 20.0])
        self.assertEqual(w, [])

    def test_label_axis(self):
        axis = LabelAxis()
        with warnings.catch_warnings(record=True) as w:
            axis.positions = np.arange(10)
        self.assertEqual(w, [])
