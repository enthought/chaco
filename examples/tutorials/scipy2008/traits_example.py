from numpy import linspace, sin

from enable.api import ColorTrait
from chaco.api import ArrayPlotData, Plot, marker_trait
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance, Int
from traitsui.api import Group, Item, View


class ScatterPlotTraits(HasTraits):

    plot = Instance(Plot)
    color = ColorTrait("blue")
    marker = marker_trait
    marker_size = Int(4)

    traits_view = View(
        Group(
            Item("color", label="Color", style="custom"),
            Item("marker", label="Marker"),
            Item("marker_size", label="Size"),
            Item("plot", editor=ComponentEditor(), show_label=False),
            orientation="vertical",
        ),
        width=800,
        height=600,
        resizable=True,
        title="Chaco Plot",
    )

    def __init__(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x ** 3
        plotdata = ArrayPlotData(x=x, y=y)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a line plot in the Plot
        self.renderer = plot.plot(("x", "y"), type="scatter", color="blue")[0]
        self.plot = plot

    def _color_changed(self):
        self.renderer.color = self.color

    def _marker_changed(self):
        self.renderer.marker = self.marker

    def _marker_size_changed(self):
        self.renderer.marker_size = self.marker_size


# ===============================================================================
# demo object that is used by the demo.py application.
# ===============================================================================
demo = ScatterPlotTraits()

if __name__ == "__main__":
    demo.configure_traits()
