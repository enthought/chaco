"""
Scatterplot in one dimension only
"""


from __future__ import absolute_import

from numpy import empty

# Enthought library imports
from enable.api import black_color_trait, ColorTrait, LineStyle
from traits.api import Any, Bool, Callable, Enum, Float, Str

# local imports
from .base_1d_plot import Base1DPlot
from .scatterplot import render_markers


class LineScatterPlot1D(Base1DPlot):
    """ A scatterplot that in 1D """

    # The thickness, in pixels, of the line
    line_width = Float(1.0)

    # The fill color of the line.
    color = black_color_trait

    # The line dash style.
    line_style = LineStyle


    #------------------------------------------------------------------------
    # Selection and selection rendering
    # A selection on the lot is indicated by setting the index or value
    # datasource's 'selections' metadata item to a list of indices, or the
    # 'selection_mask' metadata to a boolean array of the same length as the
    # datasource.
    #------------------------------------------------------------------------

    selection_metadata_name = Str("selections")

    show_selection = Bool(True)

    selected_line_width = Float(1.0)

    selected_color = ColorTrait("yellow")

    # The style of the selected line.
    selected_line_style = LineStyle("solid")

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        coord = self._compute_screen_coord()
        lines = empty(shape=(len(coord), 4))

        if self.orientation == 'v':
            lines[:, 0] = self.x
            lines[:, 1] = coord
            lines[:, 2] = self.x2
            lines[:, 3] = coord
        else:
            lines[:, 0] = coord
            lines[:, 1] = self.y
            lines[:, 2] = coord
            lines[:, 3] = self.y2

        self._render(gc, lines)

    def _render(self, gc, lines):
        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            if not self.index:
                return
            name = self.selection_metadata_name
            md = self.index.metadata
            if name in md and md[name] is not None and len(md[name]) > 0:
                selected_mask = md[name][0]
                selected_lines = lines[selected_mask]
                unselected_lines = lines[~selected_mask]

                color = list(self.color_)
                color[3] *= self.unselected_alpha
                outline_color = list(self.outline_color_)
                outline_color[3] *= self.unselected_alpha
                if unselected_lines.size > 0:
                    self._render_lines(gc, unselected_lines, self.color_,
                                       self.line_width, self.line_style_)
                if selected_lines.size > 0:
                    self._render_lines(gc, selected_lines, self.selected_color_,
                                       self.selected_line_width, self.selected_line_style_)
            else:
                self._render_lines(gc, lines, self.color_,
                                    self.line_width, self.line_style_)

    def _render_lines(self, gc, lines, color, width, dash):
        with gc:
            gc.set_stroke_color(color)
            gc.set_line_width(width)
            gc.set_line_dash(dash)
            gc.begin_path()
            for line in lines:
                line.shape = (2, 2)
                gc.lines(line)
            gc.stroke_path()

    def _bounds_changed(self, old, new):
        super(LineScatterPlot1D, self)._bounds_changed(old, new)
        self._marker_position = self._get_marker_position()

    def _bounds_items_changed(self, event):
        super(LineScatterPlot1D, self)._bounds_items_changed(event)
        self._marker_position = self._get_marker_position()

    def _orientation_changed(self):
        super(LineScatterPlot1D, self)._orientation_changed()
        self._marker_position = self._get_marker_position()
