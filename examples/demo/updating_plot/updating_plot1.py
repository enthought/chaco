#!/usr/bin/env python
"""
Demonstrates the plot responding to data updates while remaining responsive
to user interaction.  Panning and Zooming work as described in simple_line.py

There is a timer set which modifies the data that is passed to the plot.
Since the axes and grids automatically determine their range from the
dataset, they rescale each time the data changes.  This gives the zooming
in and out behavior.  As soon as the user interacts with the plot by panning
or manually zooming, the bounds of the axes are no longer "auto", and it
becomes more apparent that the plot's data is actually changing as a
function of time.

Original inspiration for this demo from Bas van Dijk.
"""
# Major library imports
from numpy import arange
from scipy.special import jn

from enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enable.api import Window
from pyface.timer.api import Timer

# Chaco imports
from chaco.api import create_line_plot, add_default_axes, add_default_grids
from chaco.tools.api import PanTool, ZoomTool


class PlotFrame(DemoFrame):
    def _create_data(self):
        numpoints = 100
        low = -5
        high = 15.0
        x = arange(low, high, (high - low) / numpoints)
        y = jn(0, x)  # use the j0 bessel function

        self.numpoints = numpoints
        self.x_values = x
        self.y_values = y
        self.current_index = numpoints / 2
        self.increment = 2

    def _create_window(self):
        self._create_data()
        x = self.x_values[: self.current_index]
        y = self.y_values[: self.current_index]

        plot = create_line_plot((x, y), color="red", width=2.0)
        plot.padding = 50
        plot.fill_padding = True
        plot.bgcolor = "white"
        left, bottom = add_default_axes(plot)
        hgrid, vgrid = add_default_grids(plot)
        bottom.tick_interval = 2.0
        vgrid.grid_interval = 2.0

        self.plot = plot
        plot.tools.append(PanTool(component=plot))
        plot.overlays.append(
            ZoomTool(component=plot, tool_mode="box", always_on=False)
        )

        self.timer = Timer(50.0, self.onTimer)
        return Window(self, -1, component=plot)

    def onTimer(self, *args):
        # adjust the index and increment
        if self.current_index <= self.numpoints / 8:
            self.increment = 2
        elif self.current_index == self.numpoints:
            self.increment = -2

        self.current_index += self.increment
        if self.current_index > self.numpoints:
            self.current_index = self.numpoints

        self.plot.index.set_data(self.x_values[: self.current_index])
        self.plot.value.set_data(self.y_values[: self.current_index])
        self.plot.request_redraw()


if __name__ == "__main__":
    # Save demo so that it doesn't get garbage collected when run within
    # existing event loop (i.e. from ipython).
    demo = demo_main(PlotFrame, size=(600, 500), title="Simple line plot")
