
from numpy import linspace, sin

from enthought.chaco.api import ArrayPlotData, VPlotContainer, Plot
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, View

class ContainerExample2(HasTraits):

    plot = Instance(VPlotContainer)

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False), 
                       width=600, height=800, resizable=True)

    def _plot_default(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        # Create the scatter plot
        scatter = Plot(plotdata)
        scatter.plot(("x", "y"), type="scatter", color="blue")
        # Create the line plot
        line = Plot(plotdata)
        line.plot(("x", "y"), type="line", color="blue")
        # Create a vertical container and put the two plots inside it
        container = VPlotContainer(scatter, line)
        return container

if __name__ == "__main__":
    ContainerExample2().edit_traits(kind="livemodal")


