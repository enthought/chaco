#!/usr/bin/env python
"""
Demonstrates how to limit the extent of grid lines
"""

# Major library imports
from numpy import array, linspace, zeros
from scipy.special import jn

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import UItem, View

# Chaco imports
from chaco.api import ArrayPlotData, HPlotContainer, Plot
from chaco.tools.api import PanTool, ZoomTool

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
    plot.x_grid.data_min = xmin
    plot.x_grid.data_max = xmax
    plot.x_grid.transverse_bounds = (ymin, ymax)
    plot.x_grid.transverse_mapper = plot.y_mapper

    plot.y_grid.data_min = ymin
    plot.y_grid.data_max = ymax
    plot.y_grid.transverse_bounds = (xmin, xmax)
    plot.y_grid.transverse_mapper = plot.x_mapper

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
    func_plot.x_grid.transverse_bounds = my_bounds_func
    func_plot.x_grid.transverse_mapper = func_plot.y_mapper
    func_plot.x_grid.line_color = "black"
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

    traits_view = View(UItem('plot', editor=ComponentEditor()),
                       width=size[0], height=size[1], resizable=True,
                       title=title
                       )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

