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
from numpy import linspace, meshgrid, pi
from scipy.special import jn

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window

# Chaco imports
from enthought.chaco.api import ArrayPlotData, ColorBar, HPlotContainer, jet, \
                                 LinearMapper, Plot
from enthought.chaco.tools.api import PanTool, RangeSelection, \
                                       RangeSelectionOverlay, ZoomTool


class PlotFrame(DemoFrame):

    def _create_window(self):

        # Create a scalar field to colormap
        xs = linspace(-2*pi, 2*pi, 600)
        ys = linspace(-1.5*pi, 1.5*pi, 300)
        x, y = meshgrid(xs,ys)
        z = jn(2, x)*y*x

        # Create a plot data obect and give it this data
        pd = ArrayPlotData()
        pd.set_data("imagedata", z)

        # Create the plot
        plot = Plot(pd)
        plot.img_plot("imagedata", 
                      name="my_plot",
                      xbounds=xs,
                      ybounds=ys,
                      colormap=jet)

        # Tweak some of the plot properties
        plot.title = "Selectable Image Plot"
        plot.padding = 50

        # Right now, some of the tools are a little invasive, and we need the 
        # actual CMapImage object to give to them
        my_plot = plot.plots["my_plot"][0]

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Create the colorbar, handing in the appropriate range and colormap
        colormap = my_plot.color_mapper
        colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                            color_mapper=colormap,
                            plot=my_plot,
                            orientation='v',
                            resizable='v',
                            width=30,
                            padding=20)
        colorbar.padding_top = plot.padding_top
        colorbar.padding_bottom = plot.padding_bottom
        
        # create a range selection for the colorbar
        range_selection = RangeSelection(component=colorbar)
        colorbar.tools.append(range_selection)
        colorbar.overlays.append(RangeSelectionOverlay(component=colorbar,
                                                       border_color="white",
                                                       alpha=0.8,
                                                       fill_color="lightgray"))

        # we also want to the range selection to inform the cmap plot of
        # the selection, so set that up as well
        range_selection.listeners.append(my_plot)

        # Create a container to position the plot and the colorbar side-by-side
        container = HPlotContainer(use_backbuffer = True)
        container.add(plot)
        container.add(colorbar)
        container.bgcolor = "lightgray"

        #my_plot.set_value_selection((-1.3, 6.9))

        # Return a window containing our plot
        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,600), title="Colormapped Image Plot")

