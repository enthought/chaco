#!/usr/bin/env python
"""
Draws a static plot of bessel functions, oriented vertically, side-by-side.

You can experiment with using different containers (uncomment lines 30-31)
or different orientations on the plots (comment out line 41 and uncomment 42).
"""

# Major library imports
from numpy import arange, fabs, pi, sin
from scipy.special import jn

# Enthought library imports
from enthought.enable2.wx_backend.api import Window
from enthought.chaco2.api import PlotComponent, OverlayPlotContainer, PlotLabel, \
                                 HPlotContainer, VPlotContainer, create_line_plot
from enthought.traits.api import false, RGBAColor

# Relative imports
from enthought.chaco2.example_support import DemoFrame, demo_main, COLOR_PALETTE


class PlotFrame(DemoFrame):
    def _create_window(self):
        numpoints = 100
        low = -5
        high = 15.0
        x = arange(low, high, (high-low)/numpoints)
        
        container = HPlotContainer(resizable = "hv", bgcolor="lightgray",
                                   fill_padding=True, padding = 10)
        # container = VPlotContainer(resizable = "hv", bgcolor="lightgray",
        #                            fill_padding=True, padding = 10)
        
        
        self.container = container
        
        # Plot some bessel functions
        value_range = None
        for i in range(10):
            y = jn(i, x)
            plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[i]), width=2.0,
                                    orientation="v")
                                   # orientation="h")
            plot.origin_axis_visible = True
            plot.index_direction = "flipped"
            plot.padding_left = 10
            plot.padding_right = 10
            plot.border_visible = True
            plot.bgcolor = "white"
            if value_range is None:
                value_range = plot.value_mapper.range
            else:
                plot.value_range = value_range
                value_range.add(plot.value)
            if i%2 == 1:
                plot.line_style = "dash"
            container.add(plot)

        container.padding_top = 50
        container.overlays.append(PlotLabel("More Bessels",
                                            component=container,
                                            font = "swiss 16",
                                            overlay_position = "top"))

        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,600), title="Vertical line plot")

# EOF
