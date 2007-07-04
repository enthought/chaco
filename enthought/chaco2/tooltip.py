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

    # The font to render the tooltip in
    font = KivaFont('modern 10')

    # Override the Component border setting
    border_visible = True

    # The ammount of space between the border and the text
    border_padding = Int(4)

    # Set a default white background color
    bgcolor = white_color_trait

    # The spacing between lines
    line_spacing = Int(4)

    # The text to put in the tooltip
    lines = List

    # Make the tooltip a fixed size
    resizable = ""

    # The available space in the four directions, used to determine layout
    # If -1, assume there is enough space in that direction.

    left_space = Float(-1)
    right_space = Float(-1)
    below_space = Float(-1)
    above_space = Float(-1)

    # The position of the corner of the tooltip.  Which corner this represents
    # depends on the space available on each side, set by left_space, etc.

    corner_point = List

    #----------------------------------------------------------------------
    # Private Traits
    #----------------------------------------------------------------------


    def draw(self, gc, view_bounds=None, mode='normal'):
        self.overlay(self, gc, view_bounds=view_bounds, mode='normal')
        return

    def overlay(self, component, gc, view_bounds=None, mode='normal'):
        self.do_layout()
        PlotComponent._draw(self, gc, view_bounds, mode)
        return

    def _draw_overlay(self, gc, view_bounds=None, mode='normal'):
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


