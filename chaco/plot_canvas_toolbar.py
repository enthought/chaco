from traits.api import Any, Enum, Int
from enable.drawing.api import ToolbarButton

# Local, relative imports
from .plot_containers import VPlotContainer
from .plot_component import PlotComponent


class PlotCanvasToolbar(VPlotContainer):

    # The placement of the toolbar over the canvas
    align = Enum("ur", "ul", "ll", "lr", "left", "right", "top", "bottom")

    # The spacing between buttons
    button_spacing = Int(5)

    # The (optional) component that we overlay
    component = Any

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
        self._do_layout()
        pref_size = self.get_preferred_size()

        # Special check for when we are overlaying an instance of enable.Canvas
        if hasattr(component, "view_bounds"):
            cx, cy, cx2, cy2 = component.view_bounds
            cwidth = cx2 - cx + 1
            cheight = cy2 - cy + 1
        else:
            cx, cy = component.position
            cheight, cwidth = component.bounds

        if self.align in ("ur", "ul", "top"):
            y = cy + cheight - self.outer_height
        elif self.align in ("lr", "ll", "bottom"):
            y = cy
        else:
            y = cy + (cheight - pref_size[1]) / 2

        if self.align in ("ur", "lr", "right"):
            x = cx + cwidth - self.outer_width
        elif self.align in ("ul", "ll", "left"):
            x = cx
        else:
            x = cx + (cwidth - pref_size[0]) / 2

        self.outer_position = [x, y]
        VPlotContainer._draw(self, gc, view_bounds, mode)

    def _request_redraw(self):
        # Reproduce the behavior in AbstractOverlay to dispatch a
        # redraw event up to our overlaid component
        if self.component is not None:
            self.component.request_redraw()
        super(PlotCanvasToolbar, self)._request_redraw()


class PlotToolbarButton(PlotComponent, ToolbarButton):

    label_font = "Arial 12"

    unified_draw = True

    def _draw_plot(self, *args, **kw):
        return self._draw_mainlayer(*args, **kw)
