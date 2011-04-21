#!/usr/bin/env python
"""
Draws some x-y log plots. (No Tools)
"""

# Major library imports
from numpy import exp, linspace, sqrt
from scipy.special import gamma

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
    x = linspace(1.0, 8.0, 200)
    pd = ArrayPlotData(index = x)
    pd.set_data("y0", sqrt(x))
    pd.set_data("y1", x)
    pd.set_data("y2", x**2)
    pd.set_data("y3", exp(x))
    pd.set_data("y4", gamma(x))
    pd.set_data("y5", x**x)

    # Create some line plots of some of the data
    plot = Plot(pd)
    plot.plot(("index", "y0"), line_width=2, name="sqrt(x)", color="purple")
    plot.plot(("index", "y1"), line_width=2, name="x", color="blue")
    plot.plot(("index", "y2"), line_width=2, name="x**2", color="green")
    plot.plot(("index", "y3"), line_width=2, name="exp(x)", color="gold")
    plot.plot(("index", "y4"), line_width=2, name="gamma(x)",color="orange")
    plot.plot(("index", "y5"), line_width=2, name="x**x", color="red")

    # Set the value axis to display on a log scale
    plot.value_scale = "log"

    # Tweak some of the plot properties
    plot.title = "Log Plot"
    plot.padding = 50
    plot.legend.visible = True

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    return plot

#===============================================================================
# Attributes to use for the plot view.
size=(900,500)
title="Basic x-y log plots"

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

#--EOF---
