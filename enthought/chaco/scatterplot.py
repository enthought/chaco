""" Defines the ScatterPlot class, and associated Traits UI view and helper
function.
"""

# Major library imports
from numpy import argmin, around, array, asarray, compress, invert, isnan, \
                sqrt, sum, transpose

# Enthought library imports
from enthought.enable.api import black_color_trait, ColorTrait
from enthought.kiva import STROKE
from enthought.traits.api import Any, Array, Bool, Float, Int, Trait
from enthought.traits.ui.api import View, VGroup, Item

# Local relative imports
from base_xy_plot import BaseXYPlot
from scatter_markers import AbstractMarker, CustomMarker, \
                            MarkerNameDict, marker_trait
from speedups import scatterplot_gather_points


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


class ScatterPlot(BaseXYPlot):
    """
    Renders a scatter plot, given an index and value arrays.
    """

    # The symbol to use if **marker** is set to "custom". This attribute must
    # be a compiled path for the given Kiva context.
    custom_symbol = Any

    #------------------------------------------------------------------------
    # Styles on a ScatterPlot
    #------------------------------------------------------------------------

    # The type of marker to use.  This is a mapped trait using strings as the
    # keys.
    marker = marker_trait

    # The pixel size of the marker, not including the thickness of the outline.
    marker_size = Float(4.0)

    # The thickness, in pixels, of the outline to draw around the marker.  If
    # this is 0, no outline is drawn.
    line_width = Float(1.0)

    # The fill color of the marker.
    color = black_color_trait

    # The color of the outline to draw around the marker.
    outline_color = black_color_trait

    # Traits UI View for customizing the plot.
    traits_view = ScatterPlotView()

    #------------------------------------------------------------------------
    # Selection and selection rendering
    # A selection on the lot is indicated by setting the index or value
    # datasource's 'selections' metadata item to a list of indices, or the
    # 'selection_mask' metadata to a boolean array of the same length as the
    # datasource.
    #------------------------------------------------------------------------

    selection_marker = marker_trait

    selection_marker_size = Float(4.0)

    selection_line_width = Float(1.0)

    selection_color = ColorTrait("yellow")

    selection_outline_color = black_color_trait

    _cached_selected_pts = Trait(None, None, Array)
    _cached_selected_screen_pts = Array
    _selection_cache_valid = Bool(False)

    #------------------------------------------------------------------------
    # Overridden PlotRenderer methods
    #------------------------------------------------------------------------

    def map_screen(self, data_array):
        """ Maps an array of data points into screen space and returns it as
        an array. 
        
        Implements the AbstractPlotRenderer interface.
        """
        # data_array is Nx2 array
        if len(data_array) == 0:
            return []
        
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

    def map_index(self, screen_pt, threshold=0.0, outside_returns_none=True, \
                  index_only = False):
        """ Maps a screen space point to an index into the plot's index array(s).
        
        Overrides the BaseXYPlot implementation..
        """
        # Brute force implementation
        all_data = transpose(array([self.index.get_data(), self.value.get_data()]))
        screen_points = around(self.map_screen(all_data))
        if len(screen_points) == 0:
            return None
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

    def _gather_points_old(self):
        """
        Collects the data points that are within the bounds of the plot and 
        caches them
        """
        if self._cache_valid and self._selection_cache_valid:
            return

        if not self.index or not self.value:
            return

        index, index_mask = self.index.get_data_mask()
        value, value_mask = self.value.get_data_mask()

        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            self._cached_data_pts = []
            self._cache_valid = True
            return

        index_range_mask = self.index_mapper.range.mask_data(index)
        value_range_mask = self.value_mapper.range.mask_data(value)

        nan_mask = invert(isnan(index)) & index_mask & \
                   invert(isnan(value)) & value_mask
        point_mask = nan_mask & index_range_mask & value_range_mask

        if not self._cache_valid:
            points = transpose(array((index,value)))
            self._cached_data_pts = compress(point_mask, points, axis=0)
            self._cache_valid = True

        if not self._selection_cache_valid:
            indices = None
            # Check both datasources for metadata
            # XXX: Only one is used, and if both are defined, then self.index
            # happens to take precendence.  Perhaps this should be more
            # structured?  Hopefully, when we create the Selection objects,
            # we'll have to define a small algebra about how they are combined,
            # and this will fall out...
            for ds in (self.index, self.value):
                if ds.metadata.get('selections', None) is not None:
                    indices = ds.metadata['selections']
                    point_mask = point_mask[indices]
                    points = transpose(array((index[indices], value[indices])))
                elif ds.metadata.get('selection_mask', None) is not None:
                    point_mask &= ds.metadata['selection_mask']
                else:
                    continue

                self._cached_selected_pts = compress(point_mask, points, axis=0)
                self._selection_cache_valid = True
                break
            else:
                self._cached_selected_pts = None
                self._selection_cache_valid = True

        return

    def _gather_points_fast(self):
        if self._cache_valid and self._selection_cache_valid:
            return

        if not self.index or not self.value:
            return

        index, index_mask = self.index.get_data_mask()
        value, value_mask = self.value.get_data_mask()

        index_range = self.index_mapper.range
        value_range = self.value_mapper.range

        kw = {}
        for axis in ("index", "value"):
            ds = getattr(self, axis)
            if ds.metadata.get('selections', None) is not None:
                kw[axis + "_sel"] = ds.metadata['selections']
            if ds.metadata.get('selection_mask', None) is not None:
                kw[axis + "_sel_mask"] = ds.metadata['selection_mask']

        points, selections = scatterplot_gather_points(index, index_range.low, index_range.high,
                                    value, value_range.low, value_range.high,
                                    index_mask = index_mask, 
                                    value_mask = value_mask,
                                    **kw)

        if not self._cache_valid:
            self._cached_data_pts = points
            self._cache_valid = True

        if not self._selection_cache_valid:
            if selections is not None and len(selections) > 0:
                self._cached_selected_pts = points[selections]
                self._selection_cache_valid = True
            else:
                self._cached_selected_pts = None
                self._selection_cache_valid = True

        
    def _gather_points(self):
        #self._gather_points_fast()
        self._gather_points_old()

    def _render(self, gc, points, icon_mode=False):
        """
        This same method is used both to render the scatterplot and to
        draw just the iconified version of this plot, with the latter
        simply requiring that a few steps be skipped.
        """

        if not icon_mode:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
        render_markers(gc, points, self.marker, self.marker_size,
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


    def _render_icon(self, gc, x, y, width, height):
        point = array([x+width/2, y+height/2])
        self._render(gc, [point], icon_mode=True)
        return

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _alpha_changed(self):
        self.color_ = self.color_[0:3] + (self.alpha,)
        self.outline_color_ = self.outline_color_[0:3] + (self.alpha,)
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

#------------------------------------------------------------------------------
# Helper functions for scatterplot rendering
#------------------------------------------------------------------------------

def render_markers(gc, points, marker, marker_size,
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
    if type(marker) == str:
        marker = MarkerNameDict[marker]()
    elif issubclass(marker, AbstractMarker):
        marker = marker()

    gc.save_state()

    gc.set_line_dash(None)
    if marker.draw_mode == STROKE:
        gc.set_stroke_color(color)
        gc.set_line_width(line_width)
    else:
        gc.set_stroke_color(outline_color)
        gc.set_line_width(line_width)
        gc.set_fill_color(color)

    gc.begin_path()

    # This is the fastest method - use one of the kiva built-in markers
    if (not debug) and hasattr(gc, "draw_marker_at_points") \
        and (marker.__class__ != CustomMarker) \
        and (gc.draw_marker_at_points(points,
                                      marker_size,
                                      marker.kiva_marker) != 0):
            pass

    # The second fastest method - draw the path into a compiled path, then
    # draw the compiled path at each point
    elif hasattr(gc, 'draw_path_at_points'):
        #if debug:
        #    import pdb; pdb.set_trace()
        if marker.__class__ != CustomMarker:
            path = gc.get_empty_path()
            marker.add_to_path(path, marker_size)
            mode = marker.draw_mode
        else:
            path = custom_symbol
            mode = STROKE
        if not marker.antialias:
            gc.set_antialias(False)
        gc.draw_path_at_points(points, path, mode)

    # Neither of the fast functions worked, so use the brute-force, manual way
    else:
        if not marker.antialias:
            gc.set_antialias(False)
        if marker.__class__ != CustomMarker:
            for sx,sy in points:
                gc.save_state()
                gc.translate_ctm(sx, sy)
                # Kiva GCs have a path-drawing interface
                marker.add_to_path(gc, marker_size)
                gc.draw_path(marker.draw_mode)
                gc.restore_state()
        else:
            path = custom_symbol
            for sx,sy in points:
                gc.save_state()
                gc.translate_ctm(sx, sy)
                gc.add_path(path)
                gc.draw_path(STROKE)
                gc.restore_state()


    gc.restore_state()
    return



# EOF
