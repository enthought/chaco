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

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, VPlotContainer, \
    Plot
from enthought.chaco.plotscrollbar import PlotScrollBar
from enthought.chaco.tools.api import PanTool, ZoomTool 

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
    plot1 = Plot(pd, padding=50)
    plot1.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="red")
    plot1.plot(("index", "y3"), name="j_3", color="blue")

    # Attach some tools to the plot
    plot1.tools.append(PanTool(plot1))
    zoom = ZoomTool(component=plot1, tool_mode="box", always_on=False)
    plot1.overlays.append(zoom)
    
    # Add the scrollbar
    hscrollbar = PlotScrollBar(component=plot1, axis="index", resizable="h",
                               height=15)
    plot1.padding_top = 0
    hscrollbar.force_data_update()

    # Create a container and add our plots
    container = VPlotContainer()
    container.add(plot1)
    container.add(hscrollbar)

    return container

#===============================================================================
# Attributes to use for the plot view.
size=(900,500)
title="Scrollbar example"
        
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

#===============================================================================
# Stand-alone frame to display the plot.
#===============================================================================
class PlotFrame(DemoFrame):

    def _create_window(self):
        # Return a window containing our plots
        return Window(self, -1, component=_create_plot_component())
    
if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

#--EOF---
