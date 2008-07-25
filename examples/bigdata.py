"""
Demonstrates chaco performance with large datasets.

There are 10 plots with 100,000 points each.  Right-click and drag to
create a range selection region.  The region can be moved around and
resized (drag the edges).  These interactions are very fast because
of the backbuffering built into chaco.

Zooming with the mousewheel and the zoombox (as described in simple_line.py)
is also available, but panning is not.
"""

# Major library imports
import sys
from numpy import arange, fabs, pi, sin
from scipy.special import jn

from enthought.chaco.example_support import COLOR_PALETTE
from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window
from enthought.traits.api import false

# Chaco imports
from enthought.chaco.api import OverlayPlotContainer, create_line_plot, add_default_axes, \
                                 add_default_grids
from enthought.chaco.tools.api import RangeSelection, RangeSelectionOverlay, PanTool,\
                                       SimpleZoom


class PlotFrame(DemoFrame):

    def _create_window(self):
        container = OverlayPlotContainer(padding=40, bgcolor="lightgray",
                                         use_backbuffer = True,
                                         border_visible = True,
                                         fill_padding = True)

        #container.use_backbuffer = False

        self.container = container

        numpoints = 100000
        low = -5
        high = 15.0
        x = arange(low, high+0.001, (high-low)/numpoints)

        # Plot some bessel functions
        value_mapper = None
        index_mapper = None
        for i in range(10):
            y = jn(i, x)
            plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[i]), width=2.0)
            if value_mapper is None:
                index_mapper = plot.index_mapper
                value_mapper = plot.value_mapper
                add_default_grids(plot)
                add_default_axes(plot)
            else:
                plot.value_mapper = value_mapper
                value_mapper.range.add(plot.value)
                plot.index_mapper = index_mapper
                index_mapper.range.add(plot.index)
            if i%2 == 1:
                plot.line_style = "dash"
            plot.bgcolor = "white"
            container.add(plot)

        selection_overlay = RangeSelectionOverlay(component = plot)
        plot.tools.append(RangeSelection(plot))
        zoom = SimpleZoom(plot, tool_mode="box", always_on=False)
        plot.overlays.append(selection_overlay)
        plot.overlays.append(zoom)


        return Window(self, -1, component=container)

if __name__ == "__main__":
    if (len(sys.argv) > 1) and (sys.argv[1] == "fast"):
        use_downsampling = True

    demo_main(PlotFrame, size=(600,500), title="Million point plot")

# EOF
