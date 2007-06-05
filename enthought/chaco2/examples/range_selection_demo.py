#!/usr/bin/env python
"""
Demo of the RangeSelection on a line plot.  Left-click and drag will
create a horizontal range selection; this selection can then be dragged
around, or resized by dragging its edges.
"""

# Major library imports
from numpy import arange, fabs, pi, sin
from scipy.special import jn

# Enthought library imports
from enthought.enable2.wx_backend.api import Window
from enthought.traits.api import false, RGBAColor

# Chaco imports
from enthought.chaco2.example_support import DemoFrame, demo_main
from enthought.chaco2.api import create_line_plot, add_default_axes, add_default_grids
from enthought.chaco2.tools.api import LineInspector, RangeSelection, RangeSelectionOverlay



class MyFrame(DemoFrame):
    def _create_window(self):
        
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
        
        return Window(self, -1, component=plot)

if __name__ == "__main__":
    demo_main(MyFrame, size=(600,500), title="Simple line plot")

# EOF
