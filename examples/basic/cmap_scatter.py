#!/usr/bin/env python
"""
Draws a colormapped scatterplot of some random data.

Interactions are the same as simple_line, and additionally, range selection
is available on the colorbar.  Right-click-drag will select a range of
colors on the colormap.  This range can be dragged around, and the main
plot will respond accordingly.  Left-click anywhere on the colorbar to
cancel the range selection.
"""

# Major library imports
from numpy import arange, exp, sort
from numpy.random import random

# Enthought library imports
from enthought.enable2.wx_backend.api import Window

# Chaco imports
from enthought.chaco2.example_support import DemoFrame, demo_main
from enthought.chaco2.api import ArrayPlotData, ColorBar, \
                                 ColormappedSelectionOverlay, HPlotContainer, \
                                 jet, LinearMapper, Plot
from enthought.chaco2.tools.api import PanTool, SimpleZoom, RangeSelection, \
                                       RangeSelectionOverlay



class PlotFrame(DemoFrame):
    
    def _create_window(self):

        # Create some data
        numpts = 5000
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
                  color_mapper=jet,
                  marker = "square",
                  fill_alpha = 0.5,
                  marker_size = 6,
                  outline_color = "black",
                  border_visible = True,
                  bgcolor = "white")
        
        # Tweak some of the plot properties
        plot.title = "My First Colormapped Scatter Plot"
        plot.padding = 50
        plot.x_grid.visible = False
        plot.y_grid.visible = False
        plot.x_axis.font = "modern 16"
        plot.y_axis.font = "modern 16"
        
        # Right now, some of the tools are a little invasive, and we need the 
        # actual ColomappedScatterPlot object to give to them
        my_plot = plot.plots["my_plot"][0]

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot, constrain_key="shift"))
        zoom = SimpleZoom(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)
        selection = ColormappedSelectionOverlay(my_plot, selection_type="mask")
        my_plot.overlays.append(selection)
        
        # Create the colorbar, handing in the appropriate range and colormap
        colorbar = self.create_colorbar(plot.color_mapper)
        colorbar.plot = my_plot
        colorbar.padding_top = plot.padding_top
        colorbar.padding_bottom = plot.padding_bottom
        
        # Create a container to position the plot and the colorbar side-by-side
        container = HPlotContainer(use_backbuffer = True)
        container.add(plot)
        container.add(colorbar)
        container.bgcolor = "lightgray"
        
        # Return a window containing our plot container
        return Window(self, -1, component=container)

    def create_colorbar(self, colormap):
        colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                            color_mapper=colormap,
                            orientation='v',
                            resizable='v',
                            width=30,
                            padding=20)
        colorbar.tools.append(RangeSelection(component=colorbar))
        colorbar.overlays.append(RangeSelectionOverlay(component=colorbar,
                                                       border_color="white",
                                                       alpha=0.8,
                                                       fill_color="lightgray"))
        return colorbar

if __name__ == "__main__":
    demo_main(PlotFrame, size=(650,650), title="Colormapped scatter plot")

# EOF
