
from numpy import linspace, sin

from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool
from enable.component_editor import ComponentEditor
from traits.api import Enum, HasTraits, Instance
from traitsui.api import Item, View

class PlotEditor(HasTraits):

    plot = Instance(Plot)
    plot_type = Enum("scatter", "line")
    orientation = Enum("horizontal", "vertical")
    traits_view = View(Item('orientation', label="Orientation"),
                       Item('plot', editor=ComponentEditor(), show_label=False),
                       width=500, height=500, resizable=True,
                       title="Chaco Plot")

    def __init__(self, *args, **kw):
        HasTraits.__init__(self, *args, **kw)
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        # Create the scatter plot
        plot = Plot(plotdata)
        plot.plot(("x", "y"), type=self.plot_type, color="blue")
        plot.tools.append(PanTool(plot))
        plot.tools.append(ZoomTool(plot))
        self.plot = plot

    def _orientation_changed(self):
        if self.orientation == "vertical":
            self.plot.orientation = "v"
        else:
            self.plot.orientation = "h"

if __name__ == "__main__":
    # Create the two plots
    scatter = PlotEditor(plot_type = "scatter")
    line = PlotEditor(plot_type = "line")
    # Hook up their ranges
    scatter.plot.range2d = line.plot.range2d
    # Bring up both plots by calling edit_traits().  (We call configure_traits()
    # on the second one so that the application main loop stays running.)
    line.edit_traits()
    scatter.configure_traits()

