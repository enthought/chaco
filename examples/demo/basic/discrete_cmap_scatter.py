"""
Scatterplot with range-selectable data points

Draws a colormapped scatterplot of random data.

In addition to normal zooming and panning on the plot, the user can select
a range of data values by right-dragging in the color bar.

Left-click in the color bar to cancel the range selection.
"""

# Major library imports
from numpy import sort
from numpy.random import random, randint

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, VGroup, View, Label

# Chaco imports
from chaco.api import ArrayPlotData, ColorBar, \
                                 ColormappedSelectionOverlay, HPlotContainer, \
                                 LinearMapper, Plot
from chaco.default_colormaps import accent
from chaco.tools.api import PanTool, ZoomTool, RangeSelection, \
                                       RangeSelectionOverlay

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some data
    numpts = 1000
    x = sort(random(numpts))
    y = random(numpts)
    color = randint(0, 7, numpts)

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("index", x)
    pd.set_data("value", y)
    pd.set_data("color", color)

    # Create the plot
    plot = Plot(pd)
    plot.plot(("index", "value", "color"),
              type="cmap_scatter",
              name="my_plot",
              color_mapper=accent,
              marker = "square",
              fill_alpha = 0.5,
              marker_size = 6,
              outline_color = "black",
              border_visible = True,
              bgcolor = "white")

    # Tweak some of the plot properties
    plot.title = "Colormapped Scatter Plot with Range-selectable Data Points"
    plot.padding = 50
    plot.x_grid.visible = False
    plot.y_grid.visible = False
    plot.x_axis.font = "modern 16"
    plot.y_axis.font = "modern 16"

    # Right now, some of the tools are a little invasive, and we need the
    # actual ColomappedScatterPlot object to give to them
    cmap_renderer = plot.plots["my_plot"][0]

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot, constrain_key="shift"))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)
    selection = ColormappedSelectionOverlay(cmap_renderer, fade_alpha=0.35,
                                            selection_type="mask")
    cmap_renderer.overlays.append(selection)

    # Create the colorbar, handing in the appropriate range and colormap
    colorbar = create_colorbar(plot.color_mapper)
    colorbar.plot = cmap_renderer
    colorbar.padding_top = plot.padding_top
    colorbar.padding_bottom = plot.padding_bottom
    colorbar.grid_visible = False
    colorbar._axis.tick_visible = False

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
    colorbar.tools.append(RangeSelection(component=colorbar))
    colorbar.overlays.append(RangeSelectionOverlay(component=colorbar,
                                                   border_color="white",
                                                   alpha=0.8,
                                                   fill_color="lightgray"))
    return colorbar

#===============================================================================
# Attributes to use for the plot view.
size=(650,650)
title="Colormapped scatter plot"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    VGroup(
                        Label('Right-drag on colorbar to select data range'),
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        ),
                    resizable=True,
                    title=title
                    )
    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
