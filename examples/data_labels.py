#!/usr/bin/env python
"""
Draws a line plot with several points labelled.  Demonstrates how to annotate
plots.

Left-drag pans the plot.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular region to
zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow and
alt-right-arrow moves you forwards and backwards through the "zoom history".
"""

# Major library imports
from numpy import arange
from scipy.special import jn

from enthought.enable.example_support import DemoFrame, demo_main
from enthought.chaco.example_support import COLOR_PALETTE

# Enthought library imports
from enthought.enable.api import Window

# Chaco imports
from enthought.chaco.api import create_line_plot, add_default_axes, add_default_grids, \
                                 OverlayPlotContainer, DataLabel
from enthought.chaco.tools.api import PanTool, ZoomTool, DataLabelTool



class PlotFrame(DemoFrame):
    def _create_window(self):
        container = OverlayPlotContainer(padding = 50, fill_padding = True,
                                         bgcolor = "lightgray", use_backbuffer=True)
        self.container = container
        
        # Create the initial X-series of data
        numpoints = 100
        low = -5
        high = 15.0
        x = arange(low, high+0.001, (high-low)/numpoints)
        y = jn(0, x)
        plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[0]), width=2.0)
        plot.index.sort_order = "ascending"
        plot.bgcolor = "white"
        plot.border_visible = True
        add_default_grids(plot)
        add_default_axes(plot)

        # Add some tools
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Add a dynamic label.  This can be dragged and moved around using the
        # right mouse button.  Note the use of padding to offset the label
        # from its data point.
        label = DataLabel(component=plot, data_point=(x[40], y[40]),
                          label_position="top left", padding=40,
                          bgcolor = "lightgray",
                          border_visible=False)
        plot.overlays.append(label)
        tool = DataLabelTool(label, drag_button="right", auto_arrow_root=True)
        label.tools.append(tool)

        # Add some static labels. 
        label2 = DataLabel(component=plot, data_point=(x[20], y[20]),
                           label_position="bottom right",
                           border_visible=False,
                           bgcolor="transparent",
                           marker_color="blue",
                           marker_line_color="transparent",
                           marker = "diamond",
                           arrow_visible=False)
        plot.overlays.append(label2)

        label3 = DataLabel(component=plot, data_point=(x[80], y[80]),
                           label_position="top", padding_bottom=20,
                           marker_color="transparent",
                           marker_size=8,
                           marker="circle",
                           arrow_visible=False)
        plot.overlays.append(label3)
        
    
        container.add(plot)

        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,700), title="Data label example")

# EOF
