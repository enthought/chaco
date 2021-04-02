#!/usr/bin/env python
"""
Demonstrates use of the FunctionDataSource that depends on an external range
and returns different data depending on that range.
"""

# Major library imports
from numpy import linspace, sin, ceil

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Int, Enum
from traitsui.api import Item, Group, HGroup, View, TextEditor

# Chaco imports
from chaco.api import ScatterPlot, DataView, LinePlot
from chaco.tools.api import PanTool, ZoomTool
from chaco.function_data_source import FunctionDataSource


class PlotExample(HasTraits):
    plot = Instance(Component)
    numpoints = Int(500)

    low_mode = Enum("value", "track")
    high_mode = Enum("value", "track")

    traits_view = View(
        Group(
            Item("plot", editor=ComponentEditor(), show_label=False),
            HGroup(
                HGroup(
                    Item(
                        "object.plot.x_mapper.range.low_setting",
                        label="Low",
                        editor=TextEditor(),
                        visible_when='object.low_mode == "value" ',
                    ),
                    Item("low_mode", label="Low Mode"),
                    Item(
                        "object.plot.x_mapper.range.high_setting",
                        label="High",
                        editor=TextEditor(),
                        visible_when='object.high_mode == "value" ',
                    ),
                    Item("high_mode", label="High Mode"),
                    Item(
                        "object.plot.x_mapper.range.tracking_amount",
                        label="Tracking Amount",
                        editor=TextEditor(read_only=True),
                        visible_when='object.high_mode == "track" or '
                        'object.low_mode == "track"',
                    ),
                    label="X",
                    show_border=True,
                ),
                HGroup(
                    Item(
                        "object.plot.y_mapper.range.low_setting",
                        label="Low",
                        editor=TextEditor(),
                    ),
                    Item(
                        "object.plot.y_mapper.range.high_setting",
                        label="High",
                        editor=TextEditor(),
                    ),
                    label="Y",
                    show_border=True,
                ),
            ),
            orientation="vertical",
        ),
        resizable=True,
        title="Function Plot",
        width=900,
        height=600,
    )

    def xfunc(self, low, high):
        dx = (high - low) / self.numpoints
        real_low = ceil(low / dx) * dx
        real_high = ceil(high / dx) * dx
        return linspace(real_low, real_high, self.numpoints)

    def yfunc(self, low, high):
        x = self.xfunc(low, high)
        return sin(1.0 / x)

    def _low_mode_changed(self, newvalue):
        if newvalue != "value":
            self.plot.x_mapper.range.low_setting = newvalue

    def _high_mode_changed(self, newvalue):
        if newvalue != "value":
            self.plot.x_mapper.range.high_setting = newvalue

    def _plot_default(self):
        container = DataView()

        xds = FunctionDataSource(func=self.xfunc)
        yds = FunctionDataSource(func=self.yfunc)

        xmapper = container.x_mapper
        ymapper = container.y_mapper

        xds.data_range = xmapper.range
        yds.data_range = xmapper.range

        xmapper.range.set_bounds(-5, 10)
        ymapper.range.set_bounds(-1, 1.2)

        plot = ScatterPlot(
            index=xds,
            value=yds,
            index_mapper=xmapper,
            value_mapper=ymapper,
            color="green",
            marker="circle",
            marker_size=3,
            line_width=0,
        )

        plot2 = LinePlot(
            index=xds,
            value=yds,
            index_mapper=xmapper,
            value_mapper=ymapper,
            color="lightgray",
        )

        container.add(plot2, plot)
        plot.tools.append(
            PanTool(plot, constrain_direction="x", constrain=True)
        )
        plot.tools.append(ZoomTool(plot, axis="index", tool_mode="range"))

        return container


demo = PlotExample()

if __name__ == "__main__":
    demo.configure_traits()
