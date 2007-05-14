
from numpy import concatenate, newaxis

# Enthought library imports
from enthought.enable2.api import ColorTrait, LineStyle
from enthought.traits.api import Float, Instance

# Local imports
from abstract_overlay import AbstractOverlay

class LassoOverlay(AbstractOverlay):
    """
    LassoOverlay is an AbstractOverlay that draws a lasso selection region
    on top of a plot.  LassoOverlay gets its data from a LassoSelection.
    """
    lasso_selection = Instance('enthought.chaco2.tools.lasso_selection.LassoSelection')
    selection_fill_color = ColorTrait('lightskyblue')
    selection_border_color = ColorTrait('dodgerblue')
    selection_alpha = Float(0.8)
    selection_border_width = Float(2.0)
    selection_border_dash = LineStyle
    
    bgcolor = 'clear'

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        gc.save_state()
        c = other_component
        gc.clip_to_rect(c.x, c.y, c.width, c.height)
        self._draw_component(gc, view_bounds, mode)
        gc.restore_state()
        return

    def _updated_changed_for_lasso_selection(self):
        self.component.invalidate_draw()
        self.component.request_redraw()

    def _draw_component(self, gc, view_bounds=None, mode='normal'):
        gc.save_state()
        try:
            # We may need to make map_screen more flexible in the number of dimensions
            # it accepts for ths to work well.
            points = self.component.map_screen(self.lasso_selection.dataspace_points)
            if len(points) == 0:
                return
            points = concatenate((points, points[0, newaxis]), axis=0)
            gc.set_line_width(self.border_width)
            gc.set_line_dash(self.selection_border_dash_)
            gc.set_fill_color(self.selection_fill_color_)
            gc.set_stroke_color(self.selection_border_color_)
            gc.set_alpha(self.selection_alpha)
            gc.lines(points)
            gc.draw_path()
        finally:
            gc.restore_state()
        
        
        
