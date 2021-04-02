from numpy import linspace, sin

from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool, DragZoom
from enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance, List
from traitsui.api import Item, View, CheckListEditor


class ToolChooserExample(HasTraits):

    plot = Instance(Plot)
    tools = List(
        editor=CheckListEditor(values=["PanTool", "ZoomTool", "DragZoom"])
    )
    traits_view = View(
        Item("tools", label="Tools", style="custom"),
        Item("plot", editor=ComponentEditor(), show_label=False),
        width=800,
        height=600,
        resizable=True,
        title="Tool Chooser",
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
        self.plot = plot

    def _tools_changed(self):
        classes = [eval(class_name) for class_name in self.tools]

        # Remove all tools from the plot
        plot_tools = self.plot.tools
        for tool in plot_tools:
            plot_tools.remove(tool)

        # Create new instances for the selected tool classes
        for cls in classes:
            self.plot.tools.append(cls(self.plot))


# ===============================================================================
# demo object that is used by the demo.py application.
# ===============================================================================
demo = ToolChooserExample()

if __name__ == "__main__":
    demo.configure_traits()
