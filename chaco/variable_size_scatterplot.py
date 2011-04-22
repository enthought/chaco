from __future__ import with_statement

from enthought.chaco.api import ScatterPlot, render_markers
from enable.api import MarkerNameDict, CustomMarker, AbstractMarker
from enable.kiva.constants import STROKE
from traits.api import Array

class VariableSizeScatterPlot(ScatterPlot):
    marker_size = Array

    def _render(self, gc, points, icon_mode=False):
        """
        This same method is used both to render the scatterplot and to
        draw just the iconified version of this plot, with the latter
        simply requiring that a few steps be skipped.
        """

        if not icon_mode:
            gc.save_state()
            gc.clip_to_rect(self.x, self.y, self.width, self.height)

        render_variable_size_markers(gc, points, self.marker, self.marker_size,
                       self.color_, self.line_width, self.outline_color_,
                       self.custom_symbol)

        if self._cached_selected_pts is not None and len(self._cached_selected_pts) > 0:
            sel_pts = self.map_screen(self._cached_selected_pts)
            render_markers(gc, sel_pts, self.selection_marker,
                    self.selection_marker_size, self.selection_color_,
                    self.selection_line_width, self.selection_outline_color_,
                    self.custom_symbol)

        if not icon_mode:
            # Draw the default axes, if necessary
            self._draw_default_axes(gc)
            gc.restore_state()

def render_variable_size_markers(gc, points, marker, marker_size,
                   color, line_width, outline_color,
                   custom_symbol=None, debug=False):
    """ Helper function for a PlotComponent instance to render a
    set of (x,y) points onto a graphics context.  Currently, it makes some
    assumptions about the attributes on the plot object; these may be factored
    out eventually.

    Parameters
    ----------
    gc : GraphicsContext
        The target for rendering the points
    points : array of (x,y) points
        The points to render
    marker : string, class, or instance
        The type of marker to use for the points
    marker_size : number
        The size of the markers
    color : RGB(A) color
        The color of the markers
    line_width : number
        The width, in pixels, of the marker outline
    outline_color : RGB(A) color
        The color of the marker outline
    custom_symbol : CompiledPath
        If the marker style is 'custom', this is the symbol
    """

    if len(points) == 0:
        return

    # marker can be string, class, or instance
    if isinstance(marker, basestring):
        marker = MarkerNameDict[marker]()
    elif issubclass(marker, AbstractMarker):
        marker = marker()

    with gc:
        gc.set_line_dash(None)
        if marker.draw_mode == STROKE:
            # markers with the STROKE draw mode will not be visible
            # if the line width is zero, so set it to 1
            if line_width == 0:
                line_width = 1.0
            gc.set_stroke_color(color)
            gc.set_line_width(line_width)
        else:
            gc.set_stroke_color(outline_color)
            gc.set_line_width(line_width)
            gc.set_fill_color(color)

        gc.begin_path()

        if not marker.antialias:
            gc.set_antialias(False)
        if not isinstance(marker, CustomMarker):
            for pt,size in zip(points, marker_size):
                sx, sy = pt
                gc.save_state()
                gc.translate_ctm(sx, sy)
                # Kiva GCs have a path-drawing interface
                marker.add_to_path(gc, size)
                gc.draw_path(marker.draw_mode)
                gc.restore_state()
        else:
            path = custom_symbol
            for pt,size in zip(points, marker_size):
                sx, sy = pt
                gc.save_state()
                gc.translate_ctm(sx, sy)
                gc.scale_ctm(size, size)
                gc.add_path(path)
                gc.draw_path(STROKE)
                gc.restore_state()

    return
