from numpy import linspace, cos, sin

from chaco.api import ArrayPlotData, Plot
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View


class OverlappingExample(HasTraits):

    plot = Instance(Plot)

    traits_view = View(
        Item("plot", editor=ComponentEditor(), show_label=False),
        width=800,
        height=600,
        resizable=True,
        title="Chaco Plot",
    )

    def __init__(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = x / 2 * sin(x)
        y2 = cos(x)
        plotdata = ArrayPlotData(x=x, y=y, y2=y2)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a scatter plot in the Plot
        plot.plot(("x", "y"), type="scatter", color="blue")
        # Create an overlapping line plot
        plot.plot(("x", "y2"), type="line", color="red")
        self.plot = plot


# ===============================================================================
# demo object that is used by the demo.py application.
# ===============================================================================
demo = OverlappingExample()
if __name__ == "__main__":
    demo.configure_traits()
