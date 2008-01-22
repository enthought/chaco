#!/usr/bin/env python
"""
Demonstrates the different 'hold' styles of LinePlot
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

def attach_tools(plot):
    plot.tools.append(PanTool(plot))
    zoom = SimpleZoom(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

class PlotFrame(DemoFrame):

    def _create_window(self):

        # Create some x-y data series to plot
        x = linspace(-2.0, 10.0, 40)
        pd = ArrayPlotData(index = x, y0=jn(0,x))

        # Create some line plots of some of the data
        plot1 = Plot(pd)
        lineplot = plot1.plot(("index", "y0"), name="j_0", color="red", render_style="hold")

        # Tweak some of the plot properties
        plot1.title = "render_style = hold"
        plot1.padding = 50
        plot1.legend.visible = True

        # Attach some tools to the plot
        attach_tools(plot1)

        # Create a second scatter plot of one of the datasets, linking its 
        # range to the first plot
        plot2 = Plot(pd, range2d=plot1.range2d, padding=50)
        plot2.plot(('index', 'y0'), color="blue", render_style="connectedhold")
        plot2.title = "render_style = connectedhold"
        attach_tools(plot2)

        # Create a container and add our plots
        container = HPlotContainer()
        container.add(plot1)
        container.add(plot2)

        # Return a window containing our plots
        return Window(self, -1, component=container)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(900,500), title="Line plots with hold")

