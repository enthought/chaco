"""Shows that adding the same plot to two different containers removes it from
one and adds it to the other.
"""

from numpy import linspace, sin

from chaco.api import ArrayPlotData, HPlotContainer, VPlotContainer, Plot
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View


class ContainerExample(HasTraits):

    plot = Instance(VPlotContainer)

    traits_view = View(
        Item("plot", editor=ComponentEditor(), show_label=False),
        resizable=True,
    )

    def __init__(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x ** 3
        plotdata = ArrayPlotData(x=x, y=y)

        # Create a scatter plot
        scatter_plot = Plot(plotdata)
        scatter_plot.plot(("x", "y"), type="scatter", color="blue")

        # Create a line plot
        line_plot1 = Plot(plotdata)
        line_plot1.plot(("x", "y"), type="line", color="blue")
        line_plot2 = Plot(plotdata)
        line_plot2.plot(("x", "y"), type="line", color="red")

        # Create a vertical container containing two horizontal containers
        h_container1 = HPlotContainer()
        h_container2 = HPlotContainer()
        outer_container = VPlotContainer(
            h_container1, h_container2, stack_order="top_to_bottom"
        )

        # Add the two plots to the first container
        h_container1.add(scatter_plot, line_plot1, line_plot2)

        # Now add the first line plot to the second container => it is removed
        # from the first, as each plot can only have one container
        h_container2.add(line_plot1)

        self.plot = outer_container


if __name__ == "__main__":
    demo = ContainerExample()
    demo.configure_traits()
