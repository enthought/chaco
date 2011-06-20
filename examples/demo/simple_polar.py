"""
Draws a static polar plot.
"""

# Major library imports
from numpy import arange, pi, cos

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import create_polar_plot

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create theta data
    numpoints = 5000
    low = 0
    high = 2*pi
    theta = arange(low, high, (high-low) / numpoints)

    # Create the radius data
    radius = cos(3*theta)

    # Create a new polar plot with radius and theta data
    plot = create_polar_plot((radius,theta),color=(0.0,0.0,1.0,1), width=4.0)

    return plot

#===============================================================================
# Attributes to use for the plot view.
size=(600,600)
title="Simple Polar Plot"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title,
                    width=size[0], height=size[1]
                    )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

# EOF#######################
