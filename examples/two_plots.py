""" Demonstrates plots sharing datasources, ranges, etc. """

# Major library imports
from numpy import arange, fabs, pi, sin
from scipy.special import jn

from enthought.chaco2.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable2.api import Window
from enthought.traits.api import false

# Chaco imports
from enthought.chaco2.api import HPlotContainer, create_line_plot
from enthought.chaco2.tools.api import DataPrinter, LineInspector, PointMarker, \
                                       RangeSelection, SaveTool, SimpleZoom, PanTool


class MyFrame(DemoFrame):
    def _create_window(self):

        # Create the index
        numpoints = 100
        low = -5
        high = 15.0
        x = arange(low, high, (high-low)/numpoints)

        # Create the left plot
        y = jn(0, x)
        left_plot = create_line_plot((x,y), color="blue", width=2.0)
        left_plot.origin_axis_visible = True
        left_plot.overlays.append(LineInspector(left_plot, axis='value',
                                                write_metadata=True,
                                                is_listener=True))
        left_plot.overlays.append(LineInspector(left_plot, axis="index",
                                                write_metadata=True,
                                                is_listener=True))

        left_plot.overlays.append(SimpleZoom(left_plot, tool_mode="range"))
        left_plot.tools.append(PanTool(left_plot, drag_button="right"))

        # Create the right plot
        y = jn(1, x)
        right_plot = create_line_plot((x,y), color="red", width=2.0)

        right_plot.index = left_plot.index
        right_plot.index_mapper.range = left_plot.index_mapper.range
        right_plot.origin_axis_visible = True
        right_plot.orientation = "v"
        right_plot.origin = "top left"
        right_plot.overlays.append(LineInspector(right_plot, write_metadata=True, is_listener=True))
        right_plot.overlays.append(LineInspector(right_plot, axis="value", is_listener=True))
        right_plot.tools.append(PanTool(right_plot, drag_button="right"))

        container = HPlotContainer(spacing=20, padding=40, background="lightgray")
        container.add(left_plot)
        container.add(right_plot)

        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(MyFrame, size=(750,500), title="Two plots")

# EOF
