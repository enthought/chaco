#!/usr/bin/env python
"""
Draws a colormapped image plot
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
from numpy import linspace, meshgrid, pi
from scipy.special import jn

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, ColorBar, HPlotContainer, jet, \
                                 LinearMapper, Plot
from chaco.tools.api import PanTool, RangeSelection, \
                                       RangeSelectionOverlay, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    # Create a scalar field to colormap# Create a scalar field to colormap
    xbounds = (-2*pi, 2*pi, 600)
    ybounds = (-1.5*pi, 1.5*pi, 300)
    xs = linspace(*xbounds)
    ys = linspace(*ybounds)
    x, y = meshgrid(xs,ys)
    z = jn(2, x)*y*x

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("imagedata", z)

    # Create the plot
    plot = Plot(pd)
    plot.img_plot("imagedata",
                  name="my_plot",
                  xbounds=xbounds[:2],
                  ybounds=ybounds[:2],
                  colormap=jet)

    # Tweak some of the plot properties
    plot.title = "Selectable Image Plot"
    plot.padding = 50

    # Right now, some of the tools are a little invasive, and we need the
    # actual CMapImage object to give to them
    my_plot = plot.plots["my_plot"][0]

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    # Create the colorbar, handing in the appropriate range and colormap
    colormap = my_plot.color_mapper
    colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        plot=my_plot,
                        orientation='v',
                        resizable='v',
                        width=30,
                        padding=20)
    colorbar.padding_top = plot.padding_top
    colorbar.padding_bottom = plot.padding_bottom

    # create a range selection for the colorbar
    range_selection = RangeSelection(component=colorbar)
    colorbar.tools.append(range_selection)
    colorbar.overlays.append(RangeSelectionOverlay(component=colorbar,
                                                   border_color="white",
                                                   alpha=0.8,
                                                   fill_color="lightgray"))

    # we also want to the range selection to inform the cmap plot of
    # the selection, so set that up as well
    range_selection.listeners.append(my_plot)

    # Create a container to position the plot and the colorbar side-by-side
    container = HPlotContainer(use_backbuffer = True)
    container.add(plot)
    container.add(colorbar)
    container.bgcolor = "lightgray"

    #my_plot.set_value_selection((-1.3, 6.9))

    return container
#===============================================================================
# Attributes to use for the plot view.
size=(800,600)
title="Colormapped Image Plot"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title
                    )
    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

