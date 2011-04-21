
from numpy import linspace, sin

from enthought.chaco.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool
from enthought.enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View

class ConnectedRange(HasTraits):

    container = Instance(HPlotContainer)

    traits_view = View(Item('container', editor=ComponentEditor(), show_label=False),
                       width=1000, height=600, resizable=True,
                       title="Connected Range")

    def __init__(self):
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

        # Create a horizontal container and put the two plots inside it
        self.container = HPlotContainer(scatter, line)

        # Add pan/zoom so we can see they are connected
        scatter.tools.append(PanTool(scatter))
        scatter.tools.append(ZoomTool(scatter))
        line.tools.append(PanTool(line))
        line.tools.append(ZoomTool(line))

        # Set the two plots' ranges to be the same
        scatter.range2d = line.range2d


#===============================================================================
# demo object that is used by the demo.py application.
#===============================================================================
demo=ConnectedRange()
if __name__ == "__main__":
    demo.configure_traits()
