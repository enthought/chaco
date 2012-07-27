"""
Example of how to use a DataView and bare renderers to create plots
"""

from numpy import linspace, sin, cos

# Enthought library imports.
from chaco.api import DataView, ArrayDataSource, ScatterPlot, \
                      LinePlot, LinearMapper
from chaco.tools.api import PanTool, ZoomTool
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import UItem, View

class PlotExample(HasTraits):
    plot = Instance(Component)

    traits_view = View(UItem('plot', editor=ComponentEditor()),
                       width=700, height=600, resizable=True,
                       title="Dataview + renderer example"
                       )

    def _plot_default(self):
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


demo = PlotExample()

if __name__ == "__main__":
    demo.configure_traits()
