"""
Draws a static polar plot.
"""

# Major library imports
from numpy import arange, pi, sin, cos

from enthought.enable2.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable2.api import Window
from enthought.traits.api import false

# Chaco imports
from enthought.chaco2.api import create_polar_plot

class MyFrame(DemoFrame):
    def _create_window(self):
        # Create theta data
        numpoints = 5000
        low = 0
        high = 2*pi
        theta = arange(low, high, (high-low) / numpoints)

        # Create the radius data
        radius = cos(3*theta)

        # Create a new polar plot with radius and theta data
        plot = create_polar_plot((radius,theta),color=(0.0,0.0,1.0,1), width=4.0)

        return Window(self, -1, component=plot)

if __name__ == "__main__":
    demo_main(MyFrame, size=(600,600), title="Simple Polar Plot")

# EOF#######################
