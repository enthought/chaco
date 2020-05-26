#!/usr/bin/env python
"""
Draws several overlapping line plots like simple_line.py, but uses a separate
Y range for j1 compared to the other 3 curves. Also has a second Y-axis on the
right hand side for j1. Demonstrates use of the BroadcasterTool.

Interactive behavior:
* Left-drag pans the plot.
* Right-click and dragging on the legend allows you to reposition the legend.
* Double-clicking on line or scatter plots brings up a traits editor for the
  plot.
"""

# Major library imports
from numpy import arange
from scipy.special import jn

from chaco.example_support import COLOR_PALETTE
# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, VGroup, View

# Chaco imports
from chaco.api import create_line_plot, add_default_axes, \
                                add_default_grids, OverlayPlotContainer, \
                                PlotLabel, Legend, PlotAxis
from chaco.tools.api import (PanTool, LegendTool, LegendHighlighter,
                             TraitsTool, BroadcasterTool, ZoomTool)

# =============================================================================
# Create the Chaco plot.
# =============================================================================


def _create_plot_component():

    container = OverlayPlotContainer(padding=60, fill_padding=True,
                                     use_backbuffer=True, border_visible=True)

    # Create the initial X-series of data
    numpoints = 100
    low = -5
    high = 15.0
    x = arange(low, high+0.001, (high-low)/numpoints)

    # Plot some bessel functions
    plots = {}
    broadcaster = BroadcasterTool()
    for i in range(4):
        y = jn(i, x)
        plot = create_line_plot((x, y), color=tuple(COLOR_PALETTE[i]),
                                width=2.0)
        if i == 0:
            add_default_grids(plot)
            left_axis, _ = add_default_axes(plot)
            left_axis.title = "Bessel j0, j2, j3"
        elif i != 1:
            # Map correctly j2 and j3 on the first plot's axis:
            plot0 = plots["Bessel j_0"]
            plot.index_mapper = plot0.index_mapper
            plot.value_mapper = plot0.value_mapper
            plot0.value_mapper.range.add(plot.value)

        # Create a pan/zoom tool and give it a reference to the plot it should
        # manipulate, but don't attach it to the plot. Instead, attach it to
        # the broadcaster. Do it only for each independent set of axis_mappers:
        if i in [0, 1]:
            pan = PanTool(component=plot)
            broadcaster.tools.append(pan)

            zoom = ZoomTool(component=plot)
            broadcaster.tools.append(zoom)

        container.add(plot)
        plots["Bessel j_%d" % i] = plot

    # Add an axis on the right-hand side that corresponds to the second plot.
    # Note that it uses plot.value_mapper instead of plot0.value_mapper.
    plot1 = plots["Bessel j_1"]
    axis = PlotAxis(plot1, orientation="right")
    plot1.underlays.append(axis)
    axis.title = "Bessel j1"

    # Add the broadcast tool to one of the renderers: adding it to the
    # container instead breaks the box mode of the ZoomTool:
    plot0 = plots["Bessel j_0"]
    plot0.tools.append(broadcaster)

    # Create a legend, with tools to move it around and highlight renderers:
    legend = Legend(component=container, padding=10, align="ur")
    legend.tools.append(LegendTool(legend, drag_button="right"))
    legend.tools.append(LegendHighlighter(legend))
    container.overlays.append(legend)
    # Set the list of plots on the legend
    legend.plots = plots

    # Add the title at the top
    container.overlays.append(PlotLabel("Bessel functions",
                              component=container,
                              font="swiss 16",
                              overlay_position="top"))

    # Add the traits inspector tool to the container
    container.tools.append(TraitsTool(container))

    return container


# =============================================================================
# Attributes to use for the plot view.
size = (800, 700)
title = "Multi-Y plot"

# =============================================================================
# Demo class that is used by the demo.py application.
# =============================================================================


class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    VGroup(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False)),
                    resizable=True, title=title,
                    width=size[0], height=size[1])

    def _plot_default(self):
        return _create_plot_component()


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
