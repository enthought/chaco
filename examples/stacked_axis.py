#!/usr/bin/env python
"""
Displays multiple data sets with different scales in the same plot area,
and shows a separate, distinct, axis for each plot.

Interactions are the same as in multiaxis.py
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

from enthought.chaco.example_support import COLOR_PALETTE
from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window, Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, HPlotContainer, \
    OverlayPlotContainer, PlotAxis, PlotGrid
from enthought.chaco.tools.api import BroadcasterTool, PanTool, SimpleZoom 
from enthought.chaco.api import create_line_plot, add_default_axes, add_default_grids

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    
    # Create some x-y data series to plot
    plot_area = OverlayPlotContainer(border_visible=True)
    container = HPlotContainer(padding=50, bgcolor="transparent")
    #container.spacing = 15

    x = linspace(-2.0, 10.0, 100)
    for i in range(5):
        color = tuple(COLOR_PALETTE[i]*0.66)
        y = jn(i, x)
        renderer = create_line_plot((x, y), color=color)
        plot_area.add(renderer)
        #plot_area.padding_left = 20

        axis = PlotAxis(orientation="left", resizable="v",
                    mapper = renderer.y_mapper,
                    axis_line_color=color,
                    tick_color=color,
                    tick_label_color=color,
                    title_color=color,
                    bgcolor="transparent",
                    title = "jn_%d" % i,
                    border_visible = True,)
        axis.bounds = [60,0]
        axis.padding_left = 10
        axis.padding_right = 10

        container.add(axis)

        if i == 4:
            # Use the last plot's X mapper to create an X axis and a
            # vertical grid
            x_axis = PlotAxis(orientation="bottom", component=renderer,
                        mapper=renderer.x_mapper)
            renderer.overlays.append(x_axis)
            grid = PlotGrid(mapper=renderer.x_mapper, orientation="vertical",
                    line_color="lightgray", line_style="dot")
            renderer.underlays.append(grid)

    # Add the plot_area to the horizontal container
    container.add(plot_area)

    # Attach some tools to the plot
    broadcaster = BroadcasterTool()
    for plot in plot_area.components:
        broadcaster.tools.append(PanTool(plot))
    
    # Attach the broadcaster to one of the plots.  The choice of which
    # plot doesn't really matter, as long as one of them has a reference
    # to the tool and will hand events to it.
    plot.tools.append(broadcaster)
    
    return container

#===============================================================================
# Attributes to use for the plot view.
size=(900,500)
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

