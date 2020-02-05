#!/usr/bin/env python
"""
Draws several overlapping line plots like simple_line.py, but uses a separate
Y range for each plot.  Also has a second Y-axis on the right hand side.
Demonstrates use of the BroadcasterTool.

Left-drag pans the plot.

Right-click and dragging on the legend allows you to reposition the legend.

Double-clicking on line or scatter plots brings up a traits editor for the plot.
"""

# Major library imports
from numpy import arange
from scipy.special import jn

from chaco.example_support import COLOR_PALETTE
# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

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

    container = OverlayPlotContainer(padding=60, fill_padding = True,
                                     bgcolor="lightgray", use_backbuffer=True)

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
        plot.index.sort_order = "ascending"
        plot.bgcolor = "white"
        plot.border_visible = True
        if i == 0:
            add_default_grids(plot)
            left_axis, _ = add_default_axes(plot)
            left_axis.title = "Bessel j0, j2, j3"
        elif i != 1:
            # For the new plot to be mapped correctly on the first plot's axis:
            plot0 = plots["Bessel j_0"]
            plot.value_mapper = plot0.value_mapper
            plot0.value_mapper.range.add(plot.value)

        # Create a pan tool and give it a reference to the plot it should
        # manipulate, but don't attach it to the plot.  Instead, attach it to
        # the broadcaster.
        pan = PanTool(plot)
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

    # Add the broadcast tool to the container, instead of to an
    # individual plot
    container.tools.append(broadcaster)

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
