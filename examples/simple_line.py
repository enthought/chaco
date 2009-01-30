#!/usr/bin/env python
"""
Draws several overlapping line plots.

Left-drag pans the plot.

Right-drag (in the Y direction) zooms the plot in and out.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular region to
zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow and
alt-right-arrow moves you forwards and backwards through the "zoom history".

Right-click and dragging on the legend allows you to reposition the legend.

Double-clicking on line or scatter plots brings up a traits editor for the plot.
"""

# Major library imports
from numpy import arange
from scipy.special import jn

from enthought.chaco.example_support import COLOR_PALETTE
from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window, Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import create_line_plot, add_default_axes, \
        add_default_grids, OverlayPlotContainer, PlotLabel, \
        create_scatter_plot, Legend
from enthought.chaco.tools.api import PanTool, ZoomTool, LegendTool, \
        TraitsTool, DragZoom

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    container = OverlayPlotContainer(padding = 50, fill_padding = True,
                                     bgcolor = "lightgray", use_backbuffer=True)

    # Create the initial X-series of data
    numpoints = 100
    low = -5
    high = 15.0
    x = arange(low, high+0.001, (high-low)/numpoints)

    # Plot some bessel functions
    value_mapper = None
    index_mapper = None
    plots = {}
    for i in range(10):
        y = jn(i, x)
        if i%2 == 1:
            plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[i]), width=2.0)
            plot.index.sort_order = "ascending"
        else:
            plot = create_scatter_plot((x,y), color=tuple(COLOR_PALETTE[i]))

        plot.bgcolor = "white"
        plot.border_visible = True
        if i == 0:
            value_mapper = plot.value_mapper
            index_mapper = plot.index_mapper
            add_default_grids(plot)
            add_default_axes(plot)
            plot.index_range.tight_bounds = False
            plot.index_range.refresh()
            plot.value_range.tight_bounds = False
            plot.value_range.refresh()
        else:
            plot.value_mapper = value_mapper
            value_mapper.range.add(plot.value)
            plot.index_mapper = index_mapper
            index_mapper.range.add(plot.index)

        if i==0:
            plot.tools.append(PanTool(plot))
            
            # The ZoomTool tool is stateful and allows drawing a zoom
            # box to select a zoom region.
            zoom = ZoomTool(plot, tool_mode="box", always_on=False)
            plot.overlays.append(zoom)

            # The DragZoom tool just zooms in and out as the user drags
            # the mouse vertically.
            dragzoom = DragZoom(plot, drag_button="right")
            plot.tools.append(dragzoom)

            # Add a legend in the upper right corner, and make it relocatable
            legend = Legend(component=plot, padding=10, align="ur")
            legend.tools.append(LegendTool(legend, drag_button="right"))
            plot.overlays.append(legend)

        container.add(plot)
        plots["Bessel j_%d"%i] = plot

    # Set the list of plots on the legend
    legend.plots = plots

    # Add the title at the top
    container.overlays.append(PlotLabel("Bessel functions",
                              component=container,
                              font = "swiss 16",
                              overlay_position="top"))

    # Add the traits inspector tool to the container
    container.tools.append(TraitsTool(container))
    
    return container

#===============================================================================
# Attributes to use for the plot view.
size=(800,700)
title="Simple Line Plot"

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
        return Window(self, -1, component=_create_plot_component())
    
if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

# EOF
