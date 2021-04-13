""" Tests for the ImageInspectorTool and ImageInspectorOverlay tools.
"""

from unittest import TestCase
import numpy as np
from numpy.testing import assert_array_equal

from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import ImageInspectorTool, ImageInspectorOverlay
from enable.testing import EnableTestAssistant
from traits.testing.api import UnittestTools


def create_image_plot(img_values, **kwargs):
    data = ArrayPlotData(img=img_values)
    plot = Plot(data)
    plot.img_plot("img", **kwargs)
    return plot


class CustomImageInspectorOverlay(ImageInspectorOverlay):
    def _build_text_from_event(self, event):
        return "Position: ({}, {})".format(*event["indices"])


class BaseImageInspectorTool(EnableTestAssistant, UnittestTools):
    def setUp(self):
        # Control the pixel size of the plot to know where the tiles are:
        self.plot.bounds = [100, 100]
        self.plot._window = self.create_mock_window()
        renderer = self.plot.plots["plot0"][0]
        self.tool = ImageInspectorTool(component=renderer)
        self.overlay = ImageInspectorOverlay(
            component=renderer, image_inspector=self.tool
        )
        self.overlay2 = CustomImageInspectorOverlay(
            component=renderer, image_inspector=self.tool
        )
        self.plot.active_tool = self.tool
        self.plot.do_layout()

        self.insp_event = None

    def test_mouse_move_records_last_position(self):
        tool = self.tool

        self.assertEqual(tool.last_mouse_position, ())

        self.mouse_move(tool, 0, 0)
        self.assertEqual(tool.last_mouse_position, (0, 0))

        self.mouse_move(tool, 10, 10)
        self.assertEqual(tool.last_mouse_position, (10, 10))

        self.mouse_leave(tool, 1000, 1000)
        self.assertEqual(tool.last_mouse_position, (10, 10))

    def test_mouse_move_custom_overlay(self):
        tool = self.tool

        # Add a listener to catch the emitted event:
        tool.observe(self.store_inspector_event, "new_value")
        try:
            self.assertIsNone(self.insp_event)

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitChanges(self.overlay2, "text", 1):
                    self.mouse_move(tool, 0, 0)

            self.assertEqual(self.overlay2.text, "Position: (0, 0)")
        finally:
            tool.observe(self.store_inspector_event, "new_value", remove=True)

    # Helper methods ----------------------------------------------------------

    def store_inspector_event(self, event):
        self.insp_event = event.new


class TestImageInspectorToolGray(BaseImageInspectorTool, TestCase):
    """Tests for the ImageInspector tool with a gray scale image"""

    def setUp(self):
        values = np.arange(4).reshape(2, 2)
        self.plot = create_image_plot(values)
        super(TestImageInspectorToolGray, self).setUp()

    def test_mouse_move_collect_image_info(self):
        tool = self.tool

        # Add a listener to catch the emitted event:
        tool.observe(self.store_inspector_event, "new_value")
        try:
            self.assertIsNone(self.insp_event)

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitChanges(self.overlay, "text", 1):
                    self.mouse_move(tool, 0, 0)
                    self.assertEqual(self.insp_event["color_value"], 0)
                    self.assertEqual(self.insp_event["indices"], (0, 0))

                    self.assertEqual(self.overlay.text, "(0, 0)\n0")

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitChanges(self.overlay, "text", 1):
                    # Move within the same tile:
                    self.mouse_move(tool, 90, 0)
                    self.assertEqual(self.insp_event["color_value"], 1)
                    self.assertEqual(self.insp_event["indices"], (1, 0))

                    self.assertEqual(self.overlay.text, "(1, 0)\n1")

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitDoesNotChange(self.overlay, "text"):
                    # Move within the same tile:
                    self.mouse_move(tool, 91, 0)
                    self.assertEqual(self.insp_event["color_value"], 1)
                    self.assertEqual(self.insp_event["indices"], (1, 0))

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitChanges(self.overlay, "text", 1):
                    # Move to another value in the image:
                    self.mouse_move(tool, 0, 90)
                    self.assertEqual(self.insp_event["color_value"], 2)
                    self.assertEqual(self.insp_event["indices"], (0, 1))

                    self.assertEqual(self.overlay.text, "(0, 1)\n2")

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitChanges(self.overlay, "text", 1):
                    # Move within the same tile:
                    self.mouse_move(tool, 90, 90)
                    self.assertEqual(self.insp_event["color_value"], 3)
                    self.assertEqual(self.insp_event["indices"], (1, 1))

                    self.assertEqual(self.overlay.text, "(1, 1)\n3")

        finally:
            tool.observe(self.store_inspector_event, "new_value", remove=True)


class TestImageInspectorToolRGB(BaseImageInspectorTool, TestCase):
    """Tests for the ImageInspector tool with an RGB image."""

    def setUp(self):
        values = np.arange(12).reshape(2, 2, 3)
        self.plot = create_image_plot(values)
        super(TestImageInspectorToolRGB, self).setUp()

    def test_mouse_move_collect_image_info(self):
        tool = self.tool

        # Add a listener to catch the emitted event:
        tool.observe(self.store_inspector_event, "new_value")
        try:
            self.assertIsNone(self.insp_event)

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitChanges(self.overlay, "text", 1):
                    self.mouse_move(tool, 0, 0)
                    assert_array_equal(
                        self.insp_event["color_value"], np.array([0, 1, 2])
                    )
                    self.assertEqual(self.insp_event["indices"], (0, 0))

                    self.assertEqual(self.overlay.text, "(0, 0)\n(0, 1, 2)")

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitChanges(self.overlay, "text", 1):
                    # Move within the same tile:
                    self.mouse_move(tool, 90, 0)
                    assert_array_equal(
                        self.insp_event["color_value"], np.array([3, 4, 5])
                    )
                    self.assertEqual(self.insp_event["indices"], (1, 0))

                    self.assertEqual(self.overlay.text, "(1, 0)\n(3, 4, 5)")

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitDoesNotChange(self.overlay, "text"):
                    # Move within the same tile:
                    self.mouse_move(tool, 91, 0)
                    assert_array_equal(
                        self.insp_event["color_value"], np.array([3, 4, 5])
                    )
                    self.assertEqual(self.insp_event["indices"], (1, 0))

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitChanges(self.overlay, "text", 1):
                    # Move to another value in the image:
                    self.mouse_move(tool, 0, 90)
                    assert_array_equal(
                        self.insp_event["color_value"], np.array([6, 7, 8])
                    )
                    self.assertEqual(self.insp_event["indices"], (0, 1))

                    self.assertEqual(self.overlay.text, "(0, 1)\n(6, 7, 8)")

            with self.assertTraitChanges(tool, "new_value", 1):
                with self.assertTraitChanges(self.overlay, "text", 1):
                    # Move within the same tile:
                    self.mouse_move(tool, 90, 90)
                    assert_array_equal(
                        self.insp_event["color_value"], np.array([9, 10, 11])
                    )
                    self.assertEqual(self.insp_event["indices"], (1, 1))

                    self.assertEqual(self.overlay.text, "(1, 1)\n(9, 10, 11)")

        finally:
            tool.observe(self.store_inspector_event, "new_value", remove=True)
