#!/usr/bin/env python
"""
A modification of updating_plot3.py.

Three of the plots are now oriented vertically, but the dataspace of all
6 plots is still linked.  Panning along the X axis of a vertical plot
will move the Y axis of one of the horizontally-oriented plots, and vice
versa.
"""

# Major library imports
import wx
from numpy import arange, fabs, pi, sin
from scipy.special import jn

# Enthought library imports
from enthought.enable2.api import Window
from enthought.traits.api import false, HasTraits

# Chaco imports
from enthought.chaco2.example_support import DemoFrame, demo_main
from enthought.chaco2.api import *
from enthought.chaco2.tools.api import MoveTool, PanTool, SimpleZoom


COLOR_PALETTE = ("mediumslateblue", "maroon", "darkgreen", "goldenrod",
                 "purple", "indianred")

PLOT_SIZE = 250

class AnimatedPlot(HasTraits):
    def __init__(self, x, y, color="blue", bgcolor="white", orientation="h"):
        self.y_values = y[:]
        if type(x) == ArrayDataSource:
            self.x_values = x.get_data()[:]
            plot = create_line_plot((x, self.y_values), color=color,
                                    bgcolor=bgcolor, add_grid=True, add_axis=True,
                                    orientation=orientation)
        else:
            self.x_values = x[:]
            plot = create_line_plot((self.x_values,self.y_values), color=color,
                                    bgcolor=bgcolor, add_grid=True, add_axis=True,
                                    orientation=orientation)

        plot.resizable = ""
        plot.bounds = [PLOT_SIZE, PLOT_SIZE]
        plot.unified_draw = True

        plot.tools.append(PanTool(plot, drag_button="right"))
        plot.tools.append(MoveTool(plot))
        plot.overlays.append(SimpleZoom(plot, tool_mode="box", always_on=False))

        self.plot = plot
        self.numpoints = len(self.x_values)
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

    def _create_data(self):
        values = [jn(i, x) for i in range(10)]

    def _create_window(self):
        numpoints = 50
        low = -5
        high = 15.0
        x = arange(low, high, (high-low)/numpoints)
        container = OverlayPlotContainer(bgcolor="lightgray")

        common_index = None
        index_range = None
        value_range = None
        self.animated_plots = []
        for i, color in enumerate(COLOR_PALETTE):
            if not common_index:
                animated_plot = AnimatedPlot(x, jn(i,x), color)
                plot = animated_plot.plot
                common_index = plot.index
                index_range = plot.index_mapper.range
                value_range = plot.value_mapper.range
            else:
                if i % 2 == 1:
                    orientation = "v"
                else:
                    orientation = "h"
                animated_plot = AnimatedPlot(common_index, jn(i,x), color,
                                             orientation=orientation)
                plot = animated_plot.plot
                plot.index_mapper.range = index_range
                plot.value_mapper.range = value_range

            container.add(plot)
            self.animated_plots.append(animated_plot)


        for i, a_plot in enumerate(self.animated_plots):
            a_plot.plot.position = [50 + (i%3)*(PLOT_SIZE+50), 50 + (i//3)*(PLOT_SIZE+50)]


        # Set the timer to generate events to us
        timerId = wx.NewId()
        self.timer = wx.Timer(self, timerId)
        self.Bind(wx.EVT_TIMER, self.onTimer, id=timerId)
        self.timer.Start(100.0, wx.TIMER_CONTINUOUS)

        self.container = container
        return Window(self, -1, component=container)

    def onTimer(self, event):
        for plot in self.animated_plots:
            plot.timer_tick()
        return


if __name__ == "__main__":
    demo_main(PlotFrame, size=(1000,800), title="Updating line plot")

# EOF
