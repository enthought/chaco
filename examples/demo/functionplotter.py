#!/usr/bin/env python
"""
Demonstrates use of the FunctionDataSource that depends on an external range
and returns different data depending on that range.
"""

# Major library imports
from numpy import array, linspace, sin, ceil
from scipy.special import jn

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window, Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance, Callable, on_trait_change
from enthought.traits.ui.api import Item, Group, HGroup, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, HPlotContainer, Plot, \
        LinearMapper, ScatterPlot, DataView, LinePlot
from enthought.chaco.tools.api import PanTool, ZoomTool
from enthought.chaco.function_data_source import FunctionDataSource

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
numpoints = 500

def xfunc(low, high):
    dx = (high - low) / numpoints
    real_low = ceil(low/dx) * dx
    real_high = ceil(high/dx) * dx
    return linspace(real_low, real_high, numpoints)

def yfunc(low, high):
    x = xfunc(low, high)
    #return jn(0, x)
    return sin(1.0/x)

def _create_plot_component():

    container = DataView()

    xds = FunctionDataSource(func = xfunc)
    yds = FunctionDataSource(func = yfunc)

    xmapper = container.x_mapper
    ymapper = container.y_mapper

    xds.data_range = xmapper.range
    yds.data_range = xmapper.range

    xmapper.range.set_bounds(-5, 10)
    ymapper.range.set_bounds(-1, 1.2)

    plot = ScatterPlot(index = xds, value = yds, index_mapper = xmapper,
                       value_mapper = ymapper,
                       color = "green",
                       marker = "circle",
                       marker_size = 3,
                       line_width = 0)

    plot2 = LinePlot(index = xds, value = yds, index_mapper = xmapper,
                    value_mapper = ymapper,
                    color = "lightgray")

    container.add(plot2, plot)
    plot.tools.append(PanTool(plot, constrain_direction="x", constrain=True))
    plot.tools.append(ZoomTool(plot, axis="index", tool_mode="range"))

    return container

#===============================================================================
# Attributes to use for the plot view.
size=(900,500)
title="Function Plot"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        HGroup(
                            Item('object.plot.x_mapper.range.high_setting',
                                label='High'),
                            Item('object.plot.x_mapper.range.low_setting',
                                 label='Low'),
                                 label='X', show_border=True),
                        HGroup(
                            Item('object.plot.y_mapper.range.high_setting',
                                 label='High'),
                            Item('object.plot.y_mapper.range.low_setting',
                                 label='Low'),
                                 label='Y', show_border=True),
                        orientation = "vertical"),
                    resizable=True, title=title,
                    width=size[0], height=size[1]
                    )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

#===============================================================================
# Stand-alone frame to display the plot.
#===============================================================================
class PlotFrame(DemoFrame):

    def _create_window(self):
        # Return a window containing our plots
        return Window(self, -1, component=_create_plot_component())

if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

#--EOF---

