#!/usr/bin/env python
"""
Draws a random x-y lineplot and makes a tool which
shows the closet point on the lineplot to the mouse position.
"""
# Major library imports
from numpy.random import random_sample
from numpy import arange

# Enthought library imports
from enable.api import Component, ComponentEditor, BaseTool
from traits.api import HasTraits, Instance, Any, Int
from traitsui.api import View, UItem

# Chaco imports
from chaco.api import Plot, ArrayPlotData, AbstractOverlay, ArrayDataSource


# ===============================================================================
# # Create the Chaco custom tool
# ===============================================================================
class HittestTool(BaseTool, AbstractOverlay):
    """This tool uses LinePlot.hittest() to get the closest point
    on the line to the mouse position and to draw it to the screen.
    Also implements an Overlay in order to draw the point.
    """

    # A reference to the lineplot the tool acts on
    line_plot = Any()

    # Whether to draw the overlay
    visible = True

    # The point to draw on the plot, or None if no point
    pt = Any()

    # How many pixels away we may be from the line in order to do
    threshold = Int(40)

    def normal_mouse_move(self, event):
        # Compute the nearest point and draw it whenever the mouse moves
        x, y = event.x, event.y

        if self.line_plot.orientation == "h":
            x, y = self.component.map_data((x, y))
        else:
            x, y = self.component.map_data((y, x))

        x, y = self.line_plot.map_screen((x, y))
        self.pt = self.line_plot.hittest((x, y), threshold=self.threshold)
        self.request_redraw()

    def overlay(self, plot, gc, view_bounds=None, mode="normal"):
        # If we have a point, draw it to the screen as a small square
        if self.pt is not None:
            x, y = plot.map_screen(self.pt)
            gc.draw_rect((int(x) - 2, int(y) - 2, 4, 4))


# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================


def _create_plot_component():
    # make 10 random points
    x = arange(10)
    x = ArrayDataSource(x, sort_order="ascending")
    y = random_sample(10)

    # Plot the data
    pd = ArrayPlotData(x=x, y=y)

    plot = Plot(pd)
    plot.orientation = "v"
    line_plot = plot.plot(("x", "y"))[0]

    # Add the tool to the plot both as a tool and as an overlay
    tool = HittestTool(component=plot, line_plot=line_plot)
    plot.tools.append(tool)
    plot.overlays.append(tool)

    return plot


# ===============================================================================
# Attributes to use for the plot view.
# ===============================================================================
size = (800, 600)
title = "LinePlot Hittest Demo"

# ===============================================================================
# # Demo class that is used by the demo.py application.
# ===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
        UItem("plot", editor=ComponentEditor(size=size)),
        resizable=True,
        title=title,
    )

    def _plot_default(self):
        return _create_plot_component()


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
