"""
Draws a scatterplot of a set of random points of variable size.
 - This uses the non-standard renderer, VariableSizeScatterPlot
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
import numpy
import numpy.random

from enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enable.api import Component, ComponentEditor, Window
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot, VariableSizeScatterPlot, \
        LinearMapper, ArrayDataSource
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

    # Create a plot data object and give it this data
    pd = ArrayPlotData()
    pd.set_data("index", x)
    pd.set_data("value", y)

    # Because this is a non-standard renderer, we can't call plot.plot, which
    # sets up the array data sources, mappers and default index/value ranges.
    # So, its gotta be done manually for now.

    index_ds = ArrayDataSource(x)
    value_ds = ArrayDataSource(y)

    # Create the plot
    plot = Plot(pd)
    plot.index_range.add(index_ds)
    plot.value_range.add(value_ds)

    # Create the index and value mappers using the plot data ranges
    imapper = LinearMapper(range=plot.index_range)
    vmapper = LinearMapper(range=plot.value_range)

    # Create the scatter renderer
    scatter = VariableSizeScatterPlot(
                    index=index_ds,
                    value=value_ds,
                    index_mapper = imapper,
                    value_mapper = vmapper,
                    marker='circle',
                    marker_size=marker_size,
                    color=(1.0,0.0,0.75,0.4))

    # Append the renderer to the list of the plot's plots
    plot.add(scatter)
    plot.plots['var_size_scatter'] = [scatter]

    # Tweak some of the plot properties
    plot.title = "Scatter Plot"
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
title = "Basic scatter plot"
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

#===============================================================================
# Stand-alone frame to display the plot.
#===============================================================================
class PlotFrame(DemoFrame):

    def _create_window(self):
        # Return a window containing our plots
        return Window(self, -1, component=_create_plot_component(),
                      bg_color=bg_color)

if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

#--EOF---
