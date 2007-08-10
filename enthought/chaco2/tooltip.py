""" Defines the ToolTip class.
"""

from numpy import array

# Enthought library imports
from enthought.enable2.api import white_color_trait
from enthought.kiva import STROKE, font_metrics_provider
from enthought.kiva.traits.kiva_font_trait import KivaFont
from enthought.traits.api import List, Int, Float


# Local imports
from abstract_overlay import AbstractOverlay
from plot_component import PlotComponent
from label import Label

class ToolTip(AbstractOverlay):
    """ An overlay that is a toolip.
    """
    # The font to render the tooltip.
    font = KivaFont('modern 10')

    # Use a visible border. (Overrides Enable Component.)
    border_visible = True

    # The ammount of space between the border and the text.
    border_padding = Int(4)

    # Use a white background color (overrides AbstractOverlay).
    bgcolor = white_color_trait

    # The number of pixels between lines.
    line_spacing = Int(4)

    # List of text strings to put in the tooltip.
    lines = List

    # The tooltip is a fixed size. (Overrides PlotComponent.)
    resizable = ""

    # The available space in the four directions, used to determine layout
    # If -1, assume there is enough space in that direction.

    # Available space to the left of the tooltip; if -1 there is "enough" space.
    left_space = Float(-1)
    # Available space to the right of the tooltip; if -1 there is "enough" space.
    right_space = Float(-1)
    # Available space below the tooltip; if -1 there is "enough" space.
    below_space = Float(-1)
    # Available space above the tooltip; if -1 there is "enough" space.
    above_space = Float(-1)

    # The position of the corner of the tooltip.  Which corner this represents
    # depends on the space available on each side, set by **left_space**, etc.
    # If any of those values is -1, there is enough space in that direction.
    corner_point = List

    #----------------------------------------------------------------------
    # Private Traits
    #----------------------------------------------------------------------


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
        gc.save_state()
        try:
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
        finally:
            gc.restore_state()
        return


    def _do_layout(self):
        """Computes the size of the tooltip, and creates the label objects
        for each line.
        
        Overrides PlotComponent.
        """
        labels = [Label(text=line, font=self.font, margin=0,
                        bgcolor='transparent', border_width=0)
                  for line in self.lines]

        dummy_gc = font_metrics_provider()
        line_sizes = array([label.get_width_height(dummy_gc)
                            for label in labels])
        max_line_width = max(line_sizes[:,0])
        total_line_height = sum(line_sizes[:,1]) + \
                            len(line_sizes-1)*self.line_spacing
        self.outer_bounds = [max_line_width + 2*self.border_padding + self.hpadding,
                             total_line_height + 2*self.border_padding + self.vpadding]

        if self.corner_point:
            if self.right_space != -1 and self.right_space<self.outer_bounds[0]:
                self.x = self.corner_point[0] - self.outer_bounds[0]
            else:
                self.x = self.corner_point[0]
            if self.above_space != -1 and self.above_space<self.outer_bounds[1]:
                self.y = self.corner_point[1] - self.outer_bounds[1]
            else:
                self.y = self.corner_point[1]

        self._cached_labels = labels
        self._cached_line_sizes = line_sizes

    def _anytrait_changed(self, name, old, new):
        self._layout_needed = True
        self.request_redraw()


