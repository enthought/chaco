#!/usr/bin/env python
"""
A modification of updating_plot.py to show 6 different plots whose data
are being modified.

Click and drag any of the plots to reposition them.
Right-click and drag inside the plots to pan them.
Mousewheel up and down to zoom.  Zoom box is availble (see
description in simple_line.py).
"""
# Major library imports
from numpy import arange
from scipy.special import jn

# Enthought library imports
from enable.api import Window
from enable.example_support import DemoFrame, demo_main
from traits.api import HasTraits
from pyface.timer.api import Timer

# Chaco imports
from chaco.api import create_line_plot, OverlayPlotContainer
from chaco.tools.api import MoveTool, PanTool, ZoomTool


COLOR_PALETTE = ("mediumslateblue", "maroon", "darkgreen", "goldenrod",
                 "purple", "indianred")

PLOT_SIZE = 250


class AnimatedPlot(HasTraits):

    def __init__(self, x, y, color="blue", bgcolor="white"):
        self.x_values = x[:]
        self.y_values = y[:]
        self.numpoints = len(self.x_values)

        plot = create_line_plot((self.x_values,self.y_values), color=color,
                                bgcolor=bgcolor, add_grid=True, add_axis=True)
        plot.resizable = ""
        plot.bounds = [PLOT_SIZE, PLOT_SIZE]

        plot.tools.append(PanTool(plot, drag_button="right"))
        plot.tools.append(MoveTool(plot))
        plot.overlays.append(ZoomTool(plot, tool_mode="box", always_on=False))

        plot.unified_draw = True
        self.plot = plot

        self.current_index = self.numpoints/2
        self.increment = 2

    def timer_tick(self):
        if self.current_index <= self.numpoints/3:
            self.increment = 2
        elif self.current_index == self.numpoints:
            self.increment = -2
        self.current_index += self.increment
        if self.current_index > self.numpoints:
            self.current_index = self.numpoints
        self.plot.index.set_data(self.x_values[:self.current_index])
        self.plot.value.set_data(self.y_values[:self.current_index])
        self.plot.request_redraw()


class PlotFrame(DemoFrame):

    def _create_window(self):
        numpoints = 50
        low = -5
        high = 15.0
        x = arange(low, high, (high-low)/numpoints)
        container = OverlayPlotContainer(bgcolor="lightgray")

        self.animated_plots = []
        for i, color in enumerate(COLOR_PALETTE):
            animated_plot = AnimatedPlot(x, jn(i,x), color)
            container.add(animated_plot.plot)
            self.animated_plots.append(animated_plot)

        for i, a_plot in enumerate(self.animated_plots):
            a_plot.plot.position = [50 + (i%3)*(PLOT_SIZE+50),
                                    50 + (i//3)*(PLOT_SIZE+50)]

        self.timer = Timer(100.0, self.onTimer)
        self.container = container
        return Window(self, -1, component=container)

    def onTimer(self, *args):
        for plot in self.animated_plots:
            plot.timer_tick()
        return


if __name__ == "__main__":
    # Save demo so that it doesn't get garbage collected when run within
    # existing event loop (i.e. from ipython).
    demo = demo_main(PlotFrame, size=(950, 650), title="Updating line plot")
