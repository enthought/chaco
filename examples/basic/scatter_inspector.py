#!/usr/bin/env python
"""
Example of using tooltips on Chaco plots
"""

# Major library imports
from numpy import random

from enthought.chaco.example_support import COLOR_PALETTE
from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot, ScatterInspectorOverlay
from enthought.chaco.tools.api import PanTool, ZoomTool, LegendTool, ScatterInspector


class PlotFrame(DemoFrame):

    def _create_window(self):

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


        # Return a window containing our plots
        return Window(self, -1, component=plot)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(900,500), title="Tooltip demo")

