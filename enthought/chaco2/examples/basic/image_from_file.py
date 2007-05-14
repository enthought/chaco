#!/usr/bin/env python
"""
Draws an RGB image from disk
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".
"""



# Enthought library imports
from enthought.enable2.wx_backend.api import Window

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, ImageData, Plot
from enthought.chaco2.examples import DemoFrame, demo_main
from enthought.chaco2.tools.api import PanTool, SimpleZoom


class PlotFrame(DemoFrame):
    def _create_window(self):

        # Load the image from a file
        image = ImageData.fromfile("capitol.jpg")

        # Create a plot data obect and give it this image data
        pd = ArrayPlotData()
        pd.set_data("imagedata", image)

        # Create the plot
        plot = Plot(pd)
        plot.img_plot("imagedata")

        # Tweak some of the plot properties
        plot.title = "Image From File: capitol.jpg"
        plot.padding = 50

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot))
        zoom = SimpleZoom(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Return a window containing our plot
        return Window(self, -1, component=plot)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(650,650), title="Basic image from file")

# EOF
