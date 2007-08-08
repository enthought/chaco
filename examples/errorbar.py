#!/usr/bin/env python
"""
Demonstrates error bar plots in Chaco.

Left-drag pans the plot.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular region to
zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow and
alt-right-arrow moves you forwards and backwards through the "zoom history".

Right-click and dragging on the legend allows you to reposition the legend.

Double-clicking on line or scatter plots brings up a traits editor for the plot.
"""

# Major library imports
from numpy import arange, fabs, pi, sin, ones
import numpy as np
from scipy.special import jn

# Enthought library imports
from enthought.enable2.wx_backend.api import Window
from enthought.traits.api import false

# Chaco imports
from enthought.chaco2.example_support import DemoFrame, demo_main, COLOR_PALETTE
from enthought.chaco2.api import (add_default_axes, add_default_grids, 
                                 OverlayPlotContainer, ErrorBarPlot, ArrayDataSource, 
                                 DataRange1D, LinearMapper, ScatterPlot )
from enthought.chaco2.tools.api import PanTool, SimpleZoom, TraitsTool

# Pearson's Data
# K. Pearson, Philosophical Magazine, 2, 559 (1901)
dx = np.array([.03,.03,.04,.035,.07,.11,.13,.22,.74,1.])
dy = np.array([1.,.74,.5,.35,.22,.22,.12,.12,.1,.04])

x = np.array([0.,.9,1.8,2.6,3.3,4.4,5.2,6.1,6.5,7.4])
xlow = ArrayDataSource(x - dx)
xhigh = ArrayDataSource(x + dx)
x = ArrayDataSource(x, sort_order="ascending")

y = np.array([5.9,5.4,4.4,4.6,3.5,3.7,2.8,2.8,2.4,1.5])
ylow = ArrayDataSource(y - dy)
yhigh = ArrayDataSource(y + dy)
y = ArrayDataSource(y)


class PlotFrame(DemoFrame):
    def _create_window(self):
        container = OverlayPlotContainer(padding = 50, fill_padding = True,
                                         bgcolor = "lightgray", use_backbuffer=True)
        self.container = container

        index_range = DataRange1D(x)
        index_mapper = LinearMapper(range=index_range)
        value_range = DataRange1D(ylow, yhigh)
        value_mapper = LinearMapper(range=value_range)

        # Create a plot of the vertical error
        plot1 = ErrorBarPlot(index=x, index_mapper=index_mapper,
                    value_low = ylow,
                    value_high = yhigh,
                    value_mapper = value_mapper,
                    bgcolor = "white",
                    border_visible = True)
        add_default_axes(plot1)
        add_default_grids(plot1)

        # Create a plot of the horizontal error.  Note that we add the xlow and
        # xhigh datasources to the index_range so that it will auto-fit the range
        # around the errorbars (and not just the central datapoints).
        index_range.add(xlow, xhigh)
        plot2 = ErrorBarPlot(index=y, index_mapper=LinearMapper(range=value_range),
                    value_low = xlow,
                    value_high = xhigh,
                    value_mapper = LinearMapper(range=index_range),
                    color = "blue",
                    orientation = "v")

        # Create a scatterplot for the data markers.
        value_range.add(y)
        scatter = ScatterPlot(index=x, index_mapper=LinearMapper(range=index_range),
                    value=y, value_mapper=LinearMapper(range=value_range),
                    color="red")

        plot1.tools.append(PanTool(plot1))
        zoom = SimpleZoom(plot1, tool_mode="box", always_on=False)
        plot1.overlays.append(zoom)

        # Add the plots to the container.  Note that the order matters: by adding
        # the scatterplot last, the marker will be drawn over the errorbars.  You
        # can change this order around or change the alpha value in the scatter
        # plot's marker_color to have different levels of marker visibility.
        container.add(plot1, plot2, scatter)

        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,700), title="Error bar plot")

# EOF
