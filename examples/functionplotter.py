#!/usr/bin/env python
"""
Demonstrates use of the FunctionDataSource that depends on an external range
and returns different data depending on that range.
"""

# Major library imports
from numpy import array, linspace, sin
from scipy.special import jn

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window
from enthought.traits.api import Callable, Instance, on_trait_change

# Chaco imports
from enthought.chaco.api import ArrayPlotData, HPlotContainer, Plot, \
        LinearMapper, ScatterPlot, DataView, LinePlot
from enthought.chaco.tools.api import PanTool, ZoomTool 
from enthought.chaco.function_data_source import FunctionDataSource

class PlotFrame(DemoFrame):

    numpoints = 500

    def xfunc(self, low, high):
        return linspace(low, high, self.numpoints)

    def yfunc(self, low, high):
        x = self.xfunc(low, high)
        #return jn(0, x)
        return sin(1.0/x)

    def _create_window(self):
        container = DataView()

        xds = FunctionDataSource(func = self.xfunc)
        yds = FunctionDataSource(func = self.yfunc)

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

        #plot = LinePlot(index = xds, value = yds, index_mapper = xmapper,
        #                value_mapper = ymapper,
        #                color = "green")
        
        container.add(plot)
        plot.tools.append(PanTool(plot, constrain_direction="x", constrain=True))
        plot.tools.append(ZoomTool(plot, axis="index", tool_mode="range"))
        return Window(self, -1, component=container)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(900,500), title="Function Plot")

