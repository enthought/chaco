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
from enable.api import Component
from enable.example_support import DemoFrame, demo_main
from traits.api import Any, Array, Enum, HasTraits, Instance, Str
from pyface.timer.api import Timer

# Chaco imports
from chaco.api import create_line_plot, OverlayPlotContainer, ArrayDataSource
from chaco.tools.api import MoveTool, PanTool, ZoomTool


COLOR_PALETTE = (
    "mediumslateblue",
    "maroon",
    "darkgreen",
    "goldenrod",
    "purple",
    "indianred",
)

PLOT_SIZE = 250


class AnimatedPlot(HasTraits):
    x_values = Any()  # Array or ArraryDataSource
    y_values = Array()
    color = Str()
    orientation = Enum("h", "v")

    plot = Instance(Component)

    def _plot_default(self):
        if type(self.x_values) == ArrayDataSource:
            self.x_values = self.x_values.get_data()[:]
            plot = create_line_plot(
                (self.x_values, self.y_values),
                color=self.color,
                bgcolor="white",
                add_grid=True,
                add_axis=True,
                orientation=self.orientation,
            )
        else:
            plot = create_line_plot(
                (self.x_values, self.y_values),
                color=self.color,
                bgcolor="white",
                add_grid=True,
                add_axis=True,
                orientation=self.orientation,
            )

        plot.resizable = ""
        plot.bounds = [PLOT_SIZE, PLOT_SIZE]
        plot.unified_draw = True

        plot.tools.append(PanTool(plot, drag_button="right"))
        plot.tools.append(MoveTool(plot))
        plot.overlays.append(ZoomTool(plot, tool_mode="box", always_on=False))

        self.numpoints = len(self.x_values)
        self.current_index = self.numpoints // 2
        self.increment = 2

        return plot

    def timer_tick(self):
        if self.current_index <= self.numpoints / 3:
            self.increment = 2
        elif self.current_index == self.numpoints:
            self.increment = -2
        self.current_index += self.increment
        if self.current_index > self.numpoints:
            self.current_index = self.numpoints
        self.plot.index.set_data(self.x_values[: self.current_index])
        self.plot.value.set_data(self.y_values[: self.current_index])
        self.plot.request_redraw()


class PlotFrame(DemoFrame):
    def _create_component(self):
        numpoints = 50
        low = -5
        high = 15.0
        x = arange(low, high, (high - low) / numpoints)
        container = OverlayPlotContainer(bgcolor="lightgray")

        common_index = None
        index_range = None
        value_range = None
        self.animated_plots = []
        for i, color in enumerate(COLOR_PALETTE):
            if i == 0:
                animated_plot = AnimatedPlot(
                    x_values=x, y_values=jn(i, x), color=color
                )
                plot = animated_plot.plot
                common_index = plot.index
                index_range = plot.index_mapper.range
                value_range = plot.value_mapper.range
            elif i % 2 == 0:
                animated_plot = AnimatedPlot(
                    x_values=common_index, y_values=jn(i, x), color=color
                )
                plot = animated_plot.plot
                plot.index_mapper.range = index_range
                plot.value_mapper.range = value_range
            else:
                animated_plot = AnimatedPlot(
                    x_values=x, y_values=jn(i, x), color=color, orientation="v"
                )
                plot = animated_plot.plot

            container.add(plot)
            self.animated_plots.append(animated_plot)

        for i, a_plot in enumerate(self.animated_plots):
            a_plot.plot.position = [
                50 + (i % 3) * (PLOT_SIZE + 50),
                50 + (i // 3) * (PLOT_SIZE + 50),
            ]

        self.timer = Timer(100.0, self.onTimer)
        self.container = container
        return container

    def onTimer(self, *args):
        for plot in self.animated_plots:
            plot.timer_tick()


if __name__ == "__main__":
    # Save demo so that it doesn't get garbage collected when run within
    # existing event loop (i.e. from ipython).
    demo = demo_main(PlotFrame, size=(950, 650), title="Updating line plot")
