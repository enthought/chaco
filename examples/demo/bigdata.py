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
from scipy.special import jn
from numpy import arange

from enthought.chaco.example_support import COLOR_PALETTE
from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.traits.api import Bool, HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import OverlayPlotContainer, create_line_plot, add_default_axes, \
                                 add_default_grids
from enthought.chaco.tools.api import RangeSelection, RangeSelectionOverlay, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================

# Do the plots use downsampling?
use_downsampling = False

def _create_plot_component(use_downsampling=False):

    container = OverlayPlotContainer(padding=40, bgcolor="lightgray",
                                     use_backbuffer = True,
                                     border_visible = True,
                                     fill_padding = True)

    numpoints = 100000
    low = -5
    high = 15.0
    x = arange(low, high+0.001, (high-low)/numpoints)

    # Plot some bessel functionsless ../en
    value_mapper = None
    index_mapper = None
    for i in range(10):
        y = jn(i, x)
        plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[i]), width=2.0)
        plot.use_downsampling = use_downsampling

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
    zoom = ZoomTool(plot, tool_mode="box", always_on=False)
    plot.overlays.append(selection_overlay)
    plot.overlays.append(zoom)

    return container

#===============================================================================
# Attributes to use for the plot view.
size = (600, 500)
title = "Million Point Plot"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    # FIXME: I am putting this in here just for consistency: however the plots
    # in Chaco don't have an implementation for downsampling yet, and so, this
    # trait is not exposed in the UI.
    use_downsampling = Bool

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title
                    )

    def _plot_default(self):
        return _create_plot_component(self.use_downsampling)

    def _use_downsampling_default(self):
        return use_downsampling

demo = Demo()

#===============================================================================
# Stand-alone frame to display the plot.
#===============================================================================
class PlotFrame(DemoFrame):

    def _create_window(self):

        # Return a window containing our plots
        container=_create_plot_component(use_downsampling)
        return Window(self, -1, component=container)

if __name__ == "__main__":
    if (len(sys.argv) > 1) and (sys.argv[1] == "fast"):
        use_downsampling = True
    demo_main(PlotFrame, size=size, title=title)

#--EOF---
