""" Test for the deprecation of VariableSizeScatterPlot """
import unittest


class TestDeprecated(unittest.TestCase):

    def test_deprecation_warning(self):
        with self.assertWarns(DeprecationWarning):
            from chaco.api import VariableSizeScatterPlot  # noqa: F401
