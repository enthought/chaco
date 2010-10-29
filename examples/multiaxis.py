#!/usr/bin/env python
"""
Draws several overlapping line plots like simple_line.py, but uses a separate
Y range for each plot.  Also has a second Y-axis on the right hand side.
Demonstrates use of the BroadcasterTool.

Left-drag pans the plot.

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
                                add_default_grids, OverlayPlotContainer, \
                                PlotLabel, Legend, PlotAxis
from enthought.chaco.tools.api import PanTool, LegendTool, TraitsTool, \
                                      BroadcasterTool

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
    plots = {}
    broadcaster = BroadcasterTool()
    for i in range(4):
        y = jn(i, x)
        plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[i]), width=2.0)
        plot.index.sort_order = "ascending"
        plot.bgcolor = "white"
        plot.border_visible = True
        if i == 0:
            add_default_grids(plot)
            add_default_axes(plot)

        # Create a pan tool and give it a reference to the plot it should
        # manipulate, but don't attach it to the plot.  Instead, attach it to
        # the broadcaster.
        pan = PanTool(plot)
        broadcaster.tools.append(pan)

        container.add(plot)
        plots["Bessel j_%d"%i] = plot

    # Add an axis on the right-hand side that corresponds to the second plot.
    # Note that it uses plot.value_mapper instead of plot0.value_mapper.
    plot1 = plots["Bessel j_1"]
    axis = PlotAxis(plot1, orientation="right")
    plot1.underlays.append(axis)

    # Add the broadcast tool to the container, instead of to an
    # individual plot
    container.tools.append(broadcaster)

    legend = Legend(component=container, padding=10, align="ur")
    legend.tools.append(LegendTool(legend, drag_button="right"))
    container.overlays.append(legend)

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
title="Multi-Y plot"

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

#--EOF---
