# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Unit tests for scatter_1d function
"""

from numpy import sort
from numpy.random import random, randint, uniform
import unittest
from chaco.api import ArrayPlotData, Plot


class Scatter1DTestCase(unittest.TestCase):
    def test_default_marker_size(self):
        # Create some data
        numpts = 50
        x = sort(random(numpts))
        y = random(numpts)

        # Create a plot data object and give it this data
        pd = ArrayPlotData()
        pd.set_data("index", x)
        pd.set_data("value", y)

        # Create the plot
        plot = Plot(pd, use_backbuffer=True, auto_grid=False)

        plot.plot_1d(
            "value",
            type="scatter_1d",
            orientation="v",
            marker="plus",
            alignment="left"
        )

    def test_int_marker_size(self):
        # Create some data
        numpts = 50
        x = sort(random(numpts))
        y = random(numpts)

        # Create a plot data object and give it this data
        pd = ArrayPlotData()
        pd.set_data("index", x)
        pd.set_data("value", y)

        # Create the plot
        plot = Plot(pd, use_backbuffer=True, auto_grid=False)

        plot.plot_1d(
            "value",
            type="scatter_1d",
            orientation="v",
            marker="plus",
            alignment="left",
            marker_size=5
        )

    def test_float_marker_size(self):
        # Create some data
        numpts = 50
        x = sort(random(numpts))
        y = random(numpts)

        # Create a plot data object and give it this data
        pd = ArrayPlotData()
        pd.set_data("index", x)
        pd.set_data("value", y)

        # Create the plot
        plot = Plot(pd, use_backbuffer=True, auto_grid=False)

        plot.plot_1d(
            "value",
            type="scatter_1d",
            orientation="v",
            marker="plus",
            alignment="left",
            marker_size=5.0
        )

    def test_int_arr_marker_size(self):
        # Create some data
        numpts = 50
        x = sort(random(numpts))
        y = random(numpts)

        # Create a plot data object and give it this data
        pd = ArrayPlotData()
        pd.set_data("index", x)
        pd.set_data("value", y)

        # Create the plot
        plot = Plot(pd, use_backbuffer=True, auto_grid=False)

        plot.plot_1d(
            "value",
            type="scatter_1d",
            orientation="v",
            marker="plus",
            alignment="left",
            marker_size=randint(1, 5, numpts)
        )

    def test_float_arr_marker_size(self):
        # Create some data
        numpts = 50
        x = sort(random(numpts))
        y = random(numpts)

        # Create a plot data object and give it this data
        pd = ArrayPlotData()
        pd.set_data("index", x)
        pd.set_data("value", y)

        # Create the plot
        plot = Plot(pd, use_backbuffer=True, auto_grid=False)

        plot.plot_1d(
            "value",
            type="scatter_1d",
            orientation="v",
            marker="plus",
            alignment="left",
            marker_size=uniform(1, 5, numpts)
        )
