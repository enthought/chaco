#!/usr/bin/env python
"""
Draws a colormapped scatterplot of some random data.

Interactions are the same as simple_line, and additionally, range selection
is available on the colorbar.  Right-click-drag will select a range of
colors on the colormap.  This range can be dragged around, and the main
plot will respond accordingly.  Left-click anywhere on the colorbar to
cancel the range selection.
"""

# Major library imports
from numpy import exp, sort
from numpy.random import random

# VTK-related stuff
from tvtk.api import tvtk
from mayavi import mlab
from enable.vtk_backend.vtk_window import EnableVTKWindow


# Chaco imports
from chaco.api import ArrayPlotData, ColorBar, \
    ColormappedSelectionOverlay, OverlayPlotContainer, \
    jet, LinearMapper, Plot
from chaco.tools.api import PanTool, ZoomTool, RangeSelection, \
    RangeSelectionOverlay, MoveTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def create_plot():

    # Create some data
    numpts = 200
    x = sort(random(numpts))
    y = random(numpts)
    color = exp(-(x**2 + y**2))

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
              color_mapper=jet,
              marker = "square",
              fill_alpha = 0.5,
              marker_size = 6,
              outline_color = "black",
              border_visible = True,
              bgcolor = "white")

    # Tweak some of the plot properties
    plot.title = "Colormapped Scatter Plot"
    plot.padding = 50
    plot.x_grid.visible = False
    plot.y_grid.visible = False
    plot.x_axis.font = "modern 16"
    plot.y_axis.font = "modern 16"

    # Set colors
    #plot.title_color = "white"
    #for axis in plot.x_axis, plot.y_axis:
    #    axis.trait_set(title_color="white", tick_label_color="white")

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
    plot.tools.append(MoveTool(plot, drag_button="right"))
    return plot

def create_colorbar(colormap):
    colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                    color_mapper=colormap, orientation='v', resizable='',
                    height=400, width=30, padding=20)
    colorbar.tools.append(RangeSelection(component=colorbar))
    colorbar.overlays.append(RangeSelectionOverlay(component=colorbar,
           border_color="white", alpha=0.8, fill_color="lightgray"))
    colorbar.tools.append(MoveTool(colorbar, drag_button="left"))
    return colorbar

def start_vtk(component):
    f = mlab.figure(size=(700,500))
    m = mlab.test_mesh()
    scene = mlab.gcf().scene
    render_window = scene.render_window
    renderer = scene.renderer
    rwi = scene.interactor
    window = EnableVTKWindow(rwi, renderer,
            component = component,
            istyle_class = tvtk.InteractorStyleTrackballCamera,
            bgcolor = "transparent",
            event_passthrough = True,
            )
    mlab.show()

def main():
    plot = create_plot()
    plot.bounds = [400,300]
    plot.outer_position = [30,30]
    plot.resizable = ""
    cmap_renderer = plot.plots["my_plot"][0]

    # Create the colorbar, handing in the appropriate range and colormap
    colorbar = create_colorbar(plot.color_mapper)
    colorbar.outer_position = [450,30]
    colorbar.plot = cmap_renderer
    colorbar.padding_top = plot.padding_top
    colorbar.padding_bottom = plot.padding_bottom

    container = OverlayPlotContainer(bgcolor = "transparent",
                    fit_window = True)
    container.add(plot)
    container.add(colorbar)

    start_vtk(container)


if __name__ == "__main__":
    main()

