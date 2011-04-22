
from numpy import linspace, sin

from enthought.chaco.api import ArrayPlotData, Plot, AbstractOverlay
from enthought.chaco.tools.api import PanTool, MoveTool
from enable.component_editor import ComponentEditor
from enable.api import ColorTrait
from traits.api import Button, CArray, Bool, Float, Range, \
                                 HasTraits, Instance, Property
from traitsui.api import Item, View, Group, RangeEditor, \
                                    HGroup, Handler, spring

class CustomOverlay(AbstractOverlay):
    x = Float(10, editor=RangeEditor(low=1.0, high=600, mode="slider"))
    y = Float(10, editor=RangeEditor(low=1.0, high=500, mode="slider"))
    width = Range(10.0, 300, editor=RangeEditor(low=10.0, high=300, mode="slider"))
    height = Range(10.0, 300, editor=RangeEditor(low=10.0, high=300, mode="slider"))
    color = ColorTrait("red")
    dataspace = Bool(False)
    position = Property

    _anchor = CArray

    traits_view = View(Group(
                        Item("x"), Item("y"), Item("width"), Item("height"),
                        Item("color"),
                        Item("dataspace", label="Data space?"),
                        orientation = "vertical"
                        ))

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        if self.dataspace:
            self.x, self.y = component.map_screen(self._anchor)
        gc.set_fill_color(self.color_)
        x = self.x + component.x
        y = self.y + component.y
        gc.rect(x, y, self.width, self.height)
        gc.fill_path()

    def _get_position(self):
        return [self.x, self.y]

    def _set_position(self, newpos):
        self.x, self.y = newpos

    def _anytrait_changed(self):
        self.component.request_redraw()

    def _dataspace_changed(self):
        if self.dataspace:
            # Map our current x,y point into data space
            self._anchor = self.component.map_data((self.x, self.y))

class ScatterPlotHandler(Handler):

    def object_edit_overlay_changed(self, info):
        info.object.plot.overlays[-1].edit_traits(parent=info.ui.control)
        return

class ScatterPlot(HasTraits):

    plot = Instance(Plot)

    edit_overlay = Button('Edit Overlay')

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False),
                       HGroup(spring,
                              Item('edit_overlay', show_label=False,
                                   emphasized=True,
                                   height=50),
                              spring),
                       handler = ScatterPlotHandler,
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
        # Add our custom overlay to the plot
        overlay = CustomOverlay(plot)
        # Add the MoveTool to the overlay so it can be dragged around usin gthe
        # right mouse button.
        overlay.tools.append(MoveTool(overlay, drag_button="right"))
        plot.overlays.append(overlay)
        return plot

#===============================================================================
# demo object that is used by the demo.py application.
#===============================================================================
demo = ScatterPlot()
if __name__ == "__main__":
    demo.configure_traits()
