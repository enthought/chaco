#!/usr/bin/env python
"""
Draws several overlapping line plots.

Left-drag pans the plot.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
region to zoom. If you use a sequence of zoom boxes, pressing control-y and
control-z (Meta-y and Meta-z on Mac) moves you forwards and backwards
through the "zoom history".

Right-click and dragging on the legend allows you to reposition the legend.

Double-clicking on line or scatter plots brings up a traits editor for the plot.
"""

# Major library imports
from numpy import linspace
from scipy.special import jn
from time import time

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import (
    create_line_plot,
    OverlayPlotContainer,
    PlotLabel,
    cbrewer as COLOR_PALETTE,
    create_scatter_plot,
    Legend,
    PlotGrid,
)
from chaco.tools.api import PanTool, ZoomTool, LegendTool, TraitsTool

from chaco.scales.api import CalendarScaleSystem
from chaco.scales_tick_generator import ScalesTickGenerator
from chaco.axis import PlotAxis

# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================


def add_default_axes(plot, orientation="normal", vtitle="", htitle=""):
    """
    Creates left and bottom axes for a plot.  Assumes that the index is
    horizontal and value is vertical by default; set orientation to
    something other than "normal" if they are flipped.
    """
    if orientation in ("normal", "h"):
        v_mapper = plot.value_mapper
        h_mapper = plot.index_mapper
    else:
        v_mapper = plot.index_mapper
        h_mapper = plot.value_mapper

    left = PlotAxis(
        orientation="left", title=vtitle, mapper=v_mapper, component=plot
    )

    bottom = PlotAxis(
        orientation="bottom", title=htitle, mapper=h_mapper, component=plot
    )

    plot.underlays.append(left)
    plot.underlays.append(bottom)
    return left, bottom


def add_default_grids(plot, orientation="normal", tick_gen=None):
    """
    Creates horizontal and vertical gridlines for a plot.  Assumes that the
    index is horizontal and value is vertical by default; set orientation to
    something other than "normal" if they are flipped.
    """
    if orientation in ("normal", "h"):
        v_mapper = plot.index_mapper
        h_mapper = plot.value_mapper
    else:
        v_mapper = plot.value_mapper
        h_mapper = plot.index_mapper

    vgrid = PlotGrid(
        mapper=v_mapper,
        orientation="vertical",
        component=plot,
        line_color="lightgray",
        line_style="dot",
        tick_generator=tick_gen,
    )

    hgrid = PlotGrid(
        mapper=h_mapper,
        orientation="horizontal",
        component=plot,
        line_color="lightgray",
        line_style="dot",
        tick_generator=ScalesTickGenerator(),
    )

    plot.underlays.append(vgrid)
    plot.underlays.append(hgrid)
    return hgrid, vgrid


def _create_plot_component():
    container = OverlayPlotContainer(
        padding=50, fill_padding=True, bgcolor="lightgray", use_backbuffer=True
    )

    # Create the initial X-series of data
    numpoints = 100
    low = -5
    high = 15.0
    x = linspace(low, high, numpoints)

    now = time()
    timex = linspace(now, now + 7 * 24 * 3600, numpoints)

    # Plot some bessel functions
    value_mapper = None
    index_mapper = None
    plots = {}
    for i in range(10):
        y = jn(i, x)
        if i % 2 == 1:
            plot = create_line_plot(
                (timex, y), color=tuple(COLOR_PALETTE[i]), width=2.0
            )
            plot.index.sort_order = "ascending"
        else:
            plot = create_scatter_plot(
                (timex, y), color=tuple(COLOR_PALETTE[i])
            )
        plot.bgcolor = "white"
        plot.border_visible = True
        if i == 0:
            value_mapper = plot.value_mapper
            index_mapper = plot.index_mapper
            left, bottom = add_default_axes(plot)
            left.tick_generator = ScalesTickGenerator()
            bottom.tick_generator = ScalesTickGenerator(
                scale=CalendarScaleSystem()
            )
            add_default_grids(plot, tick_gen=bottom.tick_generator)
        else:
            plot.value_mapper = value_mapper
            value_mapper.range.add(plot.value)
            plot.index_mapper = index_mapper
            index_mapper.range.add(plot.index)

        if i == 0:
            plot.tools.append(PanTool(plot))
            zoom = ZoomTool(plot, tool_mode="box", always_on=False)
            plot.overlays.append(zoom)
            # Add a legend in the upper right corner, and make it relocatable
            legend = Legend(component=plot, padding=10, align="ur")
            legend.tools.append(LegendTool(legend, drag_button="right"))
            plot.overlays.append(legend)

        container.add(plot)
        plots["Bessel j_%d" % i] = plot

    # Set the list of plots on the legend
    legend.plots = plots

    # Add the title at the top
    container.overlays.append(
        PlotLabel(
            "Bessel functions",
            component=container,
            font="swiss 16",
            overlay_position="top",
        )
    )

    # Add the traits inspector tool to the container
    container.tools.append(TraitsTool(container))

    return container


# ===============================================================================
# Attributes to use for the plot view.
size = (800, 700)
title = "Simple line plot"

# ===============================================================================
# # Demo class that is used by the demo.py application.
# ===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
        Group(
            Item("plot", editor=ComponentEditor(size=size), show_label=False),
            orientation="vertical",
        ),
        resizable=True,
        title=title,
        width=size[0],
        height=size[1],
    )

    def _plot_default(self):
        return _create_plot_component()


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
