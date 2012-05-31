""" Defines the LassoOverlay class.
"""

from __future__ import with_statement

from numpy import concatenate, newaxis

# Enthought library imports
from enable.api import ColorTrait, LineStyle
from traits.api import Float, Instance, Bool

# Local imports
from abstract_overlay import AbstractOverlay

class LassoOverlay(AbstractOverlay):
    """ Draws a lasso selection region on top of a plot.

    LassoOverlay gets its data from a LassoSelection.
    """

    # The LassoSelection that provides the data for this overlay.
    lasso_selection = Instance('chaco.tools.lasso_selection.LassoSelection')
    # The fill color for the selection region.
    selection_fill_color = ColorTrait('lightskyblue')
    # The border color for the selection region.
    selection_border_color = ColorTrait('dodgerblue')
    # The transparency level for the selection fill color.
    selection_alpha = Float(0.8)
    # The width of the selection border.
    selection_border_width = Float(2.0)
    # The line style of the selection border.
    selection_border_dash = LineStyle

    # The background color (overrides AbstractOverlay).
    bgcolor = 'clear'

    # Whether to draw the lasso
    # depends on the state of the lasso tool
    _draw_selection = Bool(False)

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.

        Implements AbstractOverlay.
        """
        if not self._draw_selection:
            return
        with gc:
            c = other_component
            gc.clip_to_rect(c.x, c.y, c.width, c.height)
            self._draw_component(gc, view_bounds, mode)
        return

    def _updated_changed_for_lasso_selection(self):
        self.component.invalidate_draw()
        self.component.request_redraw()

    def _event_state_fired_for_lasso_selection(self, val):
        self._draw_selection = val == 'selecting'
        self.component.invalidate_draw()
        self.component.request_redraw()

    def _draw_component(self, gc, view_bounds=None, mode='normal'):
        """ Draws the component.

        This method is preserved for backwards compatibility with _old_draw().
        Overrides PlotComponent.
        """
        with gc:
            # We may need to make map_screen more flexible in the number of dimensions
            # it accepts for ths to work well.
            for selection in self.lasso_selection.disjoint_selections:
                points = self.component.map_screen(selection)
                if len(points) == 0:
                    return
                points = concatenate((points, points[0, newaxis]), axis=0)
                gc.set_line_width(self.selection_border_width)
                gc.set_line_dash(self.selection_border_dash_)
                gc.set_fill_color(self.selection_fill_color_)
                gc.set_stroke_color(self.selection_border_color_)
                gc.set_alpha(self.selection_alpha)
                gc.lines(points)
                gc.draw_path()
