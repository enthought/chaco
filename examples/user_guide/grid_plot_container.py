from numpy import linspace
from scipy.special import jn

from chaco.api import ArrayPlotData, Plot, GridPlotContainer
from chaco.example_support import COLOR_PALETTE

from enable.component_editor import ComponentEditor

from traits.api import HasTraits, Instance
from traitsui.api import Item, View


class GridContainerExample(HasTraits):

    plot = Instance(GridPlotContainer)

    traits_view = View(
        Item("plot", editor=ComponentEditor(), show_label=False),
        width=1000,
        height=600,
        resizable=True,
    )

    def _plot_default(self):
        # Create a GridContainer to hold all of our plots: 2 rows, 3 columns
        container = GridPlotContainer(
            shape=(2, 3), spacing=(10, 5), valign="top", bgcolor="lightgray"
        )

        # Create x data
        x = linspace(-5, 15.0, 100)
        pd = ArrayPlotData(index=x)

        # Plot some Bessel functions and add the plots to our container
        for i in range(6):
            data_name = "y{}".format(i)
            pd.set_data(data_name, jn(i, x))

            plot = Plot(pd)
            plot.plot(
                ("index", data_name), color=COLOR_PALETTE[i], line_width=3.0
            )

            # Set each plot's aspect based on its position in the grid
            plot.height = ((i % 3) + 1) * 50.0
            plot.resizable = "h"

            # Add to the grid container
            container.add(plot)

        return container


if __name__ == "__main__":
    demo = GridContainerExample()
    demo.configure_traits()
