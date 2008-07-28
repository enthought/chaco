#!/usr/bin/env python
""" Demonstrates the ImageInspectorTool and overlay on a colormapped image
plot.  The underlying plot is similar to the one in cmap_image_plot.py.

 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".

 - Pressing "p" will toggle the display of the image inspector overlay.
"""

# Major library imports
from numpy import linspace, meshgrid, pi, sin

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window

# Chaco imports
from enthought.chaco.api import ArrayPlotData, jet, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool
from enthought.chaco.tools.image_inspector_tool import ImageInspectorTool, \
     ImageInspectorOverlay


class PlotFrame(DemoFrame):

    def _create_window(self):

        # Create a scalar field to colormap
        xs = linspace(-2*pi, 2*pi, 600)
        ys = linspace(-1.5*pi, 1.5*pi, 300)
        x, y = meshgrid(xs,ys)
        z = sin(x)*y

        # Create a plot data obect and give it this data
        pd = ArrayPlotData()
        pd.set_data("imagedata", z)

        # Create the plot
        plot = Plot(pd)
        img_plot = plot.img_plot("imagedata", 
                                 xbounds=xs,
                                 ybounds=ys,
                                 colormap=jet)[0]

        # Tweak some of the plot properties
        plot.title = "My First Image Plot"
        plot.padding = 50

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)
        imgtool = ImageInspectorTool(img_plot)
        img_plot.tools.append(imgtool)
        overlay = ImageInspectorOverlay(component=img_plot, image_inspector=imgtool,
                                        bgcolor="white", border_visible=True)

        img_plot.overlays.append(overlay)
        

        # Return a window containing our plot
        return Window(self, -1, component=plot)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,600), title="Inspecting a Colormapped Image Plot")

