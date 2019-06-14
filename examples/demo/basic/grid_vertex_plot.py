#!/usr/bin/env python
"""
Draws a colormapped image plot
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
from numpy import exp, linspace, meshgrid
from numpy.random import uniform

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, jet, Plot, GridVertexPlot
from chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    # Create a non-uniformly sampled scalar field to colormap
    xs = uniform(0.0, 10.0, 10000)
    xs.sort()
    ys = uniform(0.0, 5.0, 1000)
    ys.sort()
    x, y = meshgrid(xs, ys)
    z = exp(-(x**2+y**2)/100)

    # Create a plot data object and give it this data
    pd = ArrayPlotData()
    pd.set_data("imagedata", z)

    # Create the plot
    plot = Plot(pd)
    plot.bgcolor = 'black'

    grid_plot = plot.grid_plot("imagedata",
                       type="grid_vertex",
                       xbounds=xs,
                       ybounds=ys)[0]

    # Tweak some of the plot properties
    plot.title = "Grid Vertex Plot (10 million data points)"
    plot.padding = 50

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=grid_plot, tool_mode="box", always_on=False)
    grid_plot.overlays.append(zoom)
    return plot


#===============================================================================
# Attributes to use for the plot view.
size=(800,600)
title="Basic Grid Vertex Plot"

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
