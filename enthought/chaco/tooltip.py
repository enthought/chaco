""" Defines the ToolTip class.
"""

from __future__ import with_statement

from numpy import array

# Enthought library imports
from enthought.enable.api import black_color_trait, white_color_trait
from enthought.enable.font_metrics_provider import font_metrics_provider
from enthought.kiva.traits.kiva_font_trait import KivaFont
from enthought.traits.api import Any, Bool, List, Int, Float, on_trait_change


# Local imports
from abstract_overlay import AbstractOverlay
from plot_component import PlotComponent
from label import Label


class ToolTip(AbstractOverlay):
    """ An overlay that is a toolip.
    """
    # The font to render the tooltip.
    font = KivaFont('modern 10')

    # The color of the text in the tooltip
    text_color = black_color_trait

    # The ammount of space between the border and the text.
    border_padding = Int(4)

    # The number of pixels between lines.
    line_spacing = Int(4)

    # List of text strings to put in the tooltip.
    lines = List

    # Angle to rotate (counterclockwise) in degrees. NB this will *only*
    # currently affect text, so probably only useful if borders and background
    # are disabled
    rotate_angle = Float(0.0)

    # Should the tooltip automatically reposition itself to remain visible
    # and unclipped on its overlaid component?
    auto_adjust = Bool(True)

    # The tooltip is a fixed size. (Overrides PlotComponent.)
    resizable = ""

    # Use a visible border. (Overrides Enable Component.)
    border_visible = True

    # Use a white background color (overrides AbstractOverlay).
    bgcolor = white_color_trait

    #----------------------------------------------------------------------
    # Private Traits
    #----------------------------------------------------------------------

    _font_metrics_provider = Any()

    _text_props_valid = Bool(False)

    _max_line_width = Float(0.0)

    _total_line_height = Float(0.0)

    def draw(self, gc, view_bounds=None, mode='normal'):
        """ Draws the plot component.

        Overrides PlotComponent.
        """
        self.overlay(self, gc, view_bounds=view_bounds, mode='normal')
        return

    def overlay(self, component, gc, view_bounds=None, mode='normal'):
        """ Draws the tooltip overlaid on another component.

        Overrides AbstractOverlay.
        """
        self.do_layout()
        PlotComponent._draw(self, gc, view_bounds, mode)
        return

    def _draw_overlay(self, gc, view_bounds=None, mode='normal'):
        """ Draws the overlay layer of a component.

        Overrides PlotComponent.
        """
        with gc:
            edge_space = self.border_width + self.border_padding
            gc.translate_ctm(self.x + edge_space, self.y)
            y = self.height - edge_space
            for i, label in enumerate(self._cached_labels):
                label_height = self._cached_line_sizes[i][1]
                y -= label_height
                gc.translate_ctm(0,y)
                label.draw(gc)
                gc.translate_ctm(0,-y)
                y -= self.line_spacing
        return


    def _do_layout(self):
        """Computes the size of the tooltip, and creates the label objects
        for each line.

        Overrides PlotComponent.
        """
        if not self._text_props_valid:
            self._recompute_text()

        outer_bounds = [self._max_line_width + 2*self.border_padding + self.hpadding,
                             self._total_line_height + 2*self.border_padding + self.vpadding]

        self.outer_bounds = outer_bounds

        if self.auto_adjust and self.component is not None:
            new_pos = list(self.outer_position)
            for dimindex in (0,1):
                pos = self.position[dimindex]
                extent = outer_bounds[dimindex]
                c_min = self.component.position[dimindex]
                c_max = c_min + self.component.bounds[dimindex]
                # Is the tooltip just too wide/tall?
                if extent > (c_max - c_min):
                    new_pos[dimindex] = c_min
                # Does it extend over the c_max edge?  (right/top)
                elif pos + extent > c_max:
                    new_pos[dimindex] = c_max - extent

                # Does it extend over the c_min edge? This is not an elif so
                # that we can fix the situation where the c_max edge adjustment
                # above pushes the position negative.
                if new_pos[dimindex] < c_min:
                    new_pos[dimindex] = c_min

            self.outer_position = new_pos

        self._layout_needed = False

    def _recompute_text(self):
        labels = [Label(text=line, font=self.font, margin=0,
                        bgcolor='transparent', border_width=0,
                        color=self.text_color, rotate_angle=self.rotate_angle)
                    for line in self.lines]
        dummy_gc = self._font_metrics_provider
        line_sizes = array([label.get_width_height(dummy_gc)
                            for label in labels])
        self._cached_labels = labels
        self._cached_line_sizes = line_sizes
        self._max_line_width = max(line_sizes[:,0])
        self._total_line_height = sum(line_sizes[:,1]) + \
                                  len(line_sizes-1)*self.line_spacing
        self._layout_needed = True
        return

    def __font_metrics_provider_default(self):
        return font_metrics_provider()

    @on_trait_change("font,text_color,lines,lines_items")
    def _invalidate_text_props(self):
        self._text_props_valid = False
        self._layout_needed = True

    @on_trait_change("border_padding,line_spacing,lines,lines_items,padding")
    def _invalidate_layout(self):
        self._layout_needed = True
        self.request_redraw()
