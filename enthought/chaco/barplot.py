""" Defines the BarPlot class.
"""
import logging

from numpy import array, compress, column_stack, invert, isnan, transpose, zeros
from enthought.traits.api import Any, Bool, Enum, Float, Instance, Property, \
        Range
from enthought.enable.api import black_color_trait
from enthought.kiva import FILL_STROKE

# Local relative imports
from enthought.chaco.abstract_plot_renderer import AbstractPlotRenderer
from abstract_mapper import AbstractMapper
from array_data_source import ArrayDataSource
from base import reverse_map_1d


logger = logging.getLogger(__name__)


class BarPlot(AbstractPlotRenderer):
    """
    A renderer for bar charts.
    """
    # The data source to use for the index coordinate.
    index = Instance(ArrayDataSource)

    # The data source to use as value points.
    value = Instance(ArrayDataSource)

    # The data source to use as "starting" values for the bars.
    starting_value = Instance(ArrayDataSource)

    # Labels for the indices.
    index_mapper = Instance(AbstractMapper)
    # Labels for the values.
    value_mapper = Instance(AbstractMapper)

    # The orientation of the index axis.
    orientation = Enum("h", "v")

    # The direction of the index axis with respect to the graphics context's 
    # direction.
    index_direction = Enum("normal", "flipped")

    # The direction of the value axis with respect to the graphics context's 
    # direction.
    value_direction = Enum("normal", "flipped")

    # Type of width used for bars:
    #
    # 'data' 
    #     The width is in the units along the x-dimension of the data space.  
    # 'screen' 
    #     The width uses a fixed width of pixels.
    bar_width_type = Enum("data", "screen")

    # Width of the bars, in data or screen space (determined by 
    # **bar_width_type**).
    bar_width = Float(10)

    # Round on rectangle dimensions? This is not strictly an "antialias", but
    # it has the same effect through exact pixel drawing.
    antialias = Bool(True)

    # Width of the border of the bars.
    line_width = Float(1.0)
    # Color of the border of the bars.
    line_color = black_color_trait
    # Color to fill the bars.
    fill_color = black_color_trait
    
    # Overall alpha value of the image. Ranges from 0.0 for transparent to 1.0
    alpha = Range(0.0, 1.0, 1.0)
    

    #use_draw_order = False

    # Convenience properties that correspond to either index_mapper or
    # value_mapper, depending on the orientation of the plot.

    # Corresponds to either **index_mapper** or **value_mapper**, depending on
    # the orientation of the plot.
    x_mapper = Property
    # Corresponds to either **value_mapper** or **index_mapper**, depending on
    # the orientation of the plot.
    y_mapper = Property

    # Corresponds to either **index_direction** or **value_direction**, 
    # depending on the orientation of the plot.
    x_direction = Property
    # Corresponds to either **value_direction** or **index_direction**, 
    # depending on the orientation of the plot
    y_direction = Property

    # Convenience property for accessing the index data range.
    index_range = Property
    # Convenience property for accessing the value data range.
    value_range = Property


    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # Indicates whether or not the data cache is valid
    _cache_valid = Bool(False)

    # Cached data values from the datasources.  If **bar_width_type** is "data",
    # then this is an Nx4 array of (bar_left, bar_right, start, end) for a
    # bar plot in normal orientation.  If **bar_width_type** is "screen", then
    # this is an Nx3 array of (bar_center, start, end).
    _cached_data_pts = Any


    #------------------------------------------------------------------------
    # AbstractPlotRenderer interface
    #------------------------------------------------------------------------

    def __init__(self, *args, **kw):
        # These Traits depend on others, so we'll defer setting them until
        # after the HasTraits initialization has been completed.
        later_list = ['index_direction', 'value_direction']
        postponed = {}
        for name in later_list:
            if name in kw:
                postponed[name] = kw.pop(name)

        super(BarPlot, self).__init__(*args, **kw)

        # Set any keyword Traits that were postponed.
        self.set(**postponed)

        # update colors to use the correct alpha channel
        self.line_color_ = self.line_color_[0:3] + (self.alpha,)
        self.fill_color_ = self.fill_color_[0:3] + (self.alpha,)

    def map_screen(self, data_array):
        """ Maps an array of data points into screen space and returns it as
        an array. 
        
        Implements the AbstractPlotRenderer interface.
        """
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

    def map_data(self, screen_pt):
        """ Maps a screen space point into the "index" space of the plot.
        
        Implements the AbstractPlotRenderer interface.
        """
        if self.orientation == "h":
            screen_coord = screen_pt[0]
        else:
            screen_coord = screen_pt[1]
        return self.index_mapper.map_data(screen_coord)

    def map_index(self, screen_pt, threshold=2.0, outside_returns_none=True,
                  index_only=False):
        """ Maps a screen space point to an index into the plot's index array(s).
        
        Implements the AbstractPlotRenderer interface.
        """
        data_pt = self.map_data(screen_pt)
        if ((data_pt < self.index_mapper.range.low) or \
            (data_pt > self.index_mapper.range.high)) and outside_returns_none:
            return None
        index_data = self.index.get_data()
        value_data = self.value.get_data()

        if len(value_data) == 0 or len(index_data) == 0:
            return None

        try:
            ndx = reverse_map_1d(index_data, data_pt, self.index.sort_order)
        except IndexError:
            return None

        x = index_data[ndx]
        y = value_data[ndx]
        
        result = self.map_screen(array([[x,y]]))
        if result is None:
            return None

        sx, sy = result[0]
        if index_only and ((screen_pt[0]-sx) < threshold):
            return ndx
        elif ((screen_pt[0]-sx)**2 + (screen_pt[1]-sy)**2 < threshold*threshold):
            return ndx
        else:
            return None

    #------------------------------------------------------------------------
    # PlotComponent interface
    #------------------------------------------------------------------------

    def _gather_points(self):
        """ Collects data points that are within the range of the plot, and
        caches them in **_cached_data_pts**.
        """
        index, index_mask = self.index.get_data_mask()
        value, value_mask = self.value.get_data_mask()

        if not self.index or not self.value:
            return

        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            logger.warn("Chaco: using empty dataset; index_len=%d, value_len=%d." \
                                % (len(index), len(value)))
            self._cached_data_pts = array([])
            self._cache_valid = True
            return

        # TODO: Until we code up a better handling of value-based culling that
        # takes into account starting_value and dataspace bar widths, just use
        # the index culling for now.
#        value_range_mask = self.value_mapper.range.mask_data(value)
#        nan_mask = invert(isnan(index_mask)) & invert(isnan(value_mask))
#        point_mask = index_mask & value_mask & nan_mask & \
#                     index_range_mask & value_range_mask

        index_range_mask = self.index_mapper.range.mask_data(index)
        nan_mask = invert(isnan(index_mask))
        point_mask = index_mask & nan_mask & index_range_mask

        if self.starting_value is None:
            starting_values = zeros(len(index))
        else:
            starting_values = self.starting_value.get_data()

        if self.bar_width_type == "data":
            half_width = self.bar_width / 2.0
            points = column_stack((index-half_width, index+half_width,
                                   starting_values, value))
        else:
            points = column_stack((index, starting_values, value))
        self._cached_data_pts = compress(point_mask, points, axis=0)

        self._cache_valid = True
        return

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        """ Draws the 'plot' layer.
        """
        if not self._cache_valid:
            self._gather_points()

        data = self._cached_data_pts
        if data.size == 0:
            # Nothing to draw.
            return

        gc.save_state()
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        gc.set_antialias(self.antialias)
        gc.set_stroke_color(self.line_color_)
        gc.set_fill_color(self.fill_color_)
        gc.set_line_width(self.line_width)

        if self.bar_width_type == "data":
            # map the bar start and stop locations into screen space
            lower_left_pts = self.map_screen(data[:,(0,2)])
            upper_right_pts = self.map_screen(data[:,(1,3)])
        else:
            half_width = self.bar_width / 2.0
            # map the bar centers into screen space and then compute the bar
            # start and end positions
            lower_left_pts = self.map_screen(data[:,(0,1)])
            upper_right_pts = self.map_screen(data[:,(0,2)])
            lower_left_pts[:,0] -= half_width
            upper_right_pts[:,0] += half_width

        bounds = upper_right_pts - lower_left_pts
        gc.rects(column_stack((lower_left_pts, bounds)))
        gc.draw_path()
        gc.restore_state()


    def _draw_default_axes(self, gc):
        if not self.origin_axis_visible:
            return
        gc.save_state()
        gc.set_stroke_color(self.origin_axis_color_)
        gc.set_line_width(self.origin_axis_width)
        gc.set_line_dash(None)

        for range in (self.index_mapper.range, self.value_mapper.range):
            if (range.low < 0) and (range.high > 0):
                if range == self.index_mapper.range:
                    dual = self.value_mapper.range
                    data_pts = array([[0.0,dual.low], [0.0, dual.high]])
                else:
                    dual = self.index_mapper.range
                    data_pts = array([[dual.low,0.0], [dual.high,0.0]])
                start,end = self.map_screen(data_pts)
                gc.move_to(int(start[0])+0.5, int(start[1])+0.5)
                gc.line_to(int(end[0])+0.5, int(end[1])+0.5)
                gc.stroke_path()
        gc.restore_state()
        return

    def _render_icon(self, gc, x, y, width, height):
        gc.save_state()
        gc.set_fill_color(self.fill_color_)
        gc.set_stroke_color(self.line_color_)
        gc.rect(x+width/4, y+height/4, width/2, height/2)
        gc.draw_path(FILL_STROKE)
        gc.restore_state()

    def _post_load(self):
        super(BarPlot, self)._post_load()
        return


    #------------------------------------------------------------------------
    # Properties
    #------------------------------------------------------------------------

    def _get_index_range(self):
        return self.index_mapper.range

    def _set_index_range(self, val):
        self.index_mapper.range = val

    def _get_value_range(self):
        return self.value_mapper.range

    def _set_value_range(self, val):
        self.value_mapper.range = val

    def _get_x_mapper(self):
        if self.orientation == "h":
            return self.index_mapper
        else:
            return self.value_mapper

    def _get_y_mapper(self):
        if self.orientation == "h":
            return self.value_mapper
        else:
            return self.index_mapper

    def _get_x_direction(self):
        if self.orientation == "h":
            return self.index_direction
        else:
            return self.value_direction

    def _get_y_direction(self):
        if self.orientation == "h":
            return self.value_direction
        else:
            return self.index_direction

    #------------------------------------------------------------------------
    # Event handlers - these are mostly copied from BaseXYPlot
    #------------------------------------------------------------------------

    def _update_mappers(self):
        """ Updates the index and value mappers. Called by trait change handlers
        for various traits.
        """
        x_mapper = self.index_mapper
        y_mapper = self.value_mapper
        x_dir = self.index_direction
        y_dir = self.value_direction

        if self.orientation == "v":
            x_mapper, y_mapper = y_mapper, x_mapper
            x_dir, y_dir = y_dir, x_dir

        x = self.x
        x2 = self.x2
        y = self.y
        y2 = self.y2

        if x_mapper is not None:
            if x_dir =="normal":
                x_mapper.low_pos = x
                x_mapper.high_pos = x2
            else:
                x_mapper.low_pos = x2
                x_mapper.high_pos = x

        if y_mapper is not None:
            if y_dir == "normal":
                y_mapper.low_pos = y
                y_mapper.high_pos = y2
            else:
                y_mapper.low_pos = y2
                y_mapper.high_pos = y

        self.invalidate_draw()
        self._cache_valid = False

    def _alpha_changed(self):
        self.line_color_ = self.line_color_[0:3] + (self.alpha,)
        self.fill_color_ = self.fill_color_[0:3] + (self.alpha,)
        self.invalidate_draw()
        self.request_redraw()

    def _bounds_changed(self, old, new):
        super(BarPlot, self)._bounds_changed(old, new)
        self._update_mappers()

    def _bounds_items_changed(self, event):
        super(BarPlot, self)._bounds_items_changed(event)
        self._update_mappers()

    def _orientation_changed(self):
        self._update_mappers()

    def _index_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._either_data_changed, "data_changed", remove=True)
        if new is not None:
            new.on_trait_change(self._either_data_changed, "data_changed")
        self._either_data_changed()

    def _index_direction_changed(self):
        m = self.index_mapper
        m.low_pos, m.high_pos = m.high_pos, m.low_pos
        self.invalidate_draw()

    def _value_direction_changed(self):
        m = self.value_mapper
        m.low_pos, m.high_pos = m.high_pos, m.low_pos
        self.invalidate_draw()

    def _either_data_changed(self):
        self.invalidate_draw()
        self._cache_valid = False
        self.request_redraw()

    def _value_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._either_data_changed, "data_changed", remove=True)
        if new is not None:
            new.on_trait_change(self._either_data_changed, "data_changed")
        self._either_data_changed()

    def _index_mapper_changed(self, old, new):
        return self._either_mapper_changed(old, new)

    def _value_mapper_changed(self, old, new):
        return self._either_mapper_changed(old, new)

    def _either_mapper_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._mapper_updated_handler, "updated", remove=True)
        if new is not None:
            new.on_trait_change(self._mapper_updated_handler, "updated")
        self.invalidate_draw()

    def _mapper_updated_handler(self):
        self._cache_valid = False
        self.invalidate_draw()
        self.request_redraw()

    def _bar_width_changed(self):
        self._cache_valid = False
        self.invalidate_draw()
        self.request_redraw()

    def _bar_width_type_changed(self):
        self._cache_valid = False
        self.invalidate_draw()
        self.request_redraw()



### EOF ####################################################################
