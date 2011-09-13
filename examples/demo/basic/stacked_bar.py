"""
Demonstrates stacked bar plots.

 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
from numpy import abs, arange, cumprod, ones, random, vstack

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================

def _create_data(numpoints):
    index = arange(numpoints)

    returns1 = random.random(numpoints)/4.0
    returns2 = random.random(numpoints)/4.0
    returns3 = random.random(numpoints)/4.0
    returns4 = 1.0 - (returns1 + returns2 + returns3)
    vals = vstack((returns1, returns2, returns3, returns4))
    #vals.sort(0)
    return index, vals

def _create_plot_component():

    # Create some data
    index, vals = _create_data(20)

    # Create a plot data object and give it this data
    pd = ArrayPlotData(index = index,
                       values = vals)

    # Create the plot
    plot = Plot(pd)
    plot.stacked_bar_plot(("index", "values"),
                     color = ["red", "yellow", "green", "blue"],
                     outline_color = "lightgray",)

    # Tweak some of the plot properties
    plot.title = "Stacked Bar Plot"
    plot.line_width = 0.5
    plot.padding = 50

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot, constrain_key="shift"))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    return plot

#===============================================================================
# Attributes to use for the plot view.
size = (650, 650)
title = "Stacked Bar Plot"
bg_color="transparent"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title
                    )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

#--EOF---
