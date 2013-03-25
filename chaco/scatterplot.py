""" Defines the ScatterPlot class, and associated Traits UI view and helper
function.
"""

# Standard library imports
import itertools

# Major library imports
from numpy import abs, argmin, around, array, asarray, concatenate, invert, \
                  take, isnan, sqrt, sum, transpose, ndarray, newaxis, zeros, \
                  nonzero, argsort

# Enthought library imports
from enable.api import black_color_trait, ColorTrait, AbstractMarker, \
        CustomMarker, MarkerNameDict, MarkerTrait
from kiva.constants import STROKE
from traits.api import Any, Array, Bool, Float, Trait, Callable, Property, \
        Tuple, Either, Instance, Enum, Dict, cached_property
from traitsui.api import View, VGroup, Item

# Local relative imports
from base_xy_plot import BaseXYPlot
from base import reverse_map_1d, left_shift, right_shift
from array_data_source import ArrayDataSource
from color_mapper import ColorMapper

#------------------------------------------------------------------------------
# Traits UI View for customizing a scatter plot.
#------------------------------------------------------------------------------

class ScatterPlotView(View):
    """ Traits UI View for customizing a scatter plot.
    """
    def __init__(self):
        vgroup = VGroup(
                Item("marker", label="Marker type"),
                Item("marker_size", label="Size"),
                Item("color", label="Color", style="custom"),
                )
        super(ScatterPlotView, self).__init__(vgroup)
        self.buttons = ["OK", "Cancel"]

#------------------------------------------------------------------------------
# Helper functions for scatterplot rendering
#------------------------------------------------------------------------------


def render_markers(gc, points, marker, marker_size,
                   color, line_width, outline_color,
                   custom_symbol=None, debug=False, point_mask=None):
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
    point_mask : array of bools
        The mask specifying which points need to be rendered. The `points`
        array is already masked
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

        if isinstance(marker_size, ndarray):
            if point_mask is not None:
                marker_size = marker_size[point_mask]
        else:
            marker_size = itertools.repeat(marker_size)

        if not marker.antialias:
            gc.set_antialias(False)
        if not isinstance(marker, CustomMarker):
            for pt, size in itertools.izip(points, marker_size):
                sx, sy = pt
                with gc:
                    gc.translate_ctm(sx, sy)
                    # Kiva GCs have a path-drawing interface
                    marker.add_to_path(gc, size)
                    gc.draw_path(marker.draw_mode)
        else:
            path = custom_symbol
            for pt, size in itertools.izip(points, marker_size):
                sx, sy = pt
                with gc:
                    gc.translate_ctm(sx, sy)
                    gc.scale_ctm(size, size)
                    gc.add_path(path)
                    gc.draw_path(STROKE)

    return

#------------------------------------------------------------------------------
# The scatter plot
#------------------------------------------------------------------------------


class ScatterPlot(BaseXYPlot):
    """
    Renders a scatter plot, given an index and value arrays.
    """

    # The CompiledPath to use if **marker** is set to "custom". This attribute
    # must be a compiled path for the Kiva context onto which this plot will
    # be rendered.  Usually, importing kiva.GraphicsContext will do
    # the right thing.
    custom_symbol = Any

    #------------------------------------------------------------------------
    # Styles on a ScatterPlot
    #------------------------------------------------------------------------

    # The type of marker to use.  This is a mapped trait using strings as the
    # keys.
    marker = MarkerTrait

    # The pixel size of the markers, not including the thickness of the outline.
    # Default value is 4.0.
    # TODO: for consistency, there should be a size data source and a mapper
    marker_size = Either(Float, Array)

    # The function which actually renders the markers
    render_markers_func = Callable(render_markers)

    # The thickness, in pixels, of the outline to draw around the marker.  If
    # this is 0, no outline is drawn.
    line_width = Float(1.0)

    # The fill color of the marker.
    color = black_color_trait

    # The color of the outline to draw around the marker.
    outline_color = black_color_trait

    # The RGBA tuple for rendering lines.  It is always a tuple of length 4.
    # It has the same RGB values as color_, and its alpha value is the alpha
    # value of self.color multiplied by self.alpha. 
    effective_color = Property(Tuple, depends_on=['color', 'alpha'])

    # The RGBA tuple for rendering the fill.  It is always a tuple of length 4.
    # It has the same RGB values as outline_color_, and its alpha value is the
    # alpha value of self.outline_color multiplied by self.alpha.   
    effective_outline_color = Property(Tuple, depends_on=['outline_color', 'alpha'])

    # Source for color data.
    color_data = Instance(ArrayDataSource)

    # Mapping for colors.
    color_mapper = Instance(ColorMapper)

    # The alpha value to apply to the result of the color-mapping process.
    # (This makes it easier to create color maps without having to worry
    # about alpha.)
    fill_alpha = Float(1.0)

    # Determines what drawing approach to use:
    #
    # banded:
    #     Draw the points color-band by color-band, thus reducing the number of
    #     set_stroke_color() calls. Disadvantage is that some colors will
    #     appear more prominently than others if there are a lot of
    #     overlapping points.
    # bruteforce:
    #     Set the stroke color before drawing each marker.  Slower, but doesn't
    #     produce the banding effect that puts some colors on top of others;
    #     useful if there is a lot of overlap of the data.
    # auto:
    #     Determines which render method to use based on the number of points
    #
    # TODO: Based on preliminary results, "banded" isn't significantly
    # more expensive than "bruteforce" for small datasets (<1000),
    # so perhaps banded should be removed.
    render_method = Enum("auto", "banded", "bruteforce")

    # A dict mapping color-map indices to arrays of indices into self.data.
    # This is used for the "banded" render method.
    # This mapping is only valid if **_cache_valid** is True.
    _index_bands = Dict()

    # Traits UI View for customizing the plot.
    traits_view = ScatterPlotView()

    #------------------------------------------------------------------------
    # Selection and selection rendering
    # A selection on the lot is indicated by setting the index or value
    # datasource's 'selections' metadata item to a list of indices, or the
    # 'selection_mask' metadata to a boolean array of the same length as the
    # datasource.
    #------------------------------------------------------------------------

    show_selection = Bool(True)

    selection_marker = MarkerTrait

    selection_marker_size = Float(4.0)

    selection_line_width = Float(1.0)

    selection_color = ColorTrait("yellow")

    selection_outline_color = black_color_trait

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    _cached_selected_pts = Trait(None, None, Array)
    _cached_selected_screen_pts = Array
    _cached_point_mask = Array
    _cached_selection_point_mask = Array
    _selection_cache_valid = Bool(False)

    #------------------------------------------------------------------------
    # Overridden PlotRenderer methods
    #------------------------------------------------------------------------

    def map_screen(self, data_array):
        """ Maps an array of data points into screen space and returns it as
        an array.

        The *data_array* parameter must be an Nx2 (index, value) or Nx3
        (index, value, color_value) array. The returned array is an Nx2
        array of (x, y) tuples.
        """
        if len(data_array) == 0:
            return []
        if data_array.shape[1] == 3:
            data_array = data_array[:, :2]

        # XXX: For some reason, doing the tuple unpacking doesn't work:
        #        x_ary, y_ary = transpose(data_array)
        # There is a mysterious error "object of too small depth for
        # desired array".  However, if you catch this exception and
        # try to execute the very same line of code again, it works
        # without any complaints.
        #
        # For now, we just use slicing to assign the X and Y arrays.
        data_array = asarray(data_array)
        if len(data_array.shape) == 1:
            x_ary = data_array[0]
            y_ary = data_array[1]
        else:
            x_ary = data_array[:, 0]
            y_ary = data_array[:, 1]

        sx = self.index_mapper.map_screen(x_ary)
        sy = self.value_mapper.map_screen(y_ary)
        if self.orientation == "h":
            return transpose(array((sx,sy)))
        else:
            return transpose(array((sy,sx)))

    def map_data(self, screen_pt, all_values=True):
        """ Maps a screen space point into the "index" space of the plot.

        Overrides the BaseXYPlot implementation, and always returns an
        array of (index, value) tuples.
        """
        x, y = screen_pt
        if self.orientation == 'v':
            x, y = y, x
        return array((self.index_mapper.map_data(x),
                      self.value_mapper.map_data(y)))

    def map_index(self, screen_pt, threshold=0.0, outside_returns_none=True,
                  index_only=False):
        """ Maps a screen space point to an index into the plot's index array(s).

        Overrides the BaseXYPlot implementation..
        """
        if index_only and self.index.sort_order != "none":
            data_pt = self.map_data(screen_pt)[0]
            # The rest of this was copied out of BaseXYPlot.
            # We can't just used BaseXYPlot.map_index because
            # it expect map_data to return a value, not a pair.
            if ((data_pt < self.index_mapper.range.low) or \
                (data_pt > self.index_mapper.range.high)) and outside_returns_none:
                return None
            index_data = self.index.get_data()
            value_data = self.value.get_data()

            if len(value_data) == 0 or len(index_data) == 0:
                return None

            try:
                ndx = reverse_map_1d(index_data, data_pt, self.index.sort_order)
            except IndexError, e:
                # if reverse_map raises this exception, it means that data_pt is
                # outside the range of values in index_data.
                if outside_returns_none:
                    return None
                else:
                    if data_pt < index_data[0]:
                        return 0
                    else:
                        return len(index_data) - 1

            if threshold == 0.0:
                # Don't do any threshold testing
                return ndx

            x = index_data[ndx]
            y = value_data[ndx]
            if isnan(x) or isnan(y):
                return None
            sx, sy = self.map_screen([x,y])
            if ((threshold == 0.0) or (screen_pt[0]-sx) < threshold):
                return ndx
            else:
                return None
        else:
            # Brute force implementation
            all_data = transpose(array([self.index.get_data(), self.value.get_data()]))
            screen_points = around(self.map_screen(all_data))
            if len(screen_points) == 0:
                return None
            if index_only:
                distances = abs(screen_points[:,0] - screen_pt[0])
            else:
                delta = screen_points - array([screen_pt])
                distances = sqrt(sum(delta*delta, axis=1))
            closest_ndx = argmin(distances)
            if distances[closest_ndx] <= threshold:
                return closest_ndx
            else:
                return None


    #------------------------------------------------------------------------
    # Private methods; implements the BaseXYPlot stub methods
    #------------------------------------------------------------------------

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        """ Draws the 'plot' layer.

        Overrides BaseXYPlot, which isn't really fully generic (it assumes that
        the output of map_screen() is sufficient to render the data).
        """
        self._gather_points()
        if len(self._cached_data_pts) == 0:
            pass
        elif self._cached_data_pts.shape[1] == 2:
            # Take into account fill_alpha even if we are rendering with only two values
            old_color = self.color
            self.color = tuple(self.fill_alpha * array(self.color_))
            super(ScatterPlot, self)._draw_component(gc, view_bounds, mode)
            self.color = old_color
        else:
            colors = self._cached_data_pts[:,2]
            screen_pts = self.map_screen(self._cached_data_pts)
            pts = concatenate((screen_pts, colors[:, newaxis]), axis=1)
            self._render(gc, pts)
        return

    def _gather_points(self):
        """
        Collects the data points that are within the plot bounds and caches them
        """
        if self._cache_valid:
            return

        if not self.index or not self.value:
            self._cached_data_pts = []
            self._cache_valid = True
            return

        index, index_mask = self.index.get_data_mask()
        value, value_mask = self.value.get_data_mask()

        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            self._cached_data_pts = []
            self._cache_valid = True
            return

        index_range_mask = self.index_mapper.range.mask_data(index)
        value_range_mask = self.value_mapper.range.mask_data(value)
        nan_mask = invert(isnan(index_mask)) & invert(isnan(value_mask))
        point_mask = index_mask & value_mask & nan_mask & \
                     index_range_mask & value_range_mask

        if self.color_data is not None:
            if self.color_data.is_masked():
                color_data, color_mask = self.color_data.get_data_mask()
                point_mask = point_mask & color_mask
            else:
                color_data = self.color_data.get_data()

            #color_nan_mask = isreal(color_data)
            color_nan_mask = invert(isnan(color_data))

            point_mask = point_mask & color_nan_mask
            points = transpose(array((index, value, color_data)))
        else:
            points = transpose(array((index, value)))

        self._cached_data_pts = points[point_mask]
        self._cached_point_mask = point_mask

        self._cache_valid = True
        return

    def _render(self, gc, points):
        """ Actually draws the plot.

        TODO: clean up this logic, we're just choosing 1 of 3 render methods here
        """
        # If we don't have a color data set, use the simple render method
        #import pudb; pudb.set_trace()
        if (self.color_mapper is None) or (self.color_data is None):
            self._render_monocolor(gc, points)
            return

        # If the GC doesn't have draw_*_at_points, then use bruteforce
        if hasattr(gc, 'draw_marker_at_points') or hasattr(gc, 'draw_path_at_points'):
            batch_capable = True
        else:
            batch_capable = False

        if self.render_method == 'auto':
            method = self._calc_render_method(len(points))
        else:
            method = self.render_method

        with gc:
            if method == 'bruteforce' or (not batch_capable):
                self._render_bruteforce(gc, points)
            elif method == 'banded':
                self._render_banded(gc, points)
        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _render_monocolor(self, gc, points, icon_mode=False):
        """
        Render points that are all the same color.

        This same method is used both to render the scatterplot and to
        draw just the iconified version of this plot, with the latter
        simply requiring that a few steps be skipped.
        XXX: is there any point in implementing icon_mode here?
             should it be implemented in the other _render methods?
        """

        if not icon_mode:
            gc.save_state()
            gc.clip_to_rect(self.x, self.y, self.width, self.height)

        self.render_markers_func(gc, points, self.marker, self.marker_size,
                       self.color_, self.line_width, self.outline_color_,
                       self.custom_symbol, point_mask=self._cached_point_mask)

        if self._cached_selected_pts is not None and len(self._cached_selected_pts) > 0:
            sel_pts = self.map_screen(self._cached_selected_pts)
            self.render_markers_func(gc, sel_pts, self.selection_marker,
                    self.selection_marker_size, self.selection_color_,
                    self.selection_line_width, self.selection_outline_color_,
                    self.custom_symbol, point_mask=self._cached_point_mask)

        if not icon_mode:
            # Draw the default axes, if necessary
            self._draw_default_axes(gc)
            gc.restore_state()

    def _render_icon(self, gc, x, y, width, height):
        point = array([x+width/2, y+height/2])
        self._render(gc, [point], icon_mode=True)
        return

    def _compute_bands(self, points, smartmode=False):
        """
        Sorts self.data into a list of arrays of data points by color,
        filling in self._index_bands.  If *smartmode* is True, then it first
        calls _calc_render_method() to see which rendering method is
        optimal for the number of points and the distribution of
        color indices; if the rendering method is 'bruteforce', then
        this method short-circuits and returns without doing
        anything.
        """
        if len(points) == 0:
            return
        if self.color_mapper is None:
            return

        # map the V values in the (x,y,v) self.data array

        color_data = points[:,2]
        color_indices = self.color_mapper.map_index(color_data)

        if smartmode and self.render_method == 'bruteforce':
            pass
        else:
            # shuffle_indices indicates how to sort the points in self.data
            # so that their color_indices are in order.  We don't really care
            # about the sorting so much as the fact that once they are sorted,
            # points of the same color are grouped together into "bands".
            shuffle_indices = argsort(color_indices)

            # This pulls values from the color_indices array into
            # sorted_color_indices, using the results of the sort we just did.
            sorted_color_indices = take(color_indices, shuffle_indices)

            # Now we want to determine where the continuous bands are.  We do
            # this by right-shifting the sorted_color_indices array, subtracting
            # it from the original, and looking for all the nonzero points.
            shifted = right_shift(sorted_color_indices, sorted_color_indices[0])
            start_indices = concatenate([[0], nonzero(sorted_color_indices - shifted)[0]])
	    end_indices = left_shift(start_indices, len(sorted_color_indices))

            # Store the shuffled indices in self._index_bands.  We don't store the
            # actual data points because we need to allow the renderer to index into
            # the mapped XY screen positions.
            self._index_bands = {}
            for (start, end) in zip(start_indices, end_indices):
                color_index = sorted_color_indices[start]
                self._index_bands[color_index] = shuffle_indices[start:end]

        self._color_indices = color_indices
        self._cache_valid = True
        return

    def _calc_render_method(self, numpoints):
        """ Returns a string indicating the render method.
        """
        if numpoints > 1000 and isinstance(self.marker_size, float):
            return 'banded'
        else:
            return "bruteforce"

    def _set_draw_info(self, gc, mode, color, outline_color=None,
		       outline_weight=None):
        """ Sets the stroke color, fill color, and line width on the graphics
        context.
        """
        color = tuple(color[:3]) + (self.fill_alpha,)
        if mode == STROKE:
            if outline_color is not None:
                gc.set_stroke_color(color)
        else:
            if outline_color is not None:
                gc.set_stroke_color(outline_color)
            gc.set_fill_color(color)
        if outline_weight is not None:
            gc.set_line_width(outline_weight)
        return

    def _render_banded(self, gc, points):
        """ Draws the points color-band by color-band.
        """
        self._compute_bands(points)

        # Grab the XY values corresponding to each color band of points

        xy_points = points[:,0:2]

        marker = self.marker_
        size = self.marker_size
        assert isinstance(size, float), "Variable size markers not implemented for banded rendering"

        # Set up the GC for drawing
        gc.set_line_dash(None)
        if marker.draw_mode == STROKE:
            gc.set_line_width(self.line_width)

        gc.begin_path()

        cmap = self.color_mapper

        if (hasattr(gc, 'draw_marker_at_points') and self.marker not in ('custom', 'circle', 'diamond')):
            # This is the fastest method: we use one of the built-in markers.
            color_bands = cmap.color_bands
            # Initial setup of drawing parameters
            self._set_draw_info(gc, marker.draw_mode, color_bands[0],
                                self.outline_color_, self.line_width)
            index_bands = self._index_bands
            mode = marker.draw_mode
            for color_index in index_bands.keys():
                self._set_draw_info(gc, mode, color_bands[color_index])
                gc.draw_marker_at_points(xy_points[index_bands[color_index]], size, marker.kiva_marker)


        elif hasattr(gc, 'draw_path_at_points'):
            point_bands = {}
            for color_index, indices in self._index_bands.items():
                point_bands[color_index] = xy_points[indices]
            # We have to construct the path for the marker.
            if self.marker != 'custom':
                path = gc.get_empty_path()
                # turn the class into an instance... we should make
                # add_to_path a class method at some point.
                marker().add_to_path(path, size)
                mode = marker.draw_mode
            else:
                path = self.custom_symbol
                mode = STROKE

            color_bands = cmap.color_bands
            for color_index, xy in point_bands.items():
                self._set_draw_info(gc, mode, color_bands[color_index],
                                    self.outline_color_, self.line_width)
                gc.draw_path_at_points(xy, path, mode)
        else:
            raise RuntimeError, "Batch drawing requested on non-batch-capable GC."
        return

    def _render_bruteforce(self, gc, points):
        """ Draws the points, setting the stroke color for each one.
        """
        #import pudb; pudb.set_trace()
        x, y, colors = transpose(points)

        # Map the colors
        colors = self.color_mapper.map_screen(colors)
        alphas = (zeros(len(colors))+self.fill_alpha)[:, newaxis]
        colors = concatenate((colors[:, :3], alphas), axis=1)

        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            gc.set_stroke_color(self.outline_color_)
            gc.set_line_width(self.line_width)

            marker_cls = self.marker_
            marker_size = self.marker_size
            if isinstance(marker_size, ndarray) and self._cached_point_mask is not None:
                marker_size = marker_size[self._cached_point_mask]
            mode = marker_cls.draw_mode

            if marker_cls != "custom":
                if (hasattr(gc, "draw_marker_at_points") and self.marker not in ('custom', 'circle', 'diamond')):
                    draw_func = lambda x, y, size: gc.draw_marker_at_points([[x,y]], size, marker_cls.kiva_marker)

                elif hasattr(gc, "draw_path_at_points"):
                    # turn the class into an instance... we should make add_to_path a
                    # class method at some point.
                    m = marker_cls()
                    def draw_func(x, y, size):
                        path = gc.get_empty_path()
                        m.add_to_path(path, size)
                        gc.draw_path_at_points([[x, y]], path, mode)
                else:
                    m = marker_cls()
                    def draw_func(x, y, size):
                        gc.translate_ctm(x, y)
                        gc.begin_path()
                        m.add_to_path(gc, size)
                        gc.draw_path(mode)
                        gc.translate_ctm(-x, -y)

                if not isinstance(marker_size, ndarray):
                    marker_size = itertools.repeat(marker_size)
                for sx, sy, size, color in itertools.izip(x, y, marker_size, colors):
                    gc.set_fill_color(color)
                    draw_func(sx, sy, size)

            else:
                path = marker_cls.custom_symbol
                for i in range(len(x)):
                    gc.set_fill_color(colors[i])
                    gc.draw_path_at_points([[x[i], y[i]]], path, STROKE)

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _alpha_changed(self):
        self.invalidate_draw()
        self.request_redraw()

    def _marker_changed(self):
        self.invalidate_draw()
        self.request_redraw()

    def _marker_size_changed(self):
        self.invalidate_draw()
        self.request_redraw()

    def _line_width_changed(self):
        self.invalidate_draw()
        self.request_redraw()

    def _color_changed(self):
        self.invalidate_draw()
        self.request_redraw()

    def _outline_color_changed(self):
        self.invalidate_draw()
        self.request_redraw()

    def _either_metadata_changed(self):
        self._selection_cache_valid = False
        self.invalidate_draw()
        self.request_redraw()

    def _color_data_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._either_data_changed, "data_changed", remove=True)
        if new is not None:
            new.on_trait_change(self._either_data_changed, "data_changed")
        self._either_data_changed()
        return

    def _color_mapper_changed(self, old, new):
        self._cache_valid = False

        if hasattr(new, 'range') and new.range is None and old is not None:
            # Someone passed in a ColorMapper that has no range associated with
            # it. Use the range on the old ColorMapper.
            new.range = old.range

        self.invalidate_draw()
        self.request_redraw()

        return

    def _fill_alpha_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        return

    #------------------------------------------------------------------------
    # Defaults
    #------------------------------------------------------------------------

    def _marker_size_default(self):
        return 4.0

    #------------------------------------------------------------------------
    # Properties
    #------------------------------------------------------------------------

    @cached_property
    def _get_effective_color(self):
        if len(self.color_) == 4:
            edge_alpha = self.color_[-1]
        else:
            edge_alpha = 1.0
        c = self.color_[:3] + (edge_alpha * self.alpha,)
        return c

    @cached_property
    def _get_effective_outline_color(self):
        if len(self.outline_color_) == 4:
            edge_alpha = self.outline_color_[-1]
        else:
            edge_alpha = 1.0
        c = self.outline_color_[:3] + (edge_alpha * self.alpha,)
        return c

# EOF
