""" Tornado plot example from Brennan Williams """

# Major library imports
from numpy import linspace, pi, sin, ones

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    BarPlot,
    DataRange1D,
    LabelAxis,
    LinearMapper,
    OverlayPlotContainer,
    PlotAxis,
    cbrewer as COLOR_PALETTE,
)


class PlotExample(HasTraits):
    plot = Instance(Component)

    traits_view = View(
        Item("plot", editor=ComponentEditor(), show_label=False),
        resizable=True,
        title="Tornado Plot",
        width=800,
        height=600,
    )

    def _plot_default(self):
        container = OverlayPlotContainer(bgcolor="white")
        plots = self._make_curves()
        for plot in plots:
            plot.padding = 60
            container.add(plot)

        bottom_axis = PlotAxis(plot, orientation="bottom")

        label_list = [
            "var a",
            "var b",
            "var c",
            "var d",
            "var e",
            "var f",
            "var g",
            "var h",
            "var i",
        ]
        vertical_axis = LabelAxis(
            plot,
            orientation="left",
            title="Categories",
            positions=list(range(1, 10)),
            labels=label_list,
        )
        vertical2_axis = LabelAxis(
            plot,
            orientation="right",
            positions=list(range(1, 10)),
            labels=label_list,
        )

        plot.underlays.append(vertical_axis)
        plot.underlays.append(vertical2_axis)
        plot.underlays.append(bottom_axis)

        return container

    def _get_points(self):
        index = linspace(pi / 4, 3 * pi / 2, 9)
        data = sin(index) + 2
        return (list(range(1, 10)), data)

    def _make_curves(self):
        (index_points, value_points) = self._get_points()
        size = len(index_points)

        middle_value = 2500000.0
        mid_values = middle_value * ones(size)
        low_values = mid_values - 10000.0 * value_points
        high_values = mid_values + 20000.0 * value_points

        idx = ArrayDataSource(index_points)
        vals = ArrayDataSource(low_values, sort_order="none")

        idx2 = ArrayDataSource(index_points)
        vals2 = ArrayDataSource(high_values, sort_order="none")

        starting_vals = ArrayDataSource(mid_values, sort_order="none")

        # Create the index range
        index_range = DataRange1D(idx, low=0.5, high=9.5)
        index_mapper = LinearMapper(range=index_range)

        # Create the value range
        value_range = DataRange1D(
            vals,
            vals2,
            low_setting="auto",
            high_setting="auto",
            tight_bounds=False,
        )
        value_mapper = LinearMapper(range=value_range, tight_bounds=False)

        # Create the plot
        plot1 = BarPlot(
            index=idx,
            value=vals,
            value_mapper=value_mapper,
            index_mapper=index_mapper,
            starting_value=starting_vals,
            line_color="black",
            orientation="v",
            fill_color=tuple(COLOR_PALETTE[6]),
            bar_width=0.8,
            antialias=False,
        )

        plot2 = BarPlot(
            index=idx2,
            value=vals2,
            value_mapper=value_mapper,
            index_mapper=index_mapper,
            starting_value=starting_vals,
            line_color="black",
            orientation="v",
            fill_color=tuple(COLOR_PALETTE[1]),
            bar_width=0.8,
            antialias=False,
        )

        return [plot1, plot2]


demo = PlotExample()

if __name__ == "__main__":
    demo.configure_traits()
