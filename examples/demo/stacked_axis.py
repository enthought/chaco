#!/usr/bin/env python
"""
Displays multiple data sets with different scales in the same plot area,
and shows a separate, distinct, axis for each plot.

Interactions are the same as in multiaxis.py
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

from chaco.example_support import COLOR_PALETTE
# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot, MultiAxisPlotContainer, \
                      MultiAxisPlotAxis
from chaco.tools.api import PanTool


#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some x-y data series to plot
    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(x=x)
    plot = Plot(pd,
                border_visible=True,
                padding=[50,0,50,50],
                # uncomment to test horizontal resizing of left and right axes
                #fixed_preferred_size=[300,200],
                title="Bessel Functions")
    container = MultiAxisPlotContainer(bgcolor="transparent", plot=plot)

    for i in range(5):
        color = tuple(COLOR_PALETTE[i])
        name = "jn_%d" % i
        pd.set_data(name, jn(i, x))
        renderer = plot.plot(('x', name), name=name, color=color)[0]
        
        if i==0:
            plot.value_axis.title = name
            continue
        
        axis = MultiAxisPlotAxis(orientation=("left" if i < 2 else "right"),
                                resizable="v",
                                mapper = renderer.y_mapper,
                                axis_line_color=color,
                                tick_color=color,
                                tick_label_color=color,
                                title_color=color,
                                bgcolor="transparent",
                                title=name,
                                #border_visible=True,
                                bounds=[50,100],
                                padding=0)
        container.axes.append(axis)
    
    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))

    return container

#===============================================================================
# Attributes to use for the plot view.
size=(900,500)
title="Multi-Y plot"

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
                    resizable=True, title=title,
                    width=size[0], height=size[1]
                    )

    def _plot_default(self):
        return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

#--EOF---

