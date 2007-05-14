
# Major library imports
from numpy import argmin, around, array, compress, invert, isnan, sqrt, \
                  sum, transpose

# Enthought library imports
from enthought.enable2.api import black_color_trait, white_color_trait
from enthought.kiva import STROKE
from enthought.logger import logger
from enthought.traits.api import Any, Array, Enum, false, Float, Instance, \
                                 Int,  List, RGBAColor
from enthought.traits.ui.api import View, VGroup, Item

# Local relative imports
from base_xy_plot import BaseXYPlot
from scatter_markers import CircleMarker, CustomMarker, DiamondMarker, \
                            MarkerNameDict, marker_trait, PixelMarker
from subdivision_mapper import SubdivisionDataMapper


class ScatterPlotView(View):
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
    Renders a scatter plot given an index and value arrays
    """
    
    # The symbol to use if self.marker is set to "custom". This should be
    # a compiled path for the given kiva context.
    custom_symbol = Any
    
    #------------------------------------------------------------------------
    # Styles on a ScatterPlot
    #------------------------------------------------------------------------
    
    # The type of marker to use.  This is a mapped trait using strings as the
    # keys.
    marker = marker_trait
    
    # The pixel size of the marker (doesn't include the thickness of the outline)
    marker_size = Int(4)
    
    # The thickness, in pixels, of the outline to draw around the marker.  If
    # this is 0, no outline will be drawn.
    line_width = Float(1.0)
    
    # The fill color of the marker
    color = black_color_trait
    
    # The color of the outline to draw around the marker
    outline_color = black_color_trait

    # Traits UI View
    traits_view = ScatterPlotView()

    #------------------------------------------------------------------------
    # Overridden PlotRenderer methods
    #------------------------------------------------------------------------

    def map_screen(self, data_array):
        # data_array is Nx2 array
        if len(data_array) == 0:
            return []
        x_ary, y_ary = transpose(data_array)

        sx = self.index_mapper.map_screen(x_ary)
        sy = self.value_mapper.map_screen(y_ary)
        if self.orientation == "h":
            return transpose(array((sx,sy)))
        else:
            return transpose(array((sy,sx)))

    def map_data(self, screen_pt, all_values=True):
        x, y = screen_pt
        if self.orientation == 'v':
            x, y = y, x
        return array((self.index_mapper.map_data(x),
                      self.value_mapper.map_data(y)))

    def map_index(self, screen_pt, threshold=0.0, outside_returns_none=True, \
                  index_only = False):
        # Brute force implementation
        all_data = transpose(array([self.index.get_data(), self.value.get_data()]))
        screen_points = around(self.map_screen(all_data))
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

    def _gather_points(self):
        """
        Gathers up the data points that are within our bounds and stores them
        """
        if self._cache_valid:
            return
        
        index, index_mask = self.index.get_data_mask()
        value, value_mask = self.value.get_data_mask()
        
        if not self.index or not self.value:
            return
        
        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            logger.warn("Chaco2: using empty dataset; index_len=%d, value_len=%d." \
                                % (len(index), len(value)))
            self._cached_data_pts = []
            self._cache_valid = True
            return
        
        index_range_mask = self.index_mapper.range.mask_data(index)
        value_range_mask = self.value_mapper.range.mask_data(value)
        nan_mask = invert(isnan(index_mask)) & invert(isnan(value_mask))
        point_mask = index_mask & value_mask & nan_mask & \
                     index_range_mask & value_range_mask
        
        points = transpose(array((index,value)))
        self._cached_data_pts = compress(point_mask, points, axis=0)
        
        self._cache_valid = True
        return

    def _render(self, gc, points, icon_mode=False):
        """
        This same method is used to both render the scatterplot as well as
        drawing just the iconified version of this plot, with the latter
        simply requiring that a few steps be skipped.
        """

        if not icon_mode:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
        render_markers(gc, points, self.marker, self.marker_size, 
                       self.color_, self.line_width, self.outline_color_)
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

#------------------------------------------------------------------------------
# Helper functions for scatterplot rendering
#------------------------------------------------------------------------------

def render_markers(gc, points, marker, marker_size,
                   color, line_width, outline_color):
    """ Helper function for 'plot' (PlotComponent instance) to render a
    set of (x,y) points onto gc.  Currently it makes some assumptions about
    the attributes on the plot object; this should be factored out eventually.
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
    if hasattr(gc, "draw_marker_at_points") \
        and (marker.__class__ not in (CustomMarker, CircleMarker, 
                                      DiamondMarker, PixelMarker)) \
        and (gc.draw_marker_at_points(points, 
                                      marker_size, 
                                      marker.kiva_marker) != 0):
            pass

    # The second fastest method - draw the path into a compiled path, then
    # draw the compiled path at each point
    elif hasattr(gc, 'draw_path_at_points'):
        if marker.__class__ != CustomMarker:
            path = gc.get_empty_path()
            marker.add_to_path(path, marker_size)
            mode = marker.draw_mode
        else:
            path = marker.custom_symbol
            mode = STROKE
        if not marker.antialias:
            gc.set_antialias(False)
        gc.draw_path_at_points(points, path, mode)

    # Neither of the fast functions worked, so use the brute-force, manual way
    else:
        if not marker.set_antialias:
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
            path = marker.custom_symbol
            for sx,sy in points:
                gc.save_state()
                gc.translate_ctm(sx, sy)
                gc.add_path(path)
                gc.draw_path(STROKE)
                gc.restore_state()


    gc.restore_state()
    return



# EOF
