#!/usr/bin/env python
"""
Similar to grid_container.py, but demonstrates Chaco's capability to used
a fixed screen space aspect ratio for plot components.
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

from enthought.chaco.example_support import COLOR_PALETTE
from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window

# Chaco imports
from enthought.chaco.api import ArrayPlotData, GridContainer, Plot, PlotLabel
from enthought.chaco.tools.api import PanTool, ZoomTool



class PlotFrame(DemoFrame):

    def _create_window(self):
            
        # Create a GridContainer to hold all of our plots
        container = GridContainer(padding=20, fill_padding=True,
                                  bgcolor="lightgray", use_backbuffer=True,
                                  shape=(3,3), spacing=(12,12))
        
        # Create the initial series of data
        x = linspace(-5, 15.0, 100)
        pd = ArrayPlotData(index = x)
        
        # Plot some bessel functions and add the plots to our container
        for i in range(9):
            pd.set_data("y" + str(i), jn(i,x))
            plot = Plot(pd)
            plot.plot(("index", "y" + str(i)), 
                      color=tuple(COLOR_PALETTE[i]), line_width=2.0,
                      bgcolor = "white", border_visible=True)

            # Tweak some of the plot properties
            plot.border_width = 1
            plot.padding = 10

            # Set each plot's aspect ratio based on its position in the
            # 3x3 grid of plots.
            n,m = divmod(i, 3)
            plot.aspect_ratio = float(n+1) / (m+1)

            # Attach some tools to the plot
            plot.tools.append(PanTool(plot))
            zoom = ZoomTool(plot, tool_mode="box", always_on=False)
            plot.overlays.append(zoom)

            # Add to the grid container
            container.add(plot)

        # Return a window containing our plots
        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(1000,800), 
            title="Grid Container with Fixed Aspect ratio")

