
from numpy import linspace, sin

from enthought.chaco.api import ArrayPlotData, Plot
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, View

class LinePlot(HasTraits):

    plot = Instance(Plot)

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False), 
                       width=800, height=600, resizable=True)

    def _plot_default(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 500)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a line plot in the Plot
        plot.plot(("x", "y"), type="line", color="blue")
        return plot

if __name__ == "__main__":
    LinePlot().edit_traits(kind="livemodal")

