from numpy import linspace, sin

from chaco.api import ArrayPlotData, HPlotContainer, Plot
from enable.component_editor import ComponentEditor
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
        # Create the scatter plot
        scatter = Plot(plotdata)
        scatter.plot(("x", "y"), type="scatter", color="blue")
        # Create the line plot
        line = Plot(plotdata)
        line.plot(("x", "y"), type="line", color="blue")
        # Create a horizontal container and put the two plots inside it
        container = HPlotContainer(scatter, line)
        container.spacing = 0
        scatter.padding_right = 0
        line.padding_left = 0
        line.y_axis.orientation = "right"

        self.plot = container


# ===============================================================================
# demo object that is used by the demo.py application.
# ===============================================================================
demo = ContainerExample()
if __name__ == "__main__":
    demo.configure_traits()
