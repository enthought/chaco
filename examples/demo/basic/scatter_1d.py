"""
Scatter plot with auxilliary 1d plots

Shows a scatter plot of a set of random points,
with auxilliary 1d plots of the data.

"""

# Major library imports
from numpy import sort
from numpy.random import random, randint

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some data
    numpts = 50
    x = sort(random(numpts))
    y = random(numpts)

    # Create a plot data object and give it this data
    pd = ArrayPlotData()
    pd.set_data("index", x)
    pd.set_data("value", y)

    # Create the plot
    plot = Plot(pd, use_backbuffer=True, auto_grid=False)

    plot.plot_1d(
        'index',
        type='line_scatter_1d',
        orientation='h',
        color='lightgrey',
        line_style='dot',
    )

    plot.plot_1d(
        'index',
        type='scatter_1d',
        orientation='h',
        marker='plus',
        alignment='bottom'
    )

    plot.plot_1d(
        'value',
        type='line_scatter_1d',
        orientation='v',
        color='lightgrey',
        line_style='dot',
    )

    plot.plot_1d(
        'value',
        type='scatter_1d',
        orientation='v',
        marker='plus',
        alignment='left'
    )

    plot.plot(("index", "value"),
              type="scatter",
              marker="square",
              index_sort="ascending",
              color="orange",
              marker_size=3, #randint(1,5, numpts),
              bgcolor="white",
              use_backbuffer=True)


    # Tweak some of the plot properties
    plot.title = "1D Scatter Plots"
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
title = "1D scatter plots"
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

if __name__ == "__main__":
    demo.configure_traits()

#--EOF---
