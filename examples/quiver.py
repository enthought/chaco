"""
Draws a vector or "quiver" plot of a set of random points.
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
from numpy import array, hypot, sort, transpose
from numpy.random import random

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window, Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayDataSource, MultiArrayDataSource, \
        DataRange1D, LinearMapper, QuiverPlot, OverlayPlotContainer, \
        add_default_grids, add_default_axes
from enthought.chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some data
    numpts = 400
    x = sort(random(numpts))
    y = random(numpts)

    xs = ArrayDataSource(x, sort_order='ascending')
    ys = ArrayDataSource(y)

    vectorlen = 15
    vectors = array((random(numpts)*vectorlen,random(numpts)*vectorlen)).T

    vector_ds = MultiArrayDataSource(vectors)
    xrange = DataRange1D()
    xrange.add(xs)
    yrange = DataRange1D()
    yrange.add(ys)
    quiverplot = QuiverPlot(index = xs, value = ys,
                    vectors = vector_ds,
                    index_mapper = LinearMapper(range=xrange),
                    value_mapper = LinearMapper(range=yrange),
                    bgcolor = "white")

    add_default_axes(quiverplot)
    add_default_grids(quiverplot)

    # Attach some tools to the plot
    quiverplot.tools.append(PanTool(quiverplot, constrain_key="shift"))
    zoom = ZoomTool(quiverplot)
    quiverplot.overlays.append(zoom)

    container = OverlayPlotContainer(quiverplot, padding=50)

    return container

#===============================================================================
# Attributes to use for the plot view.
size=(650, 650)
title="Quiver plot"
bg_color="lightgray"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title,
                    width=size[0], height=size[1]
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
        return Window(self, -1, component=_create_plot_component(),
                      bg_color=bg_color)

if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

#--EOF---
