#!/usr/bin/env python
"""
Demo of the RangeSelection Tool on a line plot.  Left-click and drag will
create a horizontal range selection; this selection can then be dragged
around, or resized by dragging its edges.
"""

# Major library imports
from numpy import arange, fabs, pi, sin
from scipy.special import jn

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window, Component, ComponentEditor
from enthought.traits.api import HasTraits, Instance, false
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import create_line_plot, add_default_axes, add_default_grids
from enthought.chaco.tools.api import LineInspector, RangeSelection, RangeSelectionOverlay



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
