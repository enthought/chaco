#!/usr/bin/env python
"""
The main app for the PlotCanvas application
"""

# Major library imports
from numpy import arange, fabs, linspace, pi, sin
from scipy.special import jn


# Enthought library imports
from enthought.enable2.api import Viewport, Window
from enthought.enable2.tools.api import MoveTool, ViewportPanTool
from enthought.enable2.example_support import DemoFrame, demo_main
from enthought.traits.api import false

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco2.example_support import COLOR_PALETTE
from enthought.chaco2.tools.api import PanTool, SimpleZoom , LegendTool

# Canvas imports
from enthought.chaco2.plot_canvas import PlotCanvas

def add_basic_tools(plot):
        plot.tools.append(PanTool(plot))
        plot.tools.append(MoveTool(plot, drag_button="right"))
        zoom = SimpleZoom(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)


class PlotFrame(DemoFrame):

    def _create_window(self):
        # Create a container and add our plots
        canvas = PlotCanvas()

        # Create some x-y data series to plot
        x = linspace(-2.0, 10.0, 100)
        pd = ArrayPlotData(index = x)
        for i in range(5):
            pd.set_data("y" + str(i), jn(i,x))

        # Create some line plots of some of the data
        plot1 = Plot(pd, resizable="", bounds=[300,300],
                     position=[100, 100],
                     border_visible=True,
                     unified_draw = True)
        plot1.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="red")
        plot1.plot(("index", "y3"), name="j_3", color="blue")

        # Tweak some of the plot properties
        plot1.title = "Line Plot"
        plot1.padding = 50
        plot1.legend.visible = True
        plot1.legend.tools.append(LegendTool(plot1.legend, drag_button="right"))

        # Create a second scatter plot of one of the datasets, linking its 
        # range to the first plot
        plot2 = Plot(pd, range2d=plot1.range2d, padding=50,
                     resizable="", bounds=[300,300], position=[500,100],
                     border_visible=True,
                     unified_draw = True,
                     bgcolor = (1,1,1,0.8))
        plot2.plot(('index', 'y3'), type="scatter", color="blue", marker_size=10, marker="circle")
        
        add_basic_tools(plot1)
        canvas.add(plot1)
        add_basic_tools(plot2)       
        canvas.add(plot2)

        viewport = Viewport(component=canvas)
        viewport.tools.append(ViewportPanTool(viewport, drag_button="right"))

        # Return a window containing our plots
        return Window(self, -1, component=viewport)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(1000,700), title="PlotCanvas")

# EOF
