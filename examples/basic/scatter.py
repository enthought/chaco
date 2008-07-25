"""
Draws a simple scatterplot of a set of random points.
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".
"""

# Major library imports
from numpy import arange, sort
from numpy.random import random

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot
from enthought.chaco.tools.api import PanTool, SimpleZoom


class PlotFrame(DemoFrame):

    def _create_window(self):

        # Create some data
        numpts = 5000
        x = sort(random(numpts))
        y = random(numpts)

        # Create a plot data obect and give it this data
        pd = ArrayPlotData()
        pd.set_data("index", x)
        pd.set_data("value", y)

        # Create the plot
        plot = Plot(pd)
        plot.plot(("index", "value"),
                  type="scatter",
                  marker="circle",
                  index_sort="ascending",
                  color="orange",
                  marker_size=3,
                  bgcolor="white")

        # Tweak some of the plot properties
        plot.title = "Scatter Plot"
        plot.line_width = 0.5
        plot.padding = 50

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot, constrain_key="shift"))
        zoom = SimpleZoom(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Return a window containing our plots
        return Window(self, -1, component=plot, bg_color="lightgray")

if __name__ == "__main__":
    demo_main(PlotFrame, size=(650,650), title="Basic scatter plot")
