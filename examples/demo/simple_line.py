"""
Draws several overlapping line plots.

Left-drag pans the plot.

Right-drag (in the Y direction) zooms the plot in and out.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
and alt-right-arrow moves you forwards and backwards through the "zoom history".

Right-click and dragging on the legend allows you to reposition the legend.

Double-clicking on line or scatter plots brings up a traits editor for the plot.
"""

# Major library imports
from numpy import arange
from scipy.special import jn

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import Float, HasTraits, Int, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import create_line_plot, add_default_axes, add_default_grids, \
        OverlayPlotContainer, PlotLabel, create_scatter_plot, Legend
from chaco.tools.api import PanTool, ZoomTool, LegendTool, TraitsTool, DragZoom
from chaco.example_support import COLOR_PALETTE


class OverlappingPlotContainer(OverlayPlotContainer):
    """Simple container for creating a series of plots"""

    numpoints = Int(100)
    low = Float(-5.0)
    high = Float(15.0)
    num_funs = Int(10)

    def __init__(self, *args, **kws):
        super(OverlayPlotContainer, self).__init__(*args, **kws)
        self._setup_plots()

    def _setup_plots(self):
        """Creates series of Bessel function plots"""
        plots = {}
        x = arange(self.low, self.high + 0.001,
                   (self.high - self.low) / self.numpoints)

        for i in range(self.num_funs):
            y = jn(i, x)
            if i % 2 == 1:
                plot = create_line_plot((x, y),
                                        color=tuple(COLOR_PALETTE[i]),
                                        width=2.0)
            else:
                plot = create_scatter_plot((x, y),
                                            color=tuple(COLOR_PALETTE[i]))

            if i == 0:
                value_mapper, index_mapper, legend = \
                    self._setup_plot_tools(plot)
            else:
                self._setup_mapper(plot, value_mapper, index_mapper)

            self.add(plot)
            plots["Bessel j_%d" % i] = plot

        # Set the list of plots on the legend
        legend.plots = plots

        # Add the title at the top
        self.overlays.append(PlotLabel("Bessel functions",
                                       component=self,
                                       font="swiss 16",
                                       overlay_position="top"))

        # Add the traits inspector tool to the container
        self.tools.append(TraitsTool(self))

    def _setup_plot_tools(self, plot):
        """Sets up the background, and several tools on a plot"""
        # Make a white background with grids and axes
        plot.bgcolor = "white"
        add_default_grids(plot)
        add_default_axes(plot)

        # Allow white space around plot
        plot.index_range.tight_bounds = False
        plot.index_range.refresh()
        plot.value_range.tight_bounds = False
        plot.value_range.refresh()

        # The PanTool allows panning around the plot
        plot.tools.append(PanTool(plot))

        # The ZoomTool tool is stateful and allows drawing a zoom
        # box to select a zoom region.
        zoom = ZoomTool(plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # The DragZoom tool just zooms in and out as the user drags
        # the mouse vertically.
        dragzoom = DragZoom(plot, drag_button="right")
        plot.tools.append(dragzoom)

        # Add a legend in the upper right corner, and make it relocatable
        legend = Legend(component=plot, padding=10, align="ur")
        legend.tools.append(LegendTool(legend, drag_button="right"))
        plot.overlays.append(legend)

        return plot.value_mapper, plot.index_mapper, legend

    def _setup_mapper(self, plot, value_mapper, index_mapper):
        """Sets up a mapper for given plot"""
        plot.value_mapper = value_mapper
        value_mapper.range.add(plot.value)
        plot.index_mapper = index_mapper
        index_mapper.range.add(plot.index)


size = (800, 700)
title = "Simple Line Plot"


class PlotExample(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation="vertical"),
                    resizable=True, title=title,
                    width=size[0], height=size[1]
                    )

    def _plot_default(self):
        return OverlappingPlotContainer(padding=50, fill_padding=True,
                                     bgcolor="lightgray", use_backbuffer=True)


demo = PlotExample()


if __name__ == "__main__":
    demo.configure_traits()
