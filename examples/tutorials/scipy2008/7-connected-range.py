
from numpy import linspace, sin

from enthought.chaco.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco.tools.api import PanTool, SimpleZoom
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, View

class ConnectedRange(HasTraits):

    plot = Instance(HPlotContainer)

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False), 
                       width=1000, height=600, resizable=True)

    def _plot_default(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        # Create the scatter plot
        scatter = Plot(plotdata, border_visible=True)
        scatter.plot(("x", "y"), type="scatter", color="blue")
        # Create the line plot
        line = Plot(plotdata, border_visible=True)
        line.plot(("x", "y"), type="line", color="blue")
        # Create a horizontal container and put the two plots inside it
        container = HPlotContainer(scatter, line)
        # Set the two plots' ranges to be the same
        scatter.range2d = line.range2d
        # Add pan/zoom so we can see they are connected
        scatter.tools.append(PanTool(scatter))
        scatter.tools.append(SimpleZoom(scatter))
        line.tools.append(PanTool(line))
        line.tools.append(SimpleZoom(line))
        return container

if __name__ == "__main__":
    ConnectedRange().edit_traits(kind="livemodal")

