#!/usr/bin/env python
"""
Draws a colormapped scatterplot of some random data.

Interactions on the plot are the same as simple_line, and additionally, 
pan and zoom are available on the colorbar. 

Left click will pan the colorbar's data region.  Right-click-drag will
select a zoom range.  Mousewheel up and down will zoom in and out on
the data bounds of the color bar.
"""

# Major library imports
from numpy import arange, exp, sort
from numpy.random import random

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, ColorBar, \
                                 ColormappedSelectionOverlay, HPlotContainer, \
                                 jet, LinearMapper, Plot, gist_earth
from enthought.chaco.tools.api import PanTool, ZoomTool, RangeSelection, \
                                       RangeSelectionOverlay

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    
    # Create some data
    numpts = 1000
    x = sort(random(numpts))
    y = random(numpts)
    color = exp(-(x**2 + y**2))

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("index", x)
    pd.set_data("value", y)
    pd.set_data("color", color)
    
    # Create the plot
    plot = Plot(pd)
    plot.plot(("index", "value", "color"),
              type="cmap_scatter",
              name="my_plot",
              color_mapper=gist_earth,
              marker = "square",
              fill_alpha = 0.5,
              marker_size = 8,
              outline_color = "black",
              border_visible = True,
              bgcolor = "white")
    
    # Tweak some of the plot properties
    plot.title = "Colormapped Scatter Plot with Pan/Zoom Color Bar"
    plot.padding = 50
    plot.x_grid.visible = False
    plot.y_grid.visible = False
    plot.x_axis.font = "modern 16"
    plot.y_axis.font = "modern 16"

    # Add pan and zoom to the plot
    plot.tools.append(PanTool(plot, constrain_key="shift"))
    zoom = ZoomTool(plot)
    plot.overlays.append(zoom)
    
    # Create the colorbar, handing in the appropriate range and colormap
    colorbar = ColorBar(index_mapper=LinearMapper(range=plot.color_mapper.range),
                        color_mapper=plot.color_mapper,
                        orientation='v',
                        resizable='v',
                        width=30,
                        padding=20)
    colorbar.plot = plot
    colorbar.padding_top = plot.padding_top
    colorbar.padding_bottom = plot.padding_bottom
    
    # Add pan and zoom tools to the colorbar
    colorbar.tools.append(PanTool(colorbar, constrain_direction="y", constrain=True))
    zoom_overlay = ZoomTool(colorbar, axis="index", tool_mode="range",
                            always_on=True, drag_button="right")
    colorbar.overlays.append(zoom_overlay)
    
    # Create a container to position the plot and the colorbar side-by-side
    container = HPlotContainer(plot, colorbar, use_backbuffer=True, bgcolor="lightgray")
    
    return container

#===============================================================================
# Attributes to use for the plot view.
size=(650,650)
title="Colormapped scatter plot"
        
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
