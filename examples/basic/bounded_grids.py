#!/usr/bin/env python
"""
Demonstrates how to limit the extent of grid lines
"""

# Major library imports
from numpy import array, linspace, zeros
from scipy.special import jn

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some x-y data series to plot
    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(index = x)
    for i in range(5):
        pd.set_data("y" + str(i), jn(i,x))

    # Create some line plots of some of the data
    plot = Plot(pd, title="Line Plot", padding=50, border_visible=True)
    plot.legend.visible = True
    plot.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="auto")
    plot.plot(("index", "y3"), name="j_3", color="auto")

    plot.x_grid.line_color = "black"
    plot.y_grid.line_color = "black"
    xmin, xmax = 1.0, 6.0
    ymin, ymax = 0.2, 0.80001
    plot.x_grid.set(data_min = xmin, data_max = xmax,
            transverse_bounds = (ymin, ymax),
            transverse_mapper = plot.y_mapper)

    plot.y_grid.set(data_min = ymin, data_max = ymax,
            transverse_bounds = (xmin, xmax),
            transverse_mapper = plot.x_mapper)

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    # A second plot whose vertical grid lines are clipped to the jn(3) function
    def my_bounds_func(ticks):
        """ Returns y_low and y_high for each grid tick in the array **ticks** """
        tmp = array([zeros(len(ticks)),jn(3, ticks)]).T
        return tmp

    func_plot = Plot(pd, padding=50, border_visible=True)
    func_plot.plot(("index", "y3"), color="red")
    func_plot.x_grid.set(transverse_bounds = my_bounds_func,
                    transverse_mapper = func_plot.y_mapper,
                    line_color="black")
    func_plot.tools.append(PanTool(func_plot))

    container = HPlotContainer()
    container.add(plot)
    container.add(func_plot)

    return container

#===============================================================================
# Attributes to use for the plot view.
size=(900,500)
title="Grids with bounded extents"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title
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

