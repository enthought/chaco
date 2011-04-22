#!/usr/bin/env python
"""
Example of using tooltips on Chaco plots
"""

# Major library imports
from numpy import random

from chaco.example_support import COLOR_PALETTE
from enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enable.api import Component, ComponentEditor, Window
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot, ScatterInspectorOverlay
from chaco.tools.api import PanTool, ZoomTool, LegendTool, ScatterInspector

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create a random scattering of XY pairs
    x = random.uniform(0.0, 10.0, 50)
    y = random.uniform(0.0, 5.0, 50)
    pd = ArrayPlotData(x = x, y = y)
    plot = Plot(pd, border_visible=True, overlay_border=True)

    scatter = plot.plot(("x", "y"), type="scatter", color="lightblue")[0]

    # Tweak some of the plot properties
    plot.set(title="Scatter Inspector Demo", padding=50)

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    plot.overlays.append(ZoomTool(plot))

    # Attach the inspector and its overlay
    scatter.tools.append(ScatterInspector(scatter))
    overlay = ScatterInspectorOverlay(scatter,
                    hover_color="red",
                    hover_marker_size=6,
                    selection_marker_size=6,
                    selection_color="yellow",
                    selection_outline_color="purple",
                    selection_line_width=3)
    scatter.overlays.append(overlay)

    return plot

#===============================================================================
# Attributes to use for the plot view.
size=(900,500)
title="Tooltip demo"

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

#---EOF---
