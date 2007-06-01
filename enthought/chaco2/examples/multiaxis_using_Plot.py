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

# Enthought library imports
from enthought.enable2.wx_backend.api import Window

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco2.examples import DemoFrame, demo_main
from enthought.chaco2.tools.api import BroadcasterTool, PanTool, SimpleZoom 


# Chaco imports
from enthought.chaco2.examples import COLOR_PALETTE
from enthought.chaco2.api import create_line_plot, add_default_axes, add_default_grids



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

        # Tweak some of the plot properties
        plot1.title = "My First Line Plot"
        plot1.padding = 50
        plot1.padding_top = 75
        plot1.legend.visible = True

        x = linspace(-5, 15.0, 100)
        y = jn(5, x)
        foreign_plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[0]), width=2.0)
        left, bottom = add_default_axes(foreign_plot)
        left.orientation = "right"
        bottom.orientation = "top"
        plot1.add(foreign_plot)

        # Attach some tools to the plot
        broadcaster = BroadcasterTool()
        broadcaster.tools.append(PanTool(plot1))
        broadcaster.tools.append(PanTool(foreign_plot))

        for c in (plot1, foreign_plot):
            zoom = SimpleZoom(component=c, tool_mode="box", always_on=False)
            broadcaster.tools.append(zoom)
        
        plot1.tools.append(broadcaster)

        # Return a window containing our plots
        return Window(self, -1, component=plot1)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(900,500), title="Basic x-y plots")

