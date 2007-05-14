#!/usr/bin/env python
"""
Draws several overlapping line plots.  
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".
 - Right-click and dragging on the legend allows you to reposition the legend.
 - Double-clicking on line or scatter plots brings up a traits editor for the 
   plot.
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

# Enthought library imports
from enthought.enable2.wx_backend.api import Window

# Chaco imports
from enthought.chaco2.examples import DemoFrame, demo_main, COLOR_PALETTE
from enthought.chaco2.api import ArrayPlotData, GridContainer, Plot, PlotLabel
from enthought.chaco2.tools.api import PanTool, SimpleZoom



class PlotFrame(DemoFrame):

    def _create_window(self):
            
        # Create a GridContainer to hold all of our plots
        container = GridContainer(padding=20, fill_padding=True,
                                  bgcolor="lightgray", use_backbuffer=True,
                                  shape=(2,4), spacing=(12,12))
        
        # Create the initial series of data
        x = linspace(-5, 15.0, 100)
        pd = ArrayPlotData(index = x)
        
        # Plot some bessel functions and add the plots to our container
        for i in range(8):
            pd.set_data("y" + str(i), jn(i,x))
            plot = Plot(pd)
            plot.plot(("index", "y" + str(i)), 
                      color=tuple(COLOR_PALETTE[i]), width=2.0,
                      bgcolor = "white", border_visible=True)

            # Tweak some of the plot properties
            plot.border_width = 1
            plot.padding = 0

            # Attach some tools to the plot
            plot.tools.append(PanTool(plot))
            zoom = SimpleZoom(plot, tool_mode="box", always_on=False)
            plot.overlays.append(zoom)

            # Add to the grid container
            container.add(plot)

        # Set the upper-left plot to only be resizable vertically, and to have
        # a fixed horizontal width
        ul_plot = container.plot_components[0]
        ul_plot.set(resizable="v", padding_top=30, width=200)
        ul_plot.overlays.append(PlotLabel("Vertically resizable", 
                                          component=ul_plot))

        # Set the bottom center plot to have a fixed width and height
        cplot = container.plot_components[4]
        cplot.set(resizable="", padding_top = 30, bounds=[400,400])
        cplot.overlays.append(PlotLabel("Not resizable", component=cplot))

        # Return a window containing our plots
        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(1000,800), title="Grid Container")

