"""
Plot where depth is the index such that the plot is vertical and the origin is 
the upper left
"""
import numpy
from chaco.api import ToolbarPlot, ArrayPlotData
from chaco.tools.api import LineInspector
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import UItem, View


class MyPlot(HasTraits):
    """Plot where depth is the index such that the plot is vertical
    and the origin is the upper left
    """

    plot = Instance(ToolbarPlot)

    traits_view = View(
        UItem("plot", editor=ComponentEditor()),
        width=600,
        height=600,
        resizable=True,
    )

    def _plot_default(self):
        depth = numpy.arange(1.0, 100.0, 0.1)
        data_series = numpy.sin(depth) + depth / 10.0
        plot_data = ArrayPlotData(index=depth)
        plot_data.set_data("data_series", data_series)
        plot = ToolbarPlot(plot_data, orientation="v", origin="top left")
        line = plot.plot(("index", "data_series"))[0]

        line_inspector = LineInspector(component=line, write_metadata=True)
        line.tools.append(line_inspector)
        line.overlays.append(line_inspector)

        return plot


my_plot = MyPlot()
my_plot.configure_traits()
