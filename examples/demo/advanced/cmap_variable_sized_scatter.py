"""
Draws a scatterplot of a set of random points of variable size and color.
 - This uses the non-standard renderer, VariableSizeScatterPlot
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing control-y and
   control-z  (Meta-y and Meta-z on Mac) moves you forwards and backwards
   through the "zoom history".
"""

# Major library imports
import numpy

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot, ColormappedScatterPlot, \
        LinearMapper, ArrayDataSource, viridis, DataRange1D
from chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some data
    numpts = 1000
    x = numpy.arange(0, numpts)
    y = numpy.random.random(numpts)
    marker_size = numpy.random.normal(4.0, 4.0, numpts)
    color = numpy.random.random(numpts)

    # Create a plot data object and give it this data
    pd = ArrayPlotData()
    pd.set_data("index", x)
    pd.set_data("value", y)

    # Because this is a non-standard renderer, we can't call plot.plot, which
    # sets up the array data sources, mappers and default index/value ranges.
    # So, its gotta be done manually for now.

    index_ds = ArrayDataSource(x)
    value_ds = ArrayDataSource(y)
    color_ds = ArrayDataSource(color)

    # Create the plot
    plot = Plot(pd)
    plot.index_range.add(index_ds)
    plot.value_range.add(value_ds)

    # Create the index and value mappers using the plot data ranges
    imapper = LinearMapper(range=plot.index_range)
    vmapper = LinearMapper(range=plot.value_range)

    # Create the scatter renderer
    scatter = ColormappedScatterPlot(
                    index=index_ds,
                    value=value_ds,
                    color_data=color_ds,
                    color_mapper=viridis(range=DataRange1D(low=0.0, high=1.0)),
                    fill_alpha=0.4,
                    index_mapper = imapper,
                    value_mapper = vmapper,
                    marker='circle',
                    marker_size=marker_size)

    # Append the renderer to the list of the plot's plots
    plot.add(scatter)
    plot.plots['var_size_scatter'] = [scatter]

    # Tweak some of the plot properties
    plot.title = "Variable Size and Color Scatter Plot"
    plot.line_width = 0.5
    plot.padding = 50

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot, constrain_key="shift"))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    return plot

#===============================================================================
# Attributes to use for the plot view.
size = (650, 650)
title = "Variable size and color scatter plot"
bg_color="lightgray"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size,
                                                            bgcolor=bg_color),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title
                    )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

#--EOF---
