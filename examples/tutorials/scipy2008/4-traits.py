
from numpy import linspace, sin

from enthought.enable.api import ColorTrait
from enthought.chaco.api import ArrayPlotData, Plot, marker_trait
from enthought.chaco.tools.api import PanTool, SimpleZoom
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance, Int
from enthought.traits.ui.api import Group, Item, View

class ScatterPlotTraits(HasTraits):

    plot = Instance(Plot)
    color = ColorTrait("blue")
    marker = marker_trait
    marker_size = Int(4)

    traits_view = View(
                    Group(Item('color', label="Color", style="custom"),
                        Item('marker', label="Marker"),
                        Item('marker_size', label="Size"),
                        Item('plot', editor=ComponentEditor(), show_label=False),
                        orientation = "vertical"),
                    width=800, height=600, resizable=True,
                    )

    def _plot_default(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 500)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        plot.legend.visible = True
        # Create a line plot in the Plot
        plot.plot(("x", "y"), name="plot1", type="scatter", color="blue")
        plot.tools.append(PanTool(plot))
        plot.tools.append(SimpleZoom(plot))
        return plot

    def _color_changed(self):
        self.plot.plots["plot1"][0].color = self.color

    def _marker_changed(self):
        self.plot.plots["plot1"][0].marker = self.marker

    def _marker_size_changed(self):
        self.plot.plots["plot1"][0].marker_size = self.marker_size

if __name__ == "__main__":
    ScatterPlotTraits().edit_traits(kind="livemodal")

