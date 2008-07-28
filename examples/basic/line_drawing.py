"""
Demonstrates using a line segment drawing tool on top of the
scatter plot from simple_scatter.py.

Pan using right-drag.
Zoom interactions are the same as in simple_line.py.

Line segment drawing:
    - left click places a new point
    - moving over an existing point and left-dragging will reposition that point
    - moving over an existing point and ctrl-left-clicking will delete that point
    - pressing "Enter" will "finalize" the selection.  This means that the
      tool's _finalize_selection() method will be called, and the list of
      drawn points will be reset.  By default, _finalize_selection() does nothing,
      but subclasses can customize this.
"""

# Major library imports
from numpy import arange, sort
from numpy.random import random

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot
from enthought.chaco.tools.api import LineSegmentTool, PanTool, ZoomTool


class MyLineDrawer(LineSegmentTool):
    """
    This class demonstrates how to customize the behavior of the
    LineSegmentTool via subclassing.
    """
    
    def _finalize_selection(self):
        print "Dataspace points:"
        for point in self.points:
            print "\t", point



class PlotFrame(DemoFrame):

    def _create_window(self):

        # Create some data
        numpts = 1000
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
                  name="my_plot",
                  marker="square",
                  index_sort="ascending",
                  color="lightblue",
                  outline_color="none",
                  marker_size=3,
                  bgcolor="white")

        # Tweak some of the plot properties
        plot.title = "Scatter Plot"
        plot.padding = 50
        plot.line_width = 1

        # Attach some tools to the plot
        pan = PanTool(plot, drag_button="right", constrain_key="shift")
        plot.tools.append(pan)
        zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)
        plot.overlays.append(MyLineDrawer(plot))

        # Return a window containing our plots
        return Window(self, -1, component=plot, bg_color="lightgray")

if __name__ == "__main__":
    demo_main(PlotFrame, size=(650,650), title="Simple scatter plot")

