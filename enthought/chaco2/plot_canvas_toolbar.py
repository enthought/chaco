
from enthought.traits.api import Enum, Int
from enthought.enable2.drawing.api import DrawingCanvasToolbar, ToolbarButton

# Local, relative imports
from plot_containers import HPlotContainer, VPlotContainer
from plot_component import PlotComponent


class PlotCanvasToolbar(VPlotContainer, DrawingCanvasToolbar):

    align = Enum("ur", "ul", "ll", "lr")

    # Override some inherited traits
    spacing = 5
    fit_components = "hv"
    resizable = "hv"
    halign = "center"
    valign = "center"
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
