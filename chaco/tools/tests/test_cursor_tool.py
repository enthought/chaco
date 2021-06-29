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

from enable.api import ComponentEditor
from enable.testing import EnableTestAssistant
from traits.api import HasTraits, Instance
from traits.etsconfig.api import ETSConfig
from traitsui.api import Item, View
from traitsui.testing.api import UITester

from chaco.api import ArrayPlotData, Plot
from chaco.tools.cursor_tool import CursorTool


class TestCursorTool(unittest.TestCase, EnableTestAssistant):

    # regression test for enthought/chaco#289
    @unittest.skipIf(ETSConfig.toolkit == "null", "Skip on 'null' toolkit")
    def test_use_with_log_mappers(self):
        class TestCursor(HasTraits):
            plot = Instance(Plot)

            traits_view = View(
                Item('plot', editor=ComponentEditor(), show_label=False),
                width=500,
                height=500,
                resizable=True
            )

            def _plot_default(self):
                arr = np.logspace(0, 10, num=10)
                data = ArrayPlotData(x=arr, y=arr)
                plot = Plot(data)
                renderer = plot.plot(
                    ("x", "y"),
                    index_scale="log",
                    value_scale="log"
                )[0]

                cursor = CursorTool(renderer)

                renderer.overlays.append(cursor)

                return plot

        tester = UITester()
        test_cursor = TestCursor()
        with tester.create_ui(test_cursor):
            # should not fail
            self.mouse_move(
                test_cursor.plot, 10, 10
            )

    @unittest.skipIf(ETSConfig.toolkit == "null", "Skip on 'null' toolkit")
    def test_use_with_linear_mappers(self):
        class TestCursor(HasTraits):
            plot = Instance(Plot)

            traits_view = View(
                Item('plot', editor=ComponentEditor(), show_label=False),
                width=500,
                height=500,
                resizable=True
            )

            def _plot_default(self):
                arr = np.logspace(0, 10, num=10)
                data = ArrayPlotData(x=arr, y=arr)
                plot = Plot(data)
                renderer = plot.plot(
                    ("x", "y"),
                )[0]

                cursor = CursorTool(renderer)

                renderer.overlays.append(cursor)

                return plot

        tester = UITester()
        test_cursor = TestCursor()
        with tester.create_ui(test_cursor):
            # should not fail
            self.mouse_move(
                test_cursor.plot, 10, 10
            )
