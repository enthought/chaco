#!/usr/bin/env python
""" Plot backed by a pandas DataFrame. """

# Major library imports
from numpy import linspace
from pandas import DataFrame
from scipy.special import jn

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import DataFramePlotData, Plot


# ==============================================================================
# # Demo class that is used by the demo.py application.
# ==============================================================================


class Demo(HasTraits):

    plot_data = Instance(DataFramePlotData)

    plot = Instance(Component)

    traits_view = View(
        Group(
            Item(
                "plot",
                editor=ComponentEditor(size=(900, 500)),
                show_label=False,
            ),
            orientation="vertical",
        ),
        resizable=True,
        title="pandas data example",
    )

    def _plot_data_default(self):
        # Create a DataFrame with plottable data
        index = linspace(-2.0, 10.0, 100)
        df = DataFrame(index=index)
        for i in range(5):
            name = "y" + str(i)
            df[name] = jn(i, index)

        plot_data = DataFramePlotData(data_frame=df)
        return plot_data

    def _plot_default(self):
        plot = Plot(self.plot_data, padding=50)
        plot.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="red")
        plot.plot(("index", "y3"), name="j_3", color="blue")
        plot.x_axis.title = "index"
        plot.y_axis.title = "j_n"
        return plot


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
