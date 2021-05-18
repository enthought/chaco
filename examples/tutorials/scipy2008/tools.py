from numpy import linspace, sin

from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool, DragZoom
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View


class ToolsExample(HasTraits):

    plot = Instance(Plot)
    traits_view = View(
        Item("plot", editor=ComponentEditor(), show_label=False),
        width=800,
        height=600,
        resizable=True,
        title="Pan & Zoom",
    )

    def __init__(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 500)
        y = sin(x) * x ** 3
        plotdata = ArrayPlotData(x=x, y=y)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a line plot in the Plot
        plot.plot(("x", "y"), type="line", color="blue")
        # Add the pan and zoom tools
        plot.tools.append(PanTool(plot))
        plot.tools.append(ZoomTool(plot))
        plot.tools.append(DragZoom(plot, drag_button="right"))
        self.plot = plot


# ===============================================================================
# demo object that is used by the demo.py application.
# ===============================================================================
demo = ToolsExample()

if __name__ == "__main__":
    demo.configure_traits()
