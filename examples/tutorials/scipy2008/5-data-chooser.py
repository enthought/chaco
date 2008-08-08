
from numpy import linspace
from scipy.special import jn

from enthought.chaco.api import ArrayPlotData, Plot
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import Dict, Enum, HasTraits, Instance
from enthought.traits.ui.api import Item, View

class DataChooser(HasTraits):

    plot = Instance(Plot)
    data_name = Enum("jn0", "jn1", "jn2")
    bessel_data = Dict

    traits_view = View(Item('data_name', label="Y data"),
                       #Item('color', label="Color", style="custom"),
                       Item('plot', editor=ComponentEditor(), show_label=False), 
                       width=800, height=600, resizable=True)

    def _bessel_data_default(self):
        x = linspace(-5, 10, 100)
        return dict(x = x,
                jn0 = jn(0, x),
                jn1 = jn(1, x),
                jn2 = jn(2, x))

    def _plot_default(self):
        # Create the data and the PlotData object
        plotdata = ArrayPlotData(x = self.bessel_data["x"],
                                 y = self.bessel_data[self.data_name])
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a line plot in the Plot
        plot.plot(("x", "y"), type="line", color="blue")
        return plot

    def _data_name_changed(self, old, new):
        self.plot.data.set_data("y", self.bessel_data[self.data_name])


if __name__ == "__main__":
    DataChooser().edit_traits(kind="livemodal")

