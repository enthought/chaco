#!/usr/bin/env python
"""
Draws an simple RGB image
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".
"""

# Major library imports
from numpy import zeros, uint8

from enthought.chaco2.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable2.api import Window

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, Plot
from enthought.chaco2.tools.api import PanTool, SimpleZoom
from enthought.chaco2.tools.image_inspector_tool import ImageInspectorTool, \
     ImageInspectorOverlay


class PlotFrame(DemoFrame):

    def _create_window(self):

        # Create some RGB image data
        image = zeros((200,400,3), dtype=uint8)
        image[:,0:40,0] += 255     # Vertical red stripe
        image[0:20,:,1] += 255     # Horizontal green stripe; also yellow square
        image[-80:,-160:,2] += 255 # Blue square
        
        # Create a plot data obect and give it this data
        pd = ArrayPlotData()
        pd.set_data("imagedata", image)

        # Create the plot
        plot = Plot(pd)
        img_plot = plot.img_plot("imagedata")[0]

        # Tweak some of the plot properties
        plot.bgcolor = "white"

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot, constrain_key="shift"))
        plot.overlays.append(SimpleZoom(component=plot, 
                                        tool_mode="box", always_on=False))

        imgtool = ImageInspectorTool(img_plot)
        plot.tools.append(imgtool)
        plot.overlays.append(ImageInspectorOverlay(image_inspector=imgtool))
        # Return a window containing our plot
        return Window(self, -1, component=plot, bg_color="lightgray")

if __name__ == "__main__":
    demo_main(PlotFrame, size=(600,600), title="Simple image plot")

