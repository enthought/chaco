# Copyright (c) 2014, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.

""" Tests for the BetterZoom Chaco tool """

import unittest

import numpy

from chaco.api import create_line_plot
from chaco.tools.api import BetterZoom
from enable.testing import EnableTestAssistant


class TestBetterZoomTool(EnableTestAssistant, unittest.TestCase):
    """ Tests for the BetterZoom Chaco tool """

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
