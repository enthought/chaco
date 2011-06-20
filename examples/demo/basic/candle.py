"""
Demonstrates candlestick plots.

 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
from numpy import abs, arange, cumprod, random, vstack

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

    returns = random.lognormal(0.00, 0.04, size=numpoints)
    average = 100.0 * cumprod(returns)
    high = average + abs(random.normal(0, 20.0, size=numpoints))
    low = average - abs(random.normal(0, 20.0, size=numpoints))
    delta = high - low
    open = low + delta * random.uniform(0.05, 0.95, size=numpoints)
    close = low + delta * random.uniform(0.05, 0.95, size=numpoints)
    sorted_vals = vstack((open, high, low, close, average))
    sorted_vals.sort(0)
    return index, sorted_vals

def _create_plot_component():

    # Create some data
    index, sorted_vals = _create_data(200)

    # Create a plot data obect and give it this data
    pd = ArrayPlotData(index = index,
                       min = sorted_vals[0],
                       bar_min = sorted_vals[1],
                       average = sorted_vals[2],
                       bar_max = sorted_vals[3],
                       max = sorted_vals[4])

    # Create the plot
    plot = Plot(pd)
    plot.candle_plot(("index", "min", "bar_min", "average", "bar_max", "max"),
                     color = "lightgray",
                     bar_line_color = "black",
                     stem_color = "blue",
                     center_color = "red",
                     center_width = 2)

    # Tweak some of the plot properties
    plot.title = "Candlestick Plot"
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
title = "Candlestick plot"
bg_color="lightgray"

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
