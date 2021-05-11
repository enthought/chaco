"""
Simple example of a stacked bar chart
"""

# Major library imports
import numpy

# Enthought library imports
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import UItem, View

# Chaco imports
from chaco.api import LabelAxis, Plot, ArrayPlotData, ArrayDataSource


class PlotExample(HasTraits):

    plot = Instance(Plot)

    def _plot_default(self):
        index = numpy.array([1, 2, 3, 4, 5])
        series_a, series_b, series_c = (index * 10, index * 5, index * 2)
        # Stack them up
        series_c = series_c + series_b + series_a
        series_b = series_b + series_a

        plot_data = ArrayPlotData(index=index)
        plot_data.set_data("series_a", series_a)
        plot_data.set_data("series_b", series_b)
        plot_data.set_data("series_c", series_c)
        plot = Plot(plot_data)
        plot.plot(
            ("index", "series_a"), type="bar", bar_width=0.8, color="auto"
        )
        plot.plot(
            ("index", "series_b"),
            type="bar",
            bar_width=0.8,
            color="auto",
            starting_value=ArrayDataSource(series_a),
        )
        plot.plot(
            ("index", "series_c"),
            type="bar",
            bar_width=0.8,
            color="auto",
            starting_value=ArrayDataSource(series_b),
        )

        # set the plot's value range to 0, otherwise it may pad too much
        plot.value_range.low = 0

        # replace the index values with some nicer labels
        label_axis = LabelAxis(
            plot,
            orientation="bottom",
            title="Months",
            positions=list(range(1, 10)),
            labels=["jan", "feb", "march", "april", "may"],
            small_haxis_style=True,
        )

        plot.underlays.remove(plot.index_axis)
        plot.index_axis = label_axis
        plot.underlays.append(label_axis)

        return plot

    traits_view = View(
        UItem("plot", editor=ComponentEditor()),
        width=400,
        height=400,
        resizable=True,
    )


demo = PlotExample()

if __name__ == "__main__":
    demo.configure_traits()
