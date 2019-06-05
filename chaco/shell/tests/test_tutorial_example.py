""" Test script-oriented example from interactive plotting tutorial

source: docs/source/user_manual/chaco_tutorial.rst

"""
import unittest

from numpy import linspace, pi, sin

from traits.etsconfig.api import ETSConfig
from chaco.shell import plot, title, ytitle


@unittest.skipIf(
    ETSConfig.toolkit=='null', "Skip on 'null' toolkit")
class InteractiveTestCase(unittest.TestCase):

    def test_script(self):
        x = linspace(-2*pi, 2*pi, 100)
        y = sin(x)
        plot(x, y, "r-")
        title("First plot")
        ytitle("sin(x)")

if __name__ == "__main__":
    unittest.main()
