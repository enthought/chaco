#!/usr/bin/env python
"""
Draws some x-y line and scatter plots. On the left hand plot:
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

from enthought.chaco2.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable2.api import Window

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco2.tools.api import PanTool, SimpleZoom 


class PlotFrame(DemoFrame):

    def _create_window(self):

        # Create some x-y data series to plot
        x = linspace(-2.0, 10.0, 100)
        pd = ArrayPlotData(index = x)
        for i in range(5):
            pd.set_data("y" + str(i), jn(i,x))

        # Create some line plots of some of the data
        plot1 = Plot(pd)
        plot1.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="red")
        plot1.plot(("index", "y3"), name="j_3", color="blue")

        # Tweak some of the plot properties
        plot1.title = "My First Line Plot"
        plot1.padding = 50
        plot1.legend.visible = True

        # Attach some tools to the plot
        plot1.tools.append(PanTool(plot1))
        zoom = SimpleZoom(component=plot1, tool_mode="box", always_on=False)
        plot1.overlays.append(zoom)

        # Create a second scatter plot of one of the datasets, linking its 
        # range to the first plot
        plot2 = Plot(pd, range2d=plot1.range2d, padding=50)
        plot2.plot(('index', 'y3'), type="scatter", color="blue", marker="circle")

        # Create a container and add our plots
        container = HPlotContainer()
        container.add(plot1)
        container.add(plot2)

        # Return a window containing our plots
        return Window(self, -1, component=container)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(900,500), title="Basic x-y plots")

