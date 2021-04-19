""" Test for the deprecation of PlotFrames """
import unittest
import warnings


class TestDeprecated(unittest.TestCase):

    def test_deprecation_warnings(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with self.assertRaises(DeprecationWarning):
                from chaco.api import BasePlotFrame  # noqa: F401

    def test_cross_deprecation_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with self.assertRaises(DeprecationWarning):
                from chaco.api import CrossPlotFrame  # noqa: F401

    def test_simple_deprecation_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with self.assertRaises(DeprecationWarning):
                from chaco.api import SimplePlotFrame  # noqa: F401
