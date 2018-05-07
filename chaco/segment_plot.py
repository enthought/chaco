
import numpy as np

from enable.api import ColorTrait, LineStyle, black_color_trait
from kiva.api import CAP_ROUND
from traits.api import (
    Array, Bool, Float, Instance, List, Property, Str, Tuple, cached_property,
    on_trait_change
)

from chaco.abstract_colormap import AbstractColormap
from chaco.abstract_data_source import AbstractDataSource
from chaco.abstract_mapper import AbstractMapper
from chaco.base import rgba_dtype
from chaco.base_xy_plot import BaseXYPlot


point_dtype = np.dtype([('x', float), ('y', float)])


class SegmentPlot(BaseXYPlot):
    """ Plot that draws a collection of line segments. """

    # The single color to use when color_by_data is False.
    color = black_color_trait(redraw=True)

    # The thickness of the line.
    line_width = Float(1.0, redraw=True)

    # The line dash style.
    line_style = LineStyle(redraw=True)

    # Whether to draw segments using a constant color or colormapped data.
    color_by_data = Bool(False)

    # The data to use for the segment color.  Used only when
    # self.color_by_data is True.
    color_data = Instance(AbstractDataSource, redraw=True)

    # The color mapper to use for the segment data.  Used only when
    # self.color_by_data is True.
    color_mapper = Instance(AbstractColormap, redraw=True)

    # Whether to draw segments using a constant width or mapped width.
    width_by_data = Bool(False, redraw=True)

    # The data to use for segment width.  Used only when self.color_by_width
    # is True.
    width_data = Instance(AbstractDataSource, redraw=True)

    # Whether to draw segments using a constant width or mapped width.
    width_mapper = Instance(AbstractMapper, redraw=True)

    #: Whether or not to shade selected segments.
    show_selection = True

    #: the plot data metadata name to watch for selection information
    selection_metadata_name = Str("selections")

    #: The color to use for selected segments.  Not used if color by data.
    selection_color = ColorTrait('yellow')

    #: The alpha fade to use for non-selected segments.
    selection_alpha = Float(0.3)

    #: The width multiple to use for non-selected segments.
    selection_width = Float(1.0)

    # RGBA tuples for rendering individual segments, in the case where
    # color_by_data is True.  We have one length-4 tuple for each triangle.
    # These are computed using the current color mapper and color_data, with the
    # global 'alpha' mixed in.
    effective_colors = Property(
        Array,
        depends_on=['color_by_data', 'alpha', 'color_mapper.updated',
                    'color_data.data_changed', 'alpha', 'selection_mask',
                    'selection_color', 'selection_alpha'])

    # The widths of the individual lines in screen unis, if mapped to data.
    screen_widths = Property(
        Array,
        depends_on=['width_mapper.updated', 'width_data.data_changed'])


    selected_mask = Property(
        depends_on=['selection_metadata_name', 'index.metadata_changed'])

    # These BaseXYPlot methods either don't make sense or aren't currently
    # implemented for this plot type.

    def get_closest_point(self, *args, **kwargs):
        raise NotImplementedError()

    def get_closest_line(self, *args, **kwargs):
        raise NotImplementedError()

    def hittest(self, *args, **kwargs):
        raise NotImplementedError()

    def map_index(self, *args, **kwargs):
        raise NotImplementedError()

    def _gather_points(self):
        """ Collects the data points that are within the bounds of the plot and
        caches them.
        """
        if self._cache_valid:
            return

        if self.index is None or self.value is None:
            return

        index = self.index.get_data()
        value = self.value.get_data()
        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            points = np.zeros((0, 2, 2), dtype=np.float64)
        else:
            points = np.column_stack([index, value]).reshape(-1, 2, 2)

        # TODO filter for segments intersecting the visible region

        self._cached_data_pts = points
        self._cache_valid = True

    def _render(self, gc, segments):
        """ Render an array of shape (N, 2, 2) of screen-space
        points as a collection of segments.

        """
        colors = self.effective_colors
        widths = self.screen_widths

        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            gc.set_line_dash(self.line_style_)
            gc.set_line_cap(CAP_ROUND)
            starts = segments[:, 0]
            ends = segments[:, 1]

            if len(widths) == 1 and len(colors) == 1 and colors[0]['a'] == 1.0:
                # no alpha, can draw a single unconnected path, faster
                gc.set_line_width(widths[0])
                gc.set_stroke_color(colors[0])
                gc.line_set(starts, ends)
                gc.stroke_path()
            else:
                # draw each segment individually, slower
                starts = starts.ravel().view(point_dtype)
                ends = ends.ravel().view(point_dtype)
                for color, width, start, end in np.broadcast(colors, widths, starts, ends):
                    gc.set_stroke_color(color)
                    gc.set_line_width(float(width))
                    gc.move_to(start['x'], start['y'])
                    gc.line_to(end['x'], end['y'])
                    gc.stroke_path()

    def _render_icon(self, gc, x, y, width, height):
        """ Renders a representation of this plot as an icon into the box
        defined by the parameters.

        Used by the legend.
        """
        with gc:
            gc.set_stroke_color(self.color_)
            gc.set_line_width(self.line_width)
            if hasattr(self, 'line_style_'):
                gc.set_line_dash(self.line_style_)
            gc.move_to(x, y)
            gc.line_to(width, height)

    @on_trait_change('alpha, color_data:data_changed, color_mapper:updated, '
                     'width_data:data_changed, width_mapper.updated, +redraw')
    def _attributes_changed(self):
        self.invalidate_draw()
        self.request_redraw()

    @cached_property
    def _get_effective_colors(self):
        if self.color_by_data:
            color_data = self.color_data.get_data()
            colors = self.color_mapper.map_screen(color_data)
        else:
            if self.selected_mask is not None:
                colors = np.ones((len(self.selected_mask), 4))
                colors[self.selected_mask, :len(self.selected_color_)] = self.selected_color_
                colors[~self.selected_mask, :len(self.color_)] = self.color_
            else:
                colors = np.ones((1, 4))
                colors[:, :len(self.color_)] = self.color_

        if colors.shape[-1] == 4:
            colors[:, -1] *= self.alpha
        else:
            colors = np.column_stack([colors, np.full(len(colors), self.alpha)])

        if self.selected_mask is not None:
            colors[~self.selected_mask, -1] *= self.selection_alpha

        colors = colors.astype(np.float32).view(rgba_dtype)
        colors.shape = (-1,)

        return colors

    @cached_property
    def _get_screen_widths(self):
        if self.width_by_data:
            width_data = self.width_data.get_data()
            widths = self.width_mapper.map_screen(width_data)
        else:
            widths = np.array([self.line_width])

        return widths

    @cached_property
    def _get_selected_mask(self):
        name = self.selection_metadata_name
        md = self.index.metadata
        selection = md.get(name)
        if selection is not None and len(selection) > 0:
            selected_mask = selection[0]
            return selected_mask
        return None


class ColormappedSegmentPlot(SegmentPlot):

    color_by_data = True
