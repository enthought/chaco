""" Test for the deprecation of VariableSizeScatterPlot """
import unittest

from chaco.api import VariableSizeScatterPlot


class TestDeprecated(unittest.TestCase):

    def test_deprecation_warning(self):
        with self.assertWarns(DeprecationWarning):
            VariableSizeScatterPlot()
