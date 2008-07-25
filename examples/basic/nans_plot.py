#!/usr/bin/env python
"""
This plot displays chaco's ability to handle data interlaced with NaNs.
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".
"""

# Major library imports
from numpy import linspace, nan
from scipy.special import jn

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot
from enthought.chaco.tools.api import PanTool, SimpleZoom 


class PlotFrame(DemoFrame):
    def _create_window(self):
        
        # Create some x-y data series (with NaNs) to plot
        x = linspace(-5.0, 15.0, 500)
        x[75:125] = nan
        x[200:250] = nan
        x[300:330] = nan
        pd = ArrayPlotData(index = x)
        pd.set_data("value1", jn(0, x))
        pd.set_data("value2", jn(1, x))

        # Create some line and scatter plots of the data
        plot = Plot(pd)
        plot.plot(("index", "value1"), name="j_0(x)", color="red", width=2.0)
        plot.plot(("index", "value2"), type="scatter", marker_size=1,
                  name="j_1(x)", color="green")

        # Tweak some of the plot properties
        plot.title = "Plots with NaNs"
        plot.padding = 50
        plot.legend.visible = True

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot))
        zoom = SimpleZoom(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Return a window containing our plots
        return Window(self, -1, component=plot)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,700), title="Nan Test")
