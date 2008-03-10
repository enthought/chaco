
from enthought.traits.api import Enum, Int
from enthought.enable2.drawing.api import DrawingCanvasToolbar, ToolbarButton

# Local, relative imports
from plot_containers import HPlotContainer, VPlotContainer
from plot_component import PlotComponent


class PlotCanvasToolbar(VPlotContainer, DrawingCanvasToolbar):

    spacing = Int(5)

    align = Enum("ur", "ul", "ll", "lr")

    fit_components = "v"
    
    # Override some inherited traits
    resizable = "v"
    fill_padding = False
    unified_draw = True

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Allows the toolbar to behave like an overlay """
        pass

    def _canvas_changed(self):
        # Override the one we inherit from CrawingCanvasToolbar
        return


class PlotToolbarButton(PlotComponent, ToolbarButton):
    
    label_font = "Arial 12"

    unified_draw = True

    def _draw_plot(self, *args, **kw):
        return self._draw_mainlayer(*args, **kw)
