#!/usr/bin/env python
"""
A modification of updating_plot4.py, except now all the plots are transparent,
and the three horizontally oriented plots have linked data views, while
the vertical plots are all independent.
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
from chaco.api import create_line_plot, OverlayPlotContainer, ArrayDataSource
from chaco.tools.api import MoveTool, PanTool, ZoomTool


COLOR_PALETTE = ("mediumslateblue", "maroon", "darkgreen", "goldenrod",
                 "purple", "indianred")

PLOT_SIZE = 250


class AnimatedPlot(HasTraits):

    def __init__(self, x, y, color="blue", bgcolor="none", orientation="h"):
        self.y_values = y[:]
        if type(x) == ArrayDataSource:
            self.x_values = x.get_data()[:]
            plot = create_line_plot((x, self.y_values), color=color,
                                    bgcolor=bgcolor, add_grid=True,
                                    add_axis=True, orientation=orientation)
        else:
            self.x_values = x[:]
            plot = create_line_plot((self.x_values,self.y_values), color=color,
                                    bgcolor=bgcolor, add_grid=True,
                                    add_axis=True, orientation=orientation)

        plot.resizable = ""
        plot.bounds = [PLOT_SIZE, PLOT_SIZE]
        plot.unified_draw = True

        plot.tools.append(PanTool(plot, drag_button="right"))
        plot.tools.append(MoveTool(plot))
        plot.overlays.append(ZoomTool(plot, tool_mode="box", always_on=False))

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
            if i == 0:
                animated_plot = AnimatedPlot(x, jn(i,x), color)
                plot = animated_plot.plot
                common_index = plot.index
                index_range = plot.index_mapper.range
                value_range = plot.value_mapper.range
            elif i % 2 == 0:
                animated_plot = AnimatedPlot(common_index, jn(i,x), color)
                plot = animated_plot.plot
                plot.index_mapper.range = index_range
                plot.value_mapper.range = value_range
            else:
                animated_plot = AnimatedPlot(x, jn(i,x), color, orientation="v")
                plot = animated_plot.plot

            container.add(plot)
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
    demo = demo_main(PlotFrame, size=(950, 650), title="Updating line plot")
