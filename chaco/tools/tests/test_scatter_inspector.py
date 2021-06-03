# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for the ScatterInspector Chaco tool
"""

from unittest import TestCase
import numpy

from chaco.api import create_scatter_plot
from chaco.tools.api import ScatterInspector
from enable.testing import EnableTestAssistant
from traits.testing.api import UnittestTools


class TestScatterInspectorTool(EnableTestAssistant, TestCase, UnittestTools):
    """ Tests for the ScatterInspector tool """

    def setUp(self):
        values = numpy.arange(10)
        self.plot = create_scatter_plot((values, values))
        self.plot.bounds = [100, 100]
        self.plot._window = self.create_mock_window()
        self.tool = ScatterInspector(component=self.plot)
        self.plot.active_tool = self.tool
        self.plot.do_layout()

        self.insp_event = None

    def tearDown(self):
        del self.tool
        del self.plot

    def test_default_state(self):
        tool = self.tool
        hover_name = tool.hover_metadata_name
        selection_name = tool.selection_metadata_name
        index_md = tool.component.index.metadata
        value_md = tool.component.value.metadata

        self.assertEqual(index_md[selection_name], [])
        self.assertEqual(value_md[selection_name], [])

        self.assertNotIn(hover_name, index_md)
        self.assertNotIn(hover_name, value_md)

    def test_hover(self):
        tool = self.tool
        name = tool.hover_metadata_name
        index_md = tool.component.index.metadata
        value_md = tool.component.value.metadata

        # Move to first point
        self.mouse_move(tool, 0, 0)
        self.assertEqual(index_md[name], [0])
        self.assertEqual(value_md[name], [0])

        # Move to off diagonal to not be close to a scatter point:
        self.mouse_move(tool, 10, 0)
        self.assertNotIn(name, index_md)
        self.assertNotIn(name, value_md)

        # Move to second point
        self.mouse_move(tool, 10, 10)
        self.assertEqual(index_md[name], [1])
        self.assertEqual(value_md[name], [1])

    def test_select(self):
        tool = self.tool
        name = tool.selection_metadata_name
        index_md = tool.component.index.metadata
        value_md = tool.component.value.metadata

        # Click on first point
        self.mouse_down(tool, 0, 0)
        self.assertEqual(index_md[name], [0])
        self.assertEqual(value_md[name], [0])

        # Click on second point
        self.mouse_down(tool, 10, 10)
        self.assertEqual(index_md[name], [0, 1])
        self.assertEqual(value_md[name], [0, 1])

    def test_unselect(self):
        tool = self.tool
        name = tool.selection_metadata_name
        index_md = tool.component.index.metadata
        value_md = tool.component.value.metadata

        self.mouse_down(tool, 0, 0)
        self.mouse_down(tool, 10, 10)
        self.assertEqual(index_md[name], [0, 1])
        self.assertEqual(value_md[name], [0, 1])

        # Deselect the second point
        self.mouse_down(tool, 10, 10)
        self.assertEqual(index_md[name], [0])
        self.assertEqual(value_md[name], [0])

        # Deselect the first point
        self.mouse_down(tool, 0, 0)
        self.assertEqual(index_md[name], [])
        self.assertEqual(value_md[name], [])

    def test_hover_triggers_event(self):
        tool = self.tool

        # Add a listener to catch the emitted event:
        tool.observe(self.store_inspector_event, "inspector_event")
        try:
            self.assertIsNone(self.insp_event)

            # Move to the first scatter point
            with self.assertTraitChanges(tool, "inspector_event", 1):
                self.mouse_move(tool, 0, 0)

                self.assertEqual(self.insp_event.event_type, "hover")
                self.assertEqual(self.insp_event.event_index, 0)

            # Moving around the same scatter point doesn't trigger events:
            with self.assertTraitDoesNotChange(tool, "inspector_event"):
                self.mouse_move(tool, 1, 0)

            # Leave the scatter point event:
            with self.assertTraitChanges(tool, "inspector_event", 1):
                self.mouse_move(tool, 10, 0)
                self.assertEqual(self.insp_event.event_type, "hover")
                self.assertEqual(self.insp_event.event_index, None)

            # Move to the second scatter point
            with self.assertTraitChanges(tool, "inspector_event", 1):
                self.mouse_move(tool, 10, 10)

                self.assertEqual(self.insp_event.event_type, "hover")
                self.assertEqual(self.insp_event.event_index, 1)
        finally:
            tool.observe(
                self.store_inspector_event, "inspector_event", remove=True
            )

    def test_select_triggers_event(self):
        tool = self.tool

        # Add a listener to catch the emitted event:
        tool.observe(self.store_inspector_event, "inspector_event")
        try:
            self.assertIsNone(self.insp_event)

            # Select the first scatter point
            with self.assertTraitChanges(tool, "inspector_event", 1):
                self.mouse_down(tool, 0, 0)

                self.assertEqual(self.insp_event.event_type, "select")
                self.assertEqual(self.insp_event.event_index, 0)

            # Leave the scatter point event:
            with self.assertTraitChanges(tool, "inspector_event", 1):
                self.mouse_down(tool, 10, 10)
                self.assertEqual(self.insp_event.event_type, "select")
                self.assertEqual(self.insp_event.event_index, 1)

            # Deselect the second scatter point
            with self.assertTraitChanges(tool, "inspector_event", 1):
                self.mouse_down(tool, 10, 10)

                self.assertEqual(self.insp_event.event_type, "deselect")
                self.assertEqual(self.insp_event.event_index, 1)
        finally:
            tool.observe(
                self.store_inspector_event, "inspector_event", remove=True
            )

    # Helper methods ----------------------------------------------------------

    def store_inspector_event(self, event):
        self.insp_event = event.new
