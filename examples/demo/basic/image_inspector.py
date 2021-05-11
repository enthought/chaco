#!/usr/bin/env python
"""
Demonstrates the ImageInspectorTool and overlay on a colormapped image
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

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, viridis, Plot
from chaco.tools.api import PanTool, ZoomTool
from chaco.tools.image_inspector_tool import (
    ImageInspectorTool,
    ImageInspectorOverlay,
)

# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================
def _create_plot_component():  # Create a scalar field to colormap
    xbounds = (-2 * pi, 2 * pi, 600)
    ybounds = (-1.5 * pi, 1.5 * pi, 300)
    xs = linspace(*xbounds)
    ys = linspace(*ybounds)
    x, y = meshgrid(xs, ys)
    z = sin(x) * y

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("imagedata", z)

    # Create the plot
    plot = Plot(pd)
    img_plot = plot.img_plot(
        "imagedata", xbounds=xbounds[:2], ybounds=ybounds[:2], colormap=viridis
    )[0]

    # Tweak some of the plot properties
    plot.title = "My First Image Plot"
    plot.padding = 50

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)
    imgtool = ImageInspectorTool(component=img_plot)
    img_plot.tools.append(imgtool)
    overlay = ImageInspectorOverlay(
        component=img_plot,
        image_inspector=imgtool,
        bgcolor="white",
        border_visible=True,
    )

    img_plot.overlays.append(overlay)
    return plot


# ===============================================================================
# Attributes to use for the plot view.
size = (800, 600)
title = "Inspecting a Colormapped Image Plot"

# ===============================================================================
# # Demo class that is used by the demo.py application.
# ===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
        Group(
            Item("plot", editor=ComponentEditor(size=size), show_label=False),
            orientation="vertical",
        ),
        resizable=True,
        title=title,
    )

    def _plot_default(self):
        return _create_plot_component()


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
