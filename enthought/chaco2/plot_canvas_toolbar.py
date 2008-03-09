
from enthought.traits.api import Enum, Int
from enthought.enable2.drawing.api import DrawingCanvasToolbar, ToolbarButton

# Local, relative imports
from plot_containers import HPlotContainer, VPlotContainer
from plot_component import PlotComponent


class PlotCanvasToolbar(VPlotContainer, DrawingCanvasToolbar):

    spacing = Int(5)

    align = Enum("ur", "ul", "ll", "lr")

    #fit_components = "v"
    
    # Override some inherited traits
    resizable = ""
    fill_padding = False
    unified_draw = True

    #def add_button(self, *args):
    #    DrawingCanvasToolbar.add_button(self, *args)
    #    self._layout_needed = True

    #def get_preferred_size(self):
    #    width = self.hpadding + 2*self.margin + self.button_spacing * (len(self.components) - 1)
    #    height = 2 * self.margin
    #    for c in self.components:
    #        w, h = c.get_preferred_size()
    #        width += w
    #        if h > height:
    #            height = h
    #    height += self.vpadding
    #    return width, height

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Allows the toolbar to behave like an overlay """
        pass

    #def _do_layout(self):
    #    x = self.margin
    #    y = self.margin
    #    for c in self.components:
    #        c.outer_position = [x,y]
    #        x += self.button_spacing + c.outer_width
    #    return

    def _canvas_changed(self):
        # Override the one we inherit from CrawingCanvasToolbar
        return


class PlotToolbarButton(PlotComponent, ToolbarButton):
    
    label_font = "Arial 12"

    unified_draw = True

    def _draw_plot(self, *args, **kw):
        return self._draw_mainlayer(*args, **kw)
