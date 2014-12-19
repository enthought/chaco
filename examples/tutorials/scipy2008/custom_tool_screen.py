
from numpy import linspace, sin

from chaco.api import ArrayPlotData, Plot
from enable.api import BaseTool
from enable.component_editor import ComponentEditor
from traits.api import Enum, HasTraits, Instance
from traitsui.api import Item, View

class CustomTool(BaseTool):

    def normal_mouse_move(self, event):
        print("Screen point:", event.x, event.y)

class ScatterPlot(HasTraits):

    plot = Instance(Plot)

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False),
                       width=800, height=600, resizable=True,
                       title="Custom Tool")

    def _plot_default(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a scatter plot in the Plot
        plot.plot(("x", "y"), type="scatter", color="blue")
        # Add our custom tool to the plot
        plot.tools.append(CustomTool(plot))
        return plot

#===============================================================================
# demo object that is used by the demo.py application.
#===============================================================================
demo=ScatterPlot()
if __name__ == "__main__":
    demo.edit_traits(kind="livemodal")
