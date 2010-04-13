""" Defines the ColormappedScatterPlot and ColormappedScatterPlotView classes.
"""

# Major library imports
from numpy import argsort, array, concatenate, nonzero, invert, take, \
                  isnan, transpose, newaxis, zeros

# Enthought library imports
from enthought.kiva import STROKE
from enthought.traits.api import Dict, Enum, Float, Instance
from enthought.traits.ui.api import Item, RangeEditor

# Local, relative imports
from array_data_source import ArrayDataSource
from base import left_shift, right_shift
from color_mapper import ColorMapper
from scatterplot import ScatterPlot, ScatterPlotView


class ColormappedScatterPlotView(ScatterPlotView):
    """ Traits UI View for customizing a color-mapped scatter plot.
    """
    def __init__(self):
        super(ColormappedScatterPlotView, self).__init__()
        vgroup = self.content
        vgroup.content[0].content.append(Item("fill_alpha", label="Fill alpha",
                                   editor=RangeEditor(low=0.0, high=1.0)))
        return


class ColormappedScatterPlot(ScatterPlot):
    """
    A scatter plot that allows each point to take on a different color,
    corresponding to a color map.

    If the **color_data** or **color_mapper** attributes are None, then it
    behaves like a normal ScatterPlot.
    """

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
    # bands:
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
    # so perhaps bruteforce should be removed.
    render_method = Enum("auto", "banded", "bruteforce")

    # A dict mapping color-map indices to arrays of indices into self.data.
    # This is used for the "banded" render method.
    # This mapping is only valid if **_cache_valid** is True.
    _index_bands = Dict()

    # Traits UI View for customizing the plot. Overrides the ScatterPlot value.
    traits_view = ColormappedScatterPlotView()

    #------------------------------------------------------------------------
    # BaseXYPlot interface
    #------------------------------------------------------------------------

    def map_screen(self, data_array):
        """
        Maps an array of data points into screen space, and returns them as
        an array.

        The *data_array* parameter must be an Nx2 (index, value) or Nx3
        (index, value, color_value) array. The returned array is an Nx2
        array of (x, y) tuples.
        """
        if len(data_array)>0:
            if data_array.shape[1] == 3:
                data_array = data_array[:, :2]
        return super(ColormappedScatterPlot, self).map_screen(data_array)

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
            super(ColormappedScatterPlot, self)._draw_component(gc, view_bounds, mode)
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

        self._cache_valid = True
        return

    def _render(self, gc, points):
        """ Actually draws the plot. 
        
        Overrides the ScatterPlot implementation.
        """
        # If we don't have a color data set, then use the base class to render
        if (self.color_mapper is None) or (self.color_data is None):
            return super(ColormappedScatterPlot, self)._render(gc, points)

        # If the GC doesn't have draw_*_at_points, then use bruteforce
        if hasattr(gc, 'draw_marker_at_points') or hasattr(gc, 'draw_path_at_points'):
            batch_capable = True
        else:
            batch_capable = False

        if self.render_method == 'auto':
            method = self._calc_render_method(len(points))
        else:
            method = self.render_method

        gc.save_state()
        try:
            if method == 'bruteforce' or (not batch_capable):
                self._render_bruteforce(gc, points)
            elif method == 'banded':
                self._render_banded(gc, points)
        finally:
            gc.restore_state()
        return


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

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
        if numpoints > 1000:
            return 'banded'
        else:
            return "bruteforce"

    def _set_draw_info(self, gc, mode, color, outline_color=None, outline_weight=None):
        """ Sets the stroke color, fill color, and line width on the graphics
        context.
        """
        color = tuple(color[:3]) + (self.fill_alpha,)
        if mode == STROKE:
            if outline_color is not None:
                gc.set_stroke_color( color )
        else:
            if outline_color is not None:
                gc.set_stroke_color( outline_color )
            gc.set_fill_color( color )
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

        # Set up the GC for drawing
        gc.set_line_dash( None )
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


        elif hasattr( gc, 'draw_path_at_points' ):
            point_bands = {}
            for color_index, indices in self._index_bands.items():
                point_bands[color_index] = xy_points[indices]
            # We have to construct the path for the marker.
            if self.marker != 'custom':
                path = gc.get_empty_path()
                # turn the class into an instance... we should make add_to_path a
                # class method at some point.
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
        x, y, colors = transpose(points)

        # Map the colors
        colors = self.color_mapper.map_screen(colors)
        alphas = (zeros(len(colors))+self.fill_alpha)[:, newaxis]
        colors = concatenate((colors[:, :3], alphas), axis=1)

        gc.save_state()
        try:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            gc.set_stroke_color(self.outline_color_)
            gc.set_line_width(self.line_width)

            marker = self.marker_
            size = self.marker_size
            mode = marker.draw_mode

            if marker != "custom":
                if (hasattr(gc, "draw_marker_at_points") and self.marker not in ('custom', 'circle', 'diamond')):
                    draw_func = lambda x, y: gc.draw_marker_at_points([[x,y]], size, marker.kiva_marker)

                elif hasattr(gc, "draw_path_at_points"):
                    path = gc.get_empty_path()
                    # turn the class into an instance... we should make add_to_path a
                    # class method at some point.
                    marker().add_to_path(path, size)
                    draw_func = lambda x, y: gc.draw_path_at_points([[x,y]], path, mode)

                for i in range(len(x)):
                    gc.set_fill_color(colors[i])
                    draw_func(x[i], y[i])

            else:
                path = marker.custom_symbol
                for i in range(len(x)):
                    gc.set_fill_color(colors[i])
                    gc.draw_path_at_points([[x[i], y[i]]], path, STROKE)

        finally:
            gc.restore_state()

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

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


# EOF
