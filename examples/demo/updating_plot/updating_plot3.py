#!/usr/bin/env python
"""
A modification of updating_plot2.py.  Now instead of each plot having its
own dataspace, the data space "views" of all six plots are linked together,
so panning and zooming in one plot will also affect all the others.
"""
# Major library imports
from numpy import arange
from scipy.special import jn

# Enthought library imports
from enable.api import Component
from enable.example_support import DemoFrame, demo_main
from traits.api import Any, Array, HasTraits, Instance, Str
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
            )
        else:
            plot = create_line_plot(
                (self.x_values, self.y_values),
                color=self.color,
                bgcolor="white",
                add_grid=True,
                add_axis=True,
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
            if not common_index:
                animated_plot = AnimatedPlot(
                    x_values=x, y_values=jn(i, x), color=color
                )
                common_index = animated_plot.plot.index
                index_range = animated_plot.plot.index_mapper.range
                value_range = animated_plot.plot.value_mapper.range
            else:
                animated_plot = AnimatedPlot(
                    x_values=common_index, y_values=jn(i, x), color=color
                )
                animated_plot.plot.index_mapper.range = index_range
                animated_plot.plot.value_mapper.range = value_range
            container.add(animated_plot.plot)
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
