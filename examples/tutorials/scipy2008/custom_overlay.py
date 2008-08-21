
from numpy import linspace, sin

from enthought.chaco.api import ArrayPlotData, Plot, AbstractOverlay
from enthought.chaco.tools.api import PanTool
from enthought.enable.component_editor import ComponentEditor
from enthought.enable.api import ColorTrait
from enthought.traits.api import Float, Range, HasTraits, Instance
from enthought.traits.ui.api import Item, View, Group, RangeEditor

class CustomOverlay(AbstractOverlay):
    x = Float(10, editor=RangeEditor(low=1.0, high=600, mode="slider"))
    y = Float(10, editor=RangeEditor(low=1.0, high=500, mode="slider"))
    width = Range(10.0, 300, editor=RangeEditor(low=10.0, high=300, mode="slider"))
    height = Range(10.0, 300, editor=RangeEditor(low=10.0, high=300, mode="slider"))
    color = ColorTrait("red")
    
    traits_view = View(Group(
                        Item("x"), Item("y"), Item("width"), Item("height"),
                        Item("color"), orientation = "vertical"
                        ))
    
    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        gc.set_fill_color(self.color_)
        x = self.x + component.x
        y = self.y + component.y
        gc.rect(x, y, self.width, self.height)
        gc.fill_path()

    def _anytrait_changed(self):
        self.component.request_redraw()
    
class ScatterPlot(HasTraits):

    plot = Instance(Plot)

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False), 
                       width=800, height=600, resizable=True)

    def _plot_default(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a scatter plot in the Plot
        plot.plot(("x", "y"), type="scatter", color="blue")
        plot.tools.append(PanTool(plot))
        # Add our custom tool to the plot
        plot.overlays.append(CustomOverlay(plot))
        return plot

if __name__ == "__main__":
    # Create the main plot and bring it up via calling edit_traits()
    plot = ScatterPlot()
    plot.edit_traits(kind="live")
    # Get a handle to the overlay and edit the traits on it as well
    overlay = plot.plot.overlays[-1]
    overlay.configure_traits()
