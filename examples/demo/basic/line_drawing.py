"""
Line drawing tool

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
from numpy import sort
from numpy.random import random

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import LineSegmentTool, PanTool, ZoomTool


class MyLineDrawer(LineSegmentTool):
    """
    This class demonstrates how to customize the behavior of the
    LineSegmentTool via subclassing.
    """

    def _finalize_selection(self):
        print("Dataspace points:")
        for point in self.points:
            print("\t", point)


# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================
def _create_plot_component():

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
    plot.plot(
        ("index", "value"),
        type="scatter",
        name="my_plot",
        marker="square",
        index_sort="ascending",
        color="lightblue",
        outline_color="none",
        marker_size=3,
        bgcolor="white",
    )

    # Tweak some of the plot properties
    plot.title = "Click to add points, press Enter to finalize selection"
    plot.padding = 50
    plot.line_width = 1

    # Attach some tools to the plot
    pan = PanTool(plot, drag_button="right", constrain_key="shift")
    plot.tools.append(pan)
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)
    plot.overlays.append(MyLineDrawer(plot))
    return plot


# ===============================================================================
# Attributes to use for the plot view.
size = (650, 650)
title = "Line drawing example"
bgcolor = "lightgray"

# ===============================================================================
# # Demo class that is used by the demo.py application.
# ===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
        Group(
            Item(
                "plot",
                editor=ComponentEditor(size=size, bgcolor=bgcolor),
                show_label=False,
            ),
            orientation="vertical",
        ),
        resizable=True,
        title=title,
    )

    def _plot_default(self):
        return _create_plot_component()


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
