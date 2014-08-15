"""
Scatterplot in one dimension only
"""


from __future__ import absolute_import

from numpy import empty

# Enthought library imports
from enable.api import black_color_trait, ColorTrait, MarkerTrait
from traits.api import Any, Bool, Callable, Enum, Float, Str

# local imports
from .base_1d_plot import Base1DPlot
from .scatterplot import render_markers


class ScatterPlot1D(Base1DPlot):
    """ A scatterplot that in 1D """

    # The type of marker to use.  This is a mapped trait using strings as the
    # keys.
    marker = MarkerTrait

    # The pixel size of the marker, not including the thickness of the outline.
    marker_size = Float(4.0)

    # The CompiledPath to use if **marker** is set to "custom". This attribute
    # must be a compiled path for the Kiva context onto which this plot will
    # be rendered.  Usually, importing kiva.GraphicsContext will do
    # the right thing.
    custom_symbol = Any

    # The function which actually renders the markers
    render_markers_func = Callable(render_markers)

    # The thickness, in pixels, of the outline to draw around the marker.  If
    # this is 0, no outline is drawn.
    line_width = Float(1.0)

    # The fill color of the marker.
    color = black_color_trait

    # The color of the outline to draw around the marker.
    outline_color = black_color_trait

    #------------------------------------------------------------------------
    # Selection and selection rendering
    # A selection on the lot is indicated by setting the index or value
    # datasource's 'selections' metadata item to a list of indices, or the
    # 'selection_mask' metadata to a boolean array of the same length as the
    # datasource.
    #------------------------------------------------------------------------

    selection_metadata_name = Str("selections")

    show_selection = Bool(True)

    selection_marker = MarkerTrait

    selection_marker_size = Float(4.0)

    selection_line_width = Float(1.0)

    selection_color = ColorTrait("yellow")

    selection_outline_color = black_color_trait

    #: alignment of markers relative to non-index direction
    marker_alignment = Enum("center", "left", "right", "top", "bottom")

    #: offset of markers relative to non-index direction in pixels
    marker_offset = Float

    #: private trait holding postion of markers relative to non-index direction
    _marker_position = Float


    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        coord = self._compute_screen_coord()
        pts = empty(shape=(len(coord), 2))

        if self.orientation == 'v':
            pts[:, 1] = coord
            pts[:, 0] = self._marker_position
        else:
            pts[:, 0] = coord
            pts[:, 1] = self._marker_position

        self._render(gc, pts)

    def _render(self, gc, pts):
        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            if not self.index:
                return
            name = self.selection_metadata_name
            md = self.index.metadata
            if name in md and md[name] is not None and len(md[name]) > 0:
                selected_mask = md[name][0]
                selected_pts = pts[selected_mask]
                unselected_pts = pts[~selected_mask]

                color = list(self.color_)
                color[3] *= self.unselected_alpha
                outline_color = list(self.outline_color_)
                outline_color[3] *= self.unselected_alpha
                if unselected_pts.size > 0:
                    self.render_markers_func(gc, unselected_pts, self.marker,
                        self.marker_size, tuple(color),
                        self.unselected_line_width, tuple(outline_color),
                        self.custom_symbol)
                if selected_pts.size > 0:
                    self.render_markers_func(gc, selected_pts, self.marker,
                        self.marker_size, self.selected_color_,
                        self.line_width, self.outline_color_,
                        self.custom_symbol)
            else:
                self.render_markers_func(gc, pts, self.marker,
                        self.marker_size, self.color_, self.line_width,self.outline_color_,
                        self.custom_symbol)

    def __marker_positon_default(self):
        return self._get_marker_position()

    def _get_marker_position(self):
        x, y = self.position
        w, h = self.bounds

        if self.orientation == 'v':
            y, h = x, w

        if self.marker_alignment == 'center':
            position = y + h/2.0
        elif self.marker_alignment in ['left', 'bottom']:
            position = y
        elif self.marker_alignment in ['right', 'top']:
            position = y + h

        position += self.marker_offset
        return position

    def _bounds_changed(self, old, new):
        super(ScatterPlot1D, self)._bounds_changed(old, new)
        self._marker_position = self._get_marker_position()

    def _bounds_items_changed(self, event):
        super(ScatterPlot1D, self)._bounds_items_changed(event)
        self._marker_position = self._get_marker_position()

    def _orientation_changed(self):
        super(ScatterPlot1D, self)._orientation_changed()
        self._marker_position = self._get_marker_position()

    def _marker_alignment_changed(self):
        self._marker_position = self._get_marker_position()
