"""
Example of how to use a DataView and bare renderers to create plots
"""

from numpy import linspace, sin, cos

# Enthought library imports.
from enthought.chaco.api import DataView, ArrayDataSource, ScatterPlot, \
                                LinePlot, LinearMapper
from enthought.chaco.tools.api import PanTool, ZoomTool
from enthought.enable.example_support import DemoFrame, demo_main
from enthought.enable.api import Component, ComponentEditor, Window
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    x = linspace(-5, 10, 500)
    y = sin(x)
    y2 = 0.5 * cos(2*x)

    view = DataView(border_visible = True)
    scatter = ScatterPlot(index = ArrayDataSource(x),
                          value = ArrayDataSource(y),
                          marker = "square",
                          color = "red",
                          outline_color = "transparent",
                          index_mapper = LinearMapper(range=view.index_range),
                          value_mapper = LinearMapper(range=view.value_range))

    line = LinePlot(index = scatter.index,
                    value = ArrayDataSource(y2),
                    color = "blue",
                    index_mapper = LinearMapper(range=view.index_range),
                    value_mapper = LinearMapper(range=view.value_range))

    # Add the plot's index and value datasources to the dataview's
    # ranges so that it can auto-scale and fit appropriately
    view.index_range.sources.append(scatter.index)
    view.value_range.sources.append(scatter.value)
    view.value_range.sources.append(line.value)

    # Add the renderers to the dataview.  The z-order is determined
    # by the order in which renderers are added.
    view.add(scatter)
    view.add(line)
    view.tools.append(PanTool(view))
    view.overlays.append(ZoomTool(view))

    return view

#===============================================================================
# Attributes to use for the plot view.
size=(800,700)
title="Dataview + renderer example"

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

#===============================================================================
# Stand-alone frame to display the plot.
#===============================================================================
class PlotFrame(DemoFrame):

    def _create_window(self):
        # Return a window containing our plots
        return Window(self, -1, component=_create_plot_component())

if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

#--EOF---
