"""
Segment plot with range-selectable data points

Draws a colormapped segment plot of random data.

In addition to normal zooming and panning on the plot, the user can select
a range of data values by right-dragging in the color bar.

Left-click in the color bar to cancel the range selection.
"""

# Major library imports
from numpy import column_stack, exp, sort
from numpy.random import random, standard_normal

# Enthought library imports
from enable.api import Component, ComponentEditor, Window
from traits.api import HasTraits, Instance
from traitsui.api import Item, VGroup, View, Label

# Chaco imports
from chaco.api import ArrayPlotData, ColorBar, \
                                 ColormappedSelectionOverlay, HPlotContainer, \
                                 viridis, LinearMapper, Plot
from chaco.tools.api import PanTool, ZoomTool, RangeSelection, \
                                       RangeSelectionOverlay

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some data
    numpts = 500
    x1 = random(numpts)
    y1 = random(numpts)
    x2 = x1 + standard_normal(numpts) * 0.05
    y2 = y1 + standard_normal(numpts) * 0.05
    color = exp(-(x1**2 + y2**2))
    widths = random(numpts)

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("index", column_stack([x1, x2]).reshape(-1))
    pd.set_data("value", column_stack([y1, y2]).reshape(-1))
    pd.set_data("color", color)
    pd.set_data("widths", widths)

    # Create the plot
    plot = Plot(pd)
    plot.plot(("index", "value", "color", "widths"),
              type="cmap_segment",
              name="my_plot",
              color_mapper=viridis,
              border_visible=True,
              bgcolor="white",
              size_min=0.5,
              size_max=5.0)

    # Tweak some of the plot properties
    plot.title = "Colormapped Segment Plot with variable widths"
    plot.padding = 50
    plot.x_grid.visible = False
    plot.y_grid.visible = False
    plot.x_axis.font = "modern 16"
    plot.y_axis.font = "modern 16"

    # Right now, some of the tools are a little invasive, and we need the
    # actual ColomappedSegmentPlot object to give to them
    cmap_renderer = plot.plots["my_plot"][0]

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot, constrain_key="shift"))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    # Create the colorbar, handing in the appropriate range and colormap
    colorbar = ColorBar(index_mapper=LinearMapper(range=plot.color_mapper.range),
                        color_mapper=plot.color_mapper,
                        orientation='v',
                        resizable='v',
                        width=30,
                        padding=20)
    colorbar.plot = cmap_renderer
    colorbar.padding_top = plot.padding_top
    colorbar.padding_bottom = plot.padding_bottom

    # Create a container to position the plot and the colorbar side-by-side
    container = HPlotContainer(use_backbuffer = True)
    container.add(plot)
    container.add(colorbar)
    container.bgcolor = "lightgray"
    return container

def create_colorbar(colormap):
    colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        orientation='v',
                        resizable='v',
                        width=30,
                        padding=20)
    return colorbar

#===============================================================================
# Attributes to use for the plot view.
size=(650,650)
title="Colormapped segment plot"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Item('plot', editor=ComponentEditor(size=size),
                            show_label=False),
                    resizable=True,
                    title=title
                    )
    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
