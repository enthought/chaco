#!/usr/bin/env python
"""
Demo of the RangeSelection Tool on a line plot.  Left-click and drag will
create a horizontal range selection; this selection can then be dragged
around, or resized by dragging its edges.
"""

# Major library imports
from numpy import arange
from scipy.special import jn

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import create_line_plot, add_default_axes, add_default_grids
from chaco.tools.api import RangeSelection, RangeSelectionOverlay



#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    numpoints = 100
    low = -5
    high = 15.001
    x = arange(low, high, (high-low)/numpoints)

    # Plot a bessel function
    y = jn(0, x)
    plot = create_line_plot((x,y), color=(0,0,1,1), width=2.0, index_sort="ascending")
    value_range = plot.value_mapper.range
    plot.active_tool = RangeSelection(plot, left_button_selects = True)
    plot.overlays.append(RangeSelectionOverlay(component=plot))
    plot.bgcolor = "white"
    plot.padding = 50
    add_default_grids(plot)
    add_default_axes(plot)

    return plot


#===============================================================================
# Attributes to use for the plot view.
size=(600,500)
title="Simple line plot"

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
