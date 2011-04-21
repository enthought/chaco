"""
Demonstrates making a scatterplot with custom markers.
Interactions are the same as in scatter.py.
"""

# Major library imports
from numpy import arange, sort
from numpy.random import random

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.enable.compiled_path import CompiledPath
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool


def make_custom_marker():
    path = CompiledPath()
    path.move_to(-5,-5)
    path.line_to(5, 5)
    path.line_to(5, -5)
    path.line_to(-5, 5)
    path.line_to(-5, -5)
    return path

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some data
    numpts = 300
    x = sort(random(numpts))
    y = random(numpts)

    # create a custom marker
    marker = make_custom_marker()

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("index", x)
    pd.set_data("value", y)

    # Create the plot
    plot = Plot(pd)
    plot.plot(("index", "value"),
              type="scatter",
              marker="custom",
              custom_symbol=marker,
              index_sort="ascending",
              color="orange",
              marker_size=3,
              bgcolor="white")

    # Tweak some of the plot properties
    plot.title = "Scatter plot with custom markers"
    plot.line_width = 0.5
    plot.padding = 50

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot, constrain_key="shift"))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    return plot

#===============================================================================
# Attributes to use for the plot view.
size = (650, 650)
title = "Scatter plot w/ custom markers"
bg_color="lightgray"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color),
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
        return Window(self, -1, component=_create_plot_component(),
                      bg_color=bg_color)

if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

#--EOF---
