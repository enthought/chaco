
from enthought.enable2.drawing.api import DrawingCanvasToolbar, ToolbarButton

from plot_component import PlotComponent


class PlotCanvasToolbar(PlotComponent, DrawingCanvasToolbar):
    
    resizable = ""
    fill_padding = True
    unified_draw = True

    def add_button(self, *args):
        DrawingCanvasToolbar.add_button(self, *args)
        self._layout_needed = True

    def get_preferred_size(self):
        width = self.hpadding + self.button_spacing * (len(self.components) - 1)
        height = 0
        for c in self.components:
            w, h = c.get_preferred_size()
            width += w
            if h > height:
                height = h
        height += self.vpadding
        return width, height

    def _do_layout(self):
        x = 0
        y = 0
        for c in self.components:
            c.outer_position = [x,y]
            x += self.button_spacing + c.outer_width
        return

    def _draw_plot(self, *args, **kw):
        return self._draw_mainlayer(*args, **kw)
    
    def _canvas_changed(self):
        # Override the one we inherit from CrawingCanvasToolbar
        return


class PlotToolbarButton(PlotComponent, ToolbarButton):
    
    label_font = "Arial 12"

    unified_draw = True

    def _draw_plot(self, *args, **kw):
        return self._draw_mainlayer(*args, **kw)
