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
from numpy import abs, cosh, exp, linspace, meshgrid, pi, tanh, nan
from numpy.random import uniform

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, viridis, Plot
from chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create a scalar field to contour
    # uses a randomly sampled, non-uniform grid
    xs = uniform(-2*pi, 2*pi, 600)
    xs.sort()
    ys = uniform(-1.5*pi, 1.5*pi, 300)
    ys.sort()
    x, y = meshgrid(xs,ys)
    z = tanh(x*y/6)*cosh(exp(-y**2)*x/3)
    z = x*y

    # mask out a region with nan values
    mask = ((abs(x-5) <= 1) & (abs(y-2) <= 2))
    z[mask] = nan

    # Create a plot data object and give it this data
    pd = ArrayPlotData()
    pd.set_data("imagedata", z)

    # Create a contour polygon plot of the data
    plot = Plot(pd, default_origin="bottom left")
    plot.contour_plot("imagedata",
                      type="poly",
                      poly_cmap=viridis,
                      xbounds=x,
                      ybounds=y)

    # Create a contour line plot for the data, too
    plot.contour_plot("imagedata",
                      type="line",
                      xbounds=x,
                      ybounds=y)

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

if __name__ == "__main__":
    demo.configure_traits()
