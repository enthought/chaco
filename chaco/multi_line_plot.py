""" Defines the MultiLinePlot class.
"""

from __future__ import with_statement

# Standard library imports
import warnings
from math import ceil, floor

# Major library imports
import numpy as np
from numpy import argsort, array, invert, isnan, take, transpose

# Enthought library imports
from enable.api import black_color_trait, ColorTrait, LineStyle
from traits.api import Float, List, Str, Trait, \
            Bool, Callable, Property, cached_property, Instance, Array
from traitsui.api import Item, View, ScrubberEditor, HGroup

from .array_data_source import ArrayDataSource
from .base import arg_find_runs, bin_search
from .base_xy_plot import BaseXYPlot


class MultiLinePlot(BaseXYPlot):
    """ A plot consisting of multiple lines.

    The data to be plotted must come from a two-dimensional array with shape M by N
    stored in a MultiArrayDataSource object.  M is the number of lines to be plotted,
    and N is the number of points in each line.

    Constructor Parameters
    ----------------------
    index : instance of an ArrayDataSource
        These are the 'x' or abscissa coordinates.

    yindex : instance of ArrayDataSource
        These are the 'y' coordinates.

    value : instance of a MultiArrayDataSource
        Note that the `scale`, `offset` and `normalized_amplitude` attributes of the
        MultiLinePlot control the projection of the traces into the (x,y)
        plot.  In simplest case, `scale=1` and `offset=0`, and `normalized_amplitude`
        controls the scaling of the traces relative to their base y value.

    global_min, global_max : float
        The minimum and maximum values of the data in `value`.  For large
        arrays, computing these could take excessive time, so they must be
        provided when an instance is created.

    normalized_amplitude : Float

    color : ColorTrait

    color_func : Callable or None
        If not None, this Callable overrides `color`.  The argument to `color_func`
        will be the integer index of the trace to be rendered.  `color_func` must
        return an RGBA 4-tuple.
        Default: None

    orientation : str
        Must be 'v' or 'h' (for 'vertical' or 'horizontal', respectively).  This is
        the orientation of the index axis (i.e. the 'x' axis).
        Default: 'h'

    fast_clip : bool
        If True, traces whose *base* 'y' coordinate is outside the value axis range
        are not plotted, even if some of the data in the curve extends into the plot
        region.
        Default: False

    line_width : float
        Width of the plotted lines.

    line_style :
        The style of the trace lines in the plot.

    The following are from the original LinePlot code, and are untested:

    selected_color
    selected_line_style

    """

    # M and N appearing in the comments are as defined in the docstring.

    yindex = Instance(ArrayDataSource)

    # amplitude = Float(0.0)

    # `scale` and `offset` provide a more general transformation, but are currently
    # untested.
    scale = Float(1.0)
    offset = Float(0.0)

    fast_clip = Bool(False)

    # The color of the lines.
    color = black_color_trait

    # A function that returns the color of lines.  Overrides `color` if not None.
    color_func = Trait(None, None, Callable)

    # The color to use to highlight the line when selected.
    selected_color = ColorTrait("lightyellow")

    # The style of the selected line.
    selected_line_style = LineStyle("solid")

    # The name of the key in self.metadata that holds the selection mask
    metadata_name = Str("selections")

    # The thickness of the line.
    line_width = Float(1.0)

    # The line dash style.
    line_style = LineStyle

    use_global_bounds = Bool(True)

    # Minimum value in the `value` data source.  This must be provided
    # in the call to the constructor.
    global_min = Float

    # Maximum value in the `value` data source.  This must be provided
    # in the call to the constructor.
    global_max = Float

    # Normalized amplitude is the value exposed to the user.
    normalized_amplitude = Float(-0.5)

    amplitude_scale = Property(Float, depends_on=['global_min', 'global_max', 'data',
                                                  'use_global_bounds', 'yindex'])

    amplitude = Property(Float, depends_on=['normalized_amplitude',
                                                'amplitude_scale'])

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # The projected 2D numpy array.
    _trace_data = Property(Array, depends_on=['index', 'index.data_changed',
        'value', 'value.data_changed', 'yindex', 'yindex.data_changed',
        'amplitude', 'scale', 'offset'])

    # Cached list of non-NaN arrays of (x,y) data-space points; regardless of
    # self.orientation, this is always stored as (index_pt, value_pt).  This is
    # different from the default BaseXYPlot definition.
    _cached_data_pts = List

    # Cached list of non-NaN arrays of (x,y) screen-space points.
    _cached_screen_pts = List

    #------------------------------------------------------------------------
    #
    #------------------------------------------------------------------------

    def trait_view(self, obj):
        """Create a minimalist View, with just the amplitude and color attributes."""
        # Minimalist Traits UI View for customizing the plot: only the trace amplitude
        # and line color are exposed.
        view = View(
                HGroup(
                    Item('use_global_bounds'),
                    # Item('normalized_amplitude'),
                    # Item('normalized_amplitude', editor=RangeEditor()),
                    Item('normalized_amplitude',
                        editor=ScrubberEditor(increment=0.2, hover_color=0xFFFFFF, active_color=0xA0CD9E,
                                              border_color=0x0000FF)),
                    ),
                Item("color", label="Trace color", style="simple"),
                width=480,
                title="Trace Plot Line Attributes",
                buttons=["OK", "Cancel"])
        return view

    #------------------------------------------------------------------------
    #
    #------------------------------------------------------------------------

    # See base_xy_plot.py for these:
    ## def hittest(self, screen_pt, threshold=7.0):
    ## def interpolate(self, index_value):


    def get_screen_points(self):
        self._gather_points()
        scrn_pts_list = [[self.map_screen(ary) for ary in line]
                                for line in self._cached_data_pts]
        return scrn_pts_list

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    @cached_property
    def _get_amplitude_scale(self):
        """
        If the amplitude is set to this value, the largest trace deviation from
        its base y coordinate will be equal to the y coordinate spacing.
        """
        # Note: Like the rest of the current code, this ignores the `scale` attribute.

        if self.yindex is not None:
            coordinates = self.yindex.get_data()
        else:
            coordinates = []

        if len(coordinates) > 1:
            dy = coordinates[1] - coordinates[0]
            if dy == 0:
                dy = 1.0
        else:
            # default coordinate spacing if there is only 1 coordinate
            dy = 1.0

        if self.use_global_bounds:
            max_abs = max(abs(self.global_min), abs(self.global_max))
        else:
            data = self.value._data
            max_abs = np.max(np.abs(data))

        if max_abs == 0:
            amp_scale = 0.5 * dy
        else:
            amp_scale = 0.5 * dy / max_abs
        return amp_scale

    @cached_property
    def _get_amplitude(self):
        amplitude = self.normalized_amplitude * self.amplitude_scale
        return amplitude

    @cached_property
    def _get__trace_data(self):
        """Compute the transformed data."""

        # Get the array from `value`
        data = self.value._data
        coordinates = self.yindex.get_data()
        channel_data = self.scale*(self.amplitude*data + coordinates[:,np.newaxis]) \
                                + self.offset
        return channel_data


    def _gather_points(self):
        """
        Collects the data points that are within the bounds of the plot and
        caches them.
        """

        if self._cache_valid:
            return

        if not self.index or not self.value:
            return

        index = self.index.get_data()
        varray = self._trace_data

        if varray.size == 0:
            self._cached_data_pts = []
            self._cached_valid = True
            return

        coordinates = self.yindex.get_data()

        if self.fast_clip:
            coord_min = float(coordinates[0])
            coord_max = coordinates[-1]
            slice_min = max(0,ceil((varray.shape[0]-1)*(self.value_range.low - coord_min)/(coord_max - coord_min)))
            slice_max = min(varray.shape[0], 1+floor((varray.shape[0]-1)*(self.value_range.high - coord_min)/(coord_max - coord_min)))
            varray = varray[slice_min:slice_max]
            # FIXME: The y coordinates must also be sliced to match varray.

        # Check to see if the data is completely outside the view region.
        outside = False
        # Check x coordinates.
        low, high = self.index.get_bounds()
        if low > self.index_range.high or high < self.index_range.low:
            outside = True

        # Check y coordinates. Use varray because it is nased on the yindex,
        # but has been shifted up or down depending on the values.
        ylow, yhigh = varray.min(), varray.max()
        if ylow > self.value_range.high or yhigh < self.value_range.low:
            outside = True

        if outside:
            self._cached_data_pts = []
            self._cached_valid = True
            return

        if len(index) == 0 or varray.shape[0] == 0 or varray.shape[1] == 0 \
                or len(index) != varray.shape[1]:
            self._cached_data_pts = []
            self._cache_valid = True
            return

        size_diff = varray.shape[1] - len(index)
        if size_diff > 0:
            warnings.warn('Chaco.LinePlot: value.shape[1] %d - len(index) %d = %d\n' \
                          % (varray.shape[1], len(index), size_diff))
            index_max = len(index)
            varray = varray[:,:index_max]
        else:
            index_max = varray.shape[1]
            index = index[:index_max]

        # Split the index and value raw data into non-NaN chunks.
        # nan_mask is a boolean M by N array.
        nan_mask = invert(isnan(varray)) & invert(isnan(index))
        blocks_list = []
        for nm in nan_mask:
            blocks = [b for b in arg_find_runs(nm, "flat") if nm[b[0]] != 0]
            blocks_list.append(blocks)

        line_points = []
        for k, blocks in enumerate(blocks_list):
            points = []
            for block in blocks:
                start, end = block
                block_index = index[start:end]
                block_value = varray[k, start:end]
                index_mask = self.index_mapper.range.mask_data(block_index)

                runs = [r for r in arg_find_runs(index_mask, "flat") \
                        if index_mask[r[0]] != 0]

                # Check to see if our data view region is between two points in the
                # index data.  If so, then we have to reverse map our current view
                # into the appropriate index and draw the bracketing points.
                if runs == []:
                    data_pt = self.map_data((self.x_mapper.low_pos, self.y_mapper.low_pos))
                    if self.index.sort_order == "none":
                        indices = argsort(index)
                        sorted_index = take(index, indices)
                        sorted_value = take(varray[k], indices)
                        sort = 1
                    else:
                        sorted_index = index
                        sorted_value = varray[k]
                        if self.index.sort_order == "ascending":
                            sort = 1
                        else:
                            sort = -1
                    ndx = bin_search(sorted_index, data_pt, sort)
                    if ndx == -1:
                        # bin_search can return -1 if data_pt is outside the bounds
                        # of the source data
                        continue


                    z = transpose(array((sorted_index[ndx:ndx+2],
                                                   sorted_value[ndx:ndx+2])))
                    points.append(z)

                else:
                    # Expand the width of every group of points so we draw the lines
                    # up to their next point, outside the plot area
                    data_end = len(index_mask)
                    for run in runs:
                        start, end = run
                        if start != 0:
                            start -= 1
                        if end != data_end:
                            end += 1

                        run_data = transpose(array((block_index[start:end],
                                                    block_value[start:end])))
                        points.append(run_data)
            line_points.append(points)

        self._cached_data_pts = line_points
        self._cache_valid = True
        return


    # See base_xy_plot.py for:
    ## def _downsample(self):
    ## def _downsample_vectorized(self):


    def _render(self, gc, line_points, selected_points=None):

        if len(line_points) == 0:
            return

        with gc:
            gc.set_antialias(True)
            gc.clip_to_rect(self.x, self.y, self.width, self.height)

            render = self._render_normal

            if selected_points is not None:
                gc.set_stroke_color(self.selected_color_)
                gc.set_line_width(self.line_width+10.0)
                gc.set_line_dash(self.selected_line_style_)
                render(gc, selected_points)

            if self.color_func is not None:
                # Existence of self.color_func overrides self.color.
                color_func = self.color_func
            else:
                color_func = lambda k: self.color_

            tmp = list(enumerate(line_points))
            # Note: the list is reversed for testing with _render_filled.
            for k, points in reversed(tmp):
                color = color_func(k)
                # Apply the alpha
                alpha = color[-1] if len(color) == 4 else 1
                color = color[:3] + (alpha * self.alpha,)
                gc.set_stroke_color(color)
                gc.set_line_width(self.line_width)
                gc.set_line_dash(self.line_style_)
                render(gc, points)

            # Draw the default axes, if necessary
            self._draw_default_axes(gc)

    def _render_normal(self, gc, points):
        for ary in points:
            if len(ary) > 0:
                gc.begin_path()
                gc.lines(ary)
                gc.stroke_path()
        return


    def _render_icon(self, gc, x, y, width, height):
        with gc:
            gc.set_stroke_color(self.color_)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)
            gc.set_antialias(0)
            gc.move_to(x, y+height/2)
            gc.line_to(x+width, y+height/2)
            gc.stroke_path()


    def _alpha_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        return

    def _color_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        return

    def _line_style_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        return

    def _line_width_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        return

    def _amplitude_changed(self):
        self.value.data_changed = True
        self.invalidate_draw()
        self.request_redraw()
        return

    def __getstate__(self):
        state = super(MultiLinePlot,self).__getstate__()
        for key in ['traits_view']:
            if key in state:
                del state[key]

        return state
