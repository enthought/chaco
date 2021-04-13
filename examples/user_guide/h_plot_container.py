from numpy import linspace, sin

from chaco.api import ArrayPlotData, HPlotContainer, Plot
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View


class ContainerExample(HasTraits):

    plot = Instance(HPlotContainer)

    traits_view = View(
        Item("plot", editor=ComponentEditor(), show_label=False),
        width=1000,
        height=600,
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
        line_plot = Plot(plotdata)
        line_plot.plot(("x", "y"), type="line", color="blue")

        # Create a horizontal container and put the two plots inside it
        container = HPlotContainer(line_plot, scatter_plot, spacing=100)
        self.plot = container


if __name__ == "__main__":
    demo = ContainerExample()
    demo.configure_traits()
