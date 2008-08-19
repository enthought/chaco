""" Demonstrates plots sharing datasources, ranges, etc. """

# Major library imports
from numpy import arange, fabs, pi, sin
from scipy.special import jn

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window
from enthought.traits.api import false

# Chaco imports
from enthought.chaco.api import HPlotContainer, ArrayPlotData, Plot
from enthought.chaco.tools.api import LineInspector, ZoomTool, PanTool


class MyFrame(DemoFrame):
    def _create_window(self):

        # Create the index
        numpoints = 100
        low = -5
        high = 15.0
        x = arange(low, high, (high-low)/numpoints)
        plotdata = ArrayPlotData(x=x, y1=jn(0,x), y2=jn(1,x))

        # Create the left plot
        left_plot = Plot(plotdata)
        left_plot.x_axis.title = "X"
        left_plot.y_axis.title = "j0(x)"
        renderer = left_plot.plot(("x", "y1"), type="line", color="blue", width=2.0)[0]
        renderer.overlays.append(LineInspector(renderer, axis='value',
                                                write_metadata=True,
                                                is_listener=True))
        renderer.overlays.append(LineInspector(renderer, axis="index",
                                                write_metadata=True,
                                                is_listener=True))
        left_plot.overlays.append(ZoomTool(left_plot, tool_mode="range"))
        left_plot.tools.append(PanTool(left_plot))

        # Create the right plot
        right_plot = Plot(plotdata)
        right_plot.index_range = left_plot.index_range
        right_plot.orientation = "v"
        right_plot.x_axis.title = "j1(x)"
        right_plot.y_axis.title = "X"
        renderer2 = right_plot.plot(("x","y2"), type="line", color="red", width=2.0)[0]
        renderer2.index = renderer.index
        renderer2.overlays.append(LineInspector(renderer2, write_metadata=True, is_listener=True))
        renderer2.overlays.append(LineInspector(renderer2, axis="value", is_listener=True))
        right_plot.overlays.append(ZoomTool(right_plot, tool_mode="range"))
        right_plot.tools.append(PanTool(right_plot))

        container = HPlotContainer(background="lightgray")
        container.add(left_plot)
        container.add(right_plot)

        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(MyFrame, size=(750,500), title="Two plots")

# EOF
