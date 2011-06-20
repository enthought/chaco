#!/usr/bin/env python
"""
Draws some x-y line and scatter plots. On the left hand plot:
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, HPlotContainer, Plot
from chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some x-y data series to plot
    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(index = x)
    for i in range(5):
        pd.set_data("y" + str(i), jn(i,x))

    # Create some line plots of some of the data
    plot1 = Plot(pd, title="Line Plot", padding=50, border_visible=True)
    plot1.legend.visible = True
    plot1.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="red")
    plot1.plot(("index", "y3"), name="j_3", color="blue")

    # Attach some tools to the plot
    plot1.tools.append(PanTool(plot1))
    zoom = ZoomTool(component=plot1, tool_mode="box", always_on=False)
    plot1.overlays.append(zoom)

    # Create a second scatter plot of one of the datasets, linking its
    # range to the first plot
    plot2 = Plot(pd, range2d=plot1.range2d, title="Scatter plot", padding=50,
                 border_visible=True)
    plot2.plot(('index', 'y3'), type="scatter", color="blue", marker="circle")

    # Create a container and add our plots
    container = HPlotContainer()
    container.add(plot1)
    container.add(plot2)

    return container

#===============================================================================
# Attributes to use for the plot view.
size=(900,500)
title="Basic x-y plots"

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

#--EOF---
