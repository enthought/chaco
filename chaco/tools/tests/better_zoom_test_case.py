import unittest

import numpy

from chaco.api import create_line_plot
from chaco.tools.api import BetterZoom
from enable.testing import EnableTestAssistant
from traits.testing.api import UnittestTools

class TestBetterZoomTool(EnableTestAssistant, UnittestTools, unittest.TestCase):
    """ Tests for the TraversePolyLine enable tool """

    def setUp(self):
        values = numpy.arange(10)
        self.plot = create_line_plot((values, values))
        self.plot.bounds = [100, 100]
        self.plot._window = self.create_mock_window()
        self.tool = BetterZoom(component=self.plot)
        self.plot.active_tool = self.tool
        self.plot.do_layout()

    def tearDown(self):
        del self.tool
        del self.plot

    def test_default_position(self):
        tool = self.tool

        # this doesn't throw an exception
        self.send_key(tool, '+')

        self.assertEqual(tool.position, (50, 50))

        # expected behaviour for a normal zoom in operation
        self.assertNotEqual(tool._index_factor, 1.0)
        self.assertNotEqual(tool._value_factor, 1.0)
        self.assertEqual(len(tool._history), 2)
