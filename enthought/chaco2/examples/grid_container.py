#!/usr/bin/env python
"""
Draws several overlapping line plots.  

Left-drag pans the plot.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular region to
zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow and
alt-right-arrow moves you forwards and backwards through the "zoom history".

Right-click and dragging on the legend allows you to reposition the legend.

Double-clicking on line or scatter plots brings up a traits editor for the plot.
"""

# Major library imports
from numpy import arange, fabs, pi, sin
from scipy.special import jn

# Enthought library imports
from enthought.enable2.wx_backend.api import Window
from enthought.traits.api import false, RGBAColor

# Chaco imports
from enthought.chaco2.examples import DemoFrame, demo_main, COLOR_PALETTE
from enthought.chaco2.api import create_line_plot, add_default_axes, add_default_grids, \
                                 OverlayPlotContainer, PlotLabel, VPlotContainer, \
                                 create_scatter_plot, Legend, GridContainer
from enthought.chaco2.tools.api import PanTool, RectZoomTool, SimpleZoom, \
                                       LegendTool, TraitsTool



class PlotFrame(DemoFrame):
    def _create_window(self):
        container = GridContainer(padding = 20, fill_padding = True,
                                  bgcolor = "lightgray", use_backbuffer=True,
                                  shape = (2,3), spacing=(12,12))
        self.container = container
        
        # Create the initial X-series of data
        numpoints = 10
        low = -5
        high = 15.0
        x = arange(low, high+0.001, (high-low)/numpoints)
        
        # Plot some bessel functions
        value_mapper = None
        index_mapper = None
        plots = []
        for i in range(6):
            y = jn(i, x)
            plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[i]), width=2.0,
                                    bgcolor = "white", border_visible=True)
            plot.index.sort_order = "ascending"
            plot.border_width = 1
            plot.padding = 0
            add_default_grids(plot)
            add_default_axes(plot)
            plot.tools.append(PanTool(plot))
            zoom = SimpleZoom(plot, tool_mode="box", always_on=False)
            plot.overlays.append(zoom)
            container.add(plot)

        # Set the upper-left plot to only be resizable vertically, and to have
        # a fixed horizontal width
        ul_plot = container.plot_components[0]
        ul_plot.set(resizable="v", padding_top=30, width=200)
        ul_plot.overlays.append(PlotLabel("Vertically resizable", component=ul_plot))

        # Set the bottom center plot to have a fixed width and height
        cplot = container.plot_components[4]
        cplot.set(resizable="", padding_top = 30, bounds=[400,400])
        cplot.overlays.append(PlotLabel("Not resizable", component=cplot))

        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(1000,800), title="Simple line plot")

# EOF
