#!/usr/bin/env python
"""
Similar to grid_container.py, but demonstrates Chaco's capability to used
a fixed screen space aspect ratio for plot components.
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

from chaco.example_support import COLOR_PALETTE

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View


# Chaco imports
from chaco.api import ArrayPlotData, GridContainer, Plot
from chaco.tools.api import PanTool, ZoomTool


#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    # Create a GridContainer to hold all of our plots
    container = GridContainer(padding=20, fill_padding=True,
                              bgcolor="lightgray", use_backbuffer=True,
                              shape=(3,3), spacing=(12,12))

    # Create the initial series of data
    x = linspace(-5, 15.0, 100)
    pd = ArrayPlotData(index = x)

    # Plot some bessel functions and add the plots to our container
    for i in range(9):
        pd.set_data("y" + str(i), jn(i,x))
        plot = Plot(pd)
        plot.plot(("index", "y" + str(i)),
                  color=tuple(COLOR_PALETTE[i]), line_width=2.0,
                  bgcolor = "white", border_visible=True)

        # Tweak some of the plot properties
        plot.border_width = 1
        plot.padding = 10

        # Set each plot's aspect ratio based on its position in the
        # 3x3 grid of plots.
        n,m = divmod(i, 3)
        plot.aspect_ratio = float(n+1) / (m+1)

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Add to the grid container
        container.add(plot)
    return container

#===============================================================================
# Attributes to use for the plot view.
size=(1000,800)
title="Grid Container with Fixed Aspect ratio"

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
                    resizable=True, title=title
                    )
    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

# EOF
