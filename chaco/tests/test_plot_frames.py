""" Test for the deprecation of PlotFrames """
import unittest

from chaco.api import BasePlotFrame, CrossPlotFrame, SimplePlotFrame


class TestDeprecated(unittest.TestCase):

    def test_deprecation_warnings(self):
        with self.assertWarns(DeprecationWarning):
            BasePlotFrame()

    def test_cross_deprecation_warning(self):
        with self.assertWarns(DeprecationWarning):
            CrossPlotFrame()

    def test_simple_deprecation_warning(self):
        with self.assertWarns(DeprecationWarning):
            SimplePlotFrame()
