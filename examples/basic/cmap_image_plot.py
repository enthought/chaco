#!/usr/bin/env python
"""
Draws an colormapped image plot
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".
"""

# Major library imports
from numpy import exp, linspace, meshgrid, pi, sin

from enthought.enable2.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable2.api import Window

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, jet, Plot
from enthought.chaco2.tools.api import PanTool, SimpleZoom


class PlotFrame(DemoFrame):

    def _create_window(self):

        # Create a scalar field to colormap
        xs = linspace(0, 10, 30)
        ys = linspace(0, 5, 600)
        x, y = meshgrid(xs,ys)
        z = exp(-(x**2+y**2)/100)

        # Create a plot data obect and give it this data
        pd = ArrayPlotData()
        pd.set_data("imagedata", z)

        # Create the plot
        plot = Plot(pd)
        plot.img_plot("imagedata", 
                      xbounds=xs,
                      ybounds=ys,
                      colormap=jet)

        # Tweak some of the plot properties
        plot.title = "My First Image Plot"
        plot.padding = 50

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot))
        zoom = SimpleZoom(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Return a window containing our plot
        return Window(self, -1, component=plot)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,600), title="Basic Colormapped Image Plot")

