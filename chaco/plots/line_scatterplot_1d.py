# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
A 1D scatterplot that draws lines across the renderer at the index values

"""


from numpy import empty

# Enthought library imports
from enable.api import black_color_trait, ColorTrait, LineStyle
from traits.api import Any, Bool, Float, Str

# local imports
from chaco.base_1d_plot import Base1DPlot


class LineScatterPlot1D(Base1DPlot):
    """ A 1D scatterplot that draws lines across the renderer """

    #: The thickness, in pixels, of the lines
    line_width = Float(1.0)

    #: The fill color of the lines.
    color = black_color_trait

    #: The line dash style.
    line_style = LineStyle

    # ------------------------------------------------------------------------
    # Selection and selection rendering
    # A selection on the lot is indicated by setting the index or value
    # datasource's 'selections' metadata item to a list of indices, or the
    # 'selection_mask' metadata to a boolean array of the same length as the
    # datasource.
    # ------------------------------------------------------------------------

    #: whether or not to display a selection
    show_selection = Bool(True)

    #: the plot data metadata name to watch for selection information
    selection_metadata_name = Str("selections")

    #: the thickness, in pixels, of the selected lines
    selected_line_width = Float(1.0)

    #: the color of the selected lines
    selected_color = ColorTrait("yellow")

    #: The line dash style of the selected line.
    selected_line_style = LineStyle("solid")

    #: The fade amount for unselected regions
    unselected_alpha = Float(0.3)

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        """ Draw the plot """
        coord = self._compute_screen_coord()
        lines = empty(shape=(len(coord), 4))

        if self.orientation == "v":
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
        """ Render a sequence of line values, accounting for selections """
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
                if unselected_lines.size > 0:
                    self._render_lines(
                        gc,
                        unselected_lines,
                        self.color_,
                        self.line_width,
                        self.line_style_,
                    )
                if selected_lines.size > 0:
                    self._render_lines(
                        gc,
                        selected_lines,
                        self.selected_color_,
                        self.selected_line_width,
                        self.selected_line_style_,
                    )
            else:
                self._render_lines(
                    gc, lines, self.color_, self.line_width, self.line_style_
                )

    def _render_lines(self, gc, lines, color, width, dash):
        """ Render a collection of lines with a given style """
        with gc:
            gc.set_stroke_color(color)
            gc.set_line_width(width)
            gc.set_line_dash(dash)
            for line in lines:
                gc.begin_path()
                line.shape = (2, 2)
                gc.lines(line)
                gc.stroke_path()
