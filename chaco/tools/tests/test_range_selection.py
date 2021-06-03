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

from chaco.api import LinearMapper
from chaco.array_plot_data import ArrayPlotData
from chaco.plot import Plot
from chaco.tools.range_selection import RangeSelection
from enable.testing import EnableTestAssistant


class RangeSelectionTestCase(EnableTestAssistant, unittest.TestCase):
    def test_selecting_mouse_leave_clipping(self):
        # Regression test for #216.
        plot_data = ArrayPlotData()
        arr = np.arange(4.0)
        plot_data.set_data("x", arr)
        plot_data.set_data("y", arr)

        for origin in ("bottom left", "top left", "bottom right", "top right"):
            for orientation in ("h", "v"):
                for axis in ("index", "value"):
                    plot = Plot(
                        plot_data, orientation=orientation, origin="top right"
                    )

                    renderer = plot.plot(("x", "y"))[0]
                    renderer.bounds = [10, 20]
                    tool = RangeSelection(
                        renderer,
                        left_button_selects=True,
                        axis=axis,
                    )
                    renderer.tools.append(tool)

                    low_x, low_y = plot.position
                    high_x = low_x + renderer.bounds[0] - 1
                    high_y = low_y + renderer.bounds[1] - 1

                    cx = 5
                    cy = 5

                    bounds = (
                        (low_x - 1, low_y),
                        (high_x + 1, low_y),
                        (low_x, low_y - 1),
                        (low_x, high_y + 1),
                    )
                    for x, y in bounds:
                        self.mouse_down(tool, x=cx, y=cy)
                        self.mouse_leave(tool, x=x, y=y)
                        selection = tool.selection
                        self.assertTrue(selection[0] <= selection[1])
                        self.mouse_up(tool, x=x, y=y)

    def test_selection_no_warning(self):
        plot_data = ArrayPlotData()
        arr = np.arange(4)
        plot_data.set_data("x", arr)
        plot_data.set_data("y", arr)
        plot = Plot(plot_data)
        renderer = plot.plot(("x", "y"))[0]
        tool = RangeSelection(renderer)
        with warnings.catch_warnings(record=True) as w:
            # Ignore warnings coming from any package other than Chaco
            warnings.filterwarnings(
                "ignore",
                module="(?!chaco)",
            )
            tool.selection = np.array([2.0, 3.0])

        self.assertEqual(w, [])

        # Accept tuples and lists and None
        tool.selection = (1.5, 3.5)
        tool.selection = [1.0, 2.0]
        tool.selection = None

    # regression test for enthought/chaco#597
    @unittest.mock.patch('chaco.tools.range_selection.RangeSelection.deselect')
    def test_notifiers_connected(self, mocked_deselect):
        plot_data = ArrayPlotData()
        arr = np.arange(4.0)
        plot_data.set_data("x", arr)
        plot_data.set_data("y", arr)

        plot = Plot(plot_data)

        renderer = plot.plot(("x", "y"))[0]
        tool = RangeSelection(renderer)
        renderer.tools.append(tool)

        # attempt to trigger change handler for the index_mapper trait on the
        # RangeSelection tool's plot
        # assign a new mapper with same attrs
        renderer.index_mapper = LinearMapper(
            range=renderer.index_mapper.range,
            stretch_data=renderer.index_mapper.stretch_data
        )

        mocked_deselect.assert_called_once()

    # regression test for enthought/chaco#597
    @unittest.mock.patch('chaco.tools.range_selection.RangeSelection.deselect')
    def test_notifiers_connected_specify_plot(self, mocked_deselect):
        plot_data = ArrayPlotData()
        arr = np.arange(4.0)
        plot_data.set_data("x", arr)
        plot_data.set_data("y", arr)

        plot = Plot(plot_data)

        renderer = plot.plot(("x", "y"))[0]
        tool = RangeSelection(renderer)
        renderer.tools.append(tool)

        new_renderer = plot.plot(("x", "y"), type='scatter')[0]
        tool.plot = new_renderer

        # attempt to trigger change handler for the index_mapper trait on the
        # RangeSelection tool's plot
        # assign a new mapper with same attrs
        new_renderer.index_mapper = LinearMapper(
            range=new_renderer.index_mapper.range,
            stretch_data=new_renderer.index_mapper.stretch_data
        )

        mocked_deselect.assert_called_once()
