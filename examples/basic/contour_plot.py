#!/usr/bin/env python
"""
Draws a contour polygon plot with a contour line plot on top 
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".
"""

# Major library imports
from numpy import cosh, exp, linspace, meshgrid, pi, tanh

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, jet, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create a scalar field to contour
    xs = linspace(-2*pi, 2*pi, 600)
    ys = linspace(-1.5*pi, 1.5*pi, 300)
    x, y = meshgrid(xs,ys)
    z = tanh(x*y/6)*cosh(exp(-y**2)*x/3)
    z = x*y

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("imagedata", z)

    # Create a contour polygon plot of the data
    plot = Plot(pd, default_origin="top left")
    plot.contour_plot("imagedata", 
                      type="poly",
                      poly_cmap=jet,
                      xbounds=(xs[0], xs[-1]), 
                      ybounds=(ys[0], ys[-1]))

    # Create a contour line plot for the data, too
    plot.contour_plot("imagedata", 
                      type="line",
                      xbounds=(xs[0], xs[-1]), 
                      ybounds=(ys[0], ys[-1]))

    # Tweak some of the plot properties
    plot.title = "My First Contour Plot"
    plot.padding = 50
    plot.bg_color = "white"
    plot.fill_padding = True 

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)
    return plot

#===============================================================================
# Attributes to use for the plot view.
size = (800, 600)
title = "Basic Contour Plot"
        
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

