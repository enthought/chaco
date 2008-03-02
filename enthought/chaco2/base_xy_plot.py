""" Defines the base class for XY plots.
"""
from math import sqrt
from numpy import around, array, column_stack, isnan, transpose

# Enthought library imports
from enthought.enable2.api import black_color_trait
from enthought.traits.api import Any, Array, Enum, false, Float, Instance, \
                             Property


# Local relative imports
from abstract_mapper import AbstractMapper
from abstract_plot_renderer import AbstractPlotRenderer
from abstract_data_source import AbstractDataSource
from array_data_source import ArrayDataSource
from axis import PlotAxis
from base import point_line_distance, reverse_map_1d
from grid import PlotGrid
from plot_label import PlotLabel


class BaseXYPlot(AbstractPlotRenderer):
    """ Base class for simple X-vs-Y plots that consist of a single index
    data array and a single value data array.  
    
    Subclasses handle the actual rendering, but this base class takes care of
    most of making sure events are wired up between mappers and data or screen
    space changes, etc.
    """

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------
    
    # The data source to use for the index coordinate.
    index = Instance(ArrayDataSource)
    
    # The data source to use as value points.
    value = Instance(AbstractDataSource)

    # Screen mapper for index data.
    index_mapper = Instance(AbstractMapper)
    # Screen mapper for value data
    value_mapper = Instance(AbstractMapper)
    

    # Convenience properties that correspond to either index_mapper or
    # value_mapper, depending on the orientation of the plot.

    # Corresponds to either **index_mapper** or **value_mapper**, depending on
    # the orientation of the plot.
    x_mapper = Property
    # Corresponds to either **value_mapper** or **index_mapper**, depending on
    # the orientation of the plot.
    y_mapper = Property

    # Convenience property for accessing the index data range.    
    index_range = Property
    # Convenience property for accessing the value data range.
    value_range = Property

    # The type of hit-testing that is appropriate for this renderer.  
    # 
    # * 'line': Computes Euclidean distance to the line between the
    #   nearest adjacent points.
    # * 'point': Checks for adjacency to a marker or point.
    hittest_type = Enum("point", "line")

    #------------------------------------------------------------------------
    # Appearance-related traits
    #------------------------------------------------------------------------
    
    # The orientation of the index axis.
    orientation = Enum("h", "v")
    
    #------------------------------------------------------------------------
    # Convenience readonly properties for common annotations
    #------------------------------------------------------------------------

    # Read-only property for horizontal grid.
    hgrid = Property
    # Read-only property for vertical grid.
    vgrid = Property
    # Read-only property for x-axis.
    x_axis = Property
    # Read-only property for y-axis.
    y_axis = Property    
    # Read-only property for labels.
    labels = Property


    #------------------------------------------------------------------------
    # Other public traits
    #------------------------------------------------------------------------
    
    # Does the plot use downsampling?
    # This is not used right now.  It needs an implementation of robust, fast
    # downsampling, which does not exist yet.
    use_downsampling = false
    
    # Does the plot use a spatial subdivision structure for fast hit-testing?
    # This makes data updates slower, but makes hit-tests extremely fast.
    use_subdivision = false
    
    # Overrides the default background color trait in PlotComponent.
    bgcolor = "transparent"

    # This just turns on a simple drawing of the X and Y axes... not a long
    # term solution, but good for testing.
    
    # Defines the origin axis color, for testing.
    origin_axis_color = black_color_trait
    # Defines a the origin axis width, for testing.
    origin_axis_width = Float(1.0)
    # Defines the origin axis visibility, for testing.
    origin_axis_visible = false
    
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # Are the cache traits valid? If False, new ones need to be compute.
    _cache_valid = false

    # Cached array of (x,y) data-space points; regardless of self.orientation,
    # these points are always stored as (index_pt, value_pt).
    _cached_data_pts = Array
    
    # Cached array of (x,y) screen-space points.
    _cached_screen_pts = Array
    
    # Does **_cached_screen_pts** contain the screen-space coordinates
    # of the points currently in **_cached_data_pts**?
    _screen_cache_valid = false

    # Reference to a spatial subdivision acceleration structure.
    _subdivision = Any

    #------------------------------------------------------------------------
    # Abstract methods that subclasses must implement
    #------------------------------------------------------------------------

    def _render(self, gc, points):
        """ Abstract method for rendering points.
        
        Parameters
        ----------
        gc : graphics context
            Target for drawing the points
        points : List of Nx2 arrays 
            Screen-space points to render
        """
        raise NotImplementedError

    def _gather_points(self):
        """ Abstract method to collect data points that are within the range of
        the plot, and cache them.
        """
        raise NotImplementedError
    
    def _downsample(self):
        """ Abstract method that gives the renderer a chance to downsample in
        screen space. 
        """
        # By default, this just does a mapscreen and returns the result
        raise NotImplementedError
    
    #------------------------------------------------------------------------
    # Concrete methods below
    #------------------------------------------------------------------------
    
    def __init__(self, **kwtraits):
        # Handling the setting/initialization of these traits manually because
        # they should be initialized in a certain order.
        kwargs_tmp = {"trait_change_notify": False}
        for trait_name in ("index", "value", "index_mapper", "value_mapper"):
            if trait_name in kwtraits:
                kwargs_tmp[trait_name] = kwtraits.pop(trait_name)
        self.set(**kwargs_tmp)
        AbstractPlotRenderer.__init__(self, **kwtraits)
        if self.index is not None:
            self.index.on_trait_change(self._either_data_changed, "data_changed")
            self.index.on_trait_change(self._either_metadata_changed, "metadata_changed")
        if self.index_mapper:
            self.index_mapper.on_trait_change(self._mapper_updated_handler, "updated")
        if self.value is not None:
            self.value.on_trait_change(self._either_data_changed, "data_changed")
            self.value.on_trait_change(self._either_metadata_changed, "metadata_changed")
        if self.value_mapper:
            self.value_mapper.on_trait_change(self._mapper_updated_handler, "updated")

        # If we are not resizable, we will not get a bounds update upon layout,
        # so we have to manually update our mappers
        if self.resizable == "":
            self._update_mappers()
        return

    def hittest(self, screen_pt, threshold=7.0, return_distance=False):
        """ Performs proximity testing between a given screen point and the
        plot.
        
        Parameters
        ==========
        screen_pt : (x,y) 
            A point to test.
        threshold : integer
            Optional maximum screen space distance (pixels) between
            *screen_pt* and the plot.
        return_distance : Boolean
            If True, returns the distance.

        Returns
        =======
        If self.hittest_type is 'point', then this method returns the screen
        coordinates of the closest point on the plot as a tuple (x,y)

        If self.hittest_type is 'line', then this method returns the screen 
        endpoints of the line segment closest to *screen_pt*, as 
        ((x1,y1), (x2,y2))

        If *screen_pt* does not fall within *threshold* of the plot, then this
        method returns None.
        """
        if self.hittest_type == "point":
            tmp = self.get_closest_point(screen_pt, threshold)
        elif self.hittest_type == "line":
            tmp = self.get_closest_line(screen_pt, threshold)
        else:
            raise ValueError("Unknown hittest type '%s'" % self.hittest_type)

        if tmp is not None:
            if return_distance:
                return tmp
            else:
                return tmp[:-1]
        else:
            return None

    def get_closest_point(self, screen_pt, threshold=7.0):
        """ Tests for proximity in screen-space.  
        
        This method checks only data points, not the line segments connecting
        them; to do the latter use get_closest_line() instead.
        
        Parameters
        ==========
        screen_pt : (x,y) 
            A point to test.
        threshold : integer
            Optional maximum screen space distance (pixels) between
            *screen_pt* and the plot.  If 0.0, then no threshold tests
            are performed, and the nearest point is returned.

        Returns
        =======
        (x, y, distance) of a datapoint nearest to *screen_pt*.
        If no data points are within *threshold* of *screen_pt*, returns None.
        """
        ndx = self.map_index(screen_pt, threshold)
        if ndx is not None:
            x = self.x_mapper.map_screen(self.index.get_data()[ndx])
            y = self.y_mapper.map_screen(self.value.get_data()[ndx])
            return (x, y, sqrt((x-screen_pt[0])**2 + (y-screen_pt[1])**2))
        else:
            return None
        
    def get_closest_line(self, screen_pt, threshold=7.0):
        """ Tests for proximity in screen-space against lines connecting the
        points in this plot's dataset.
        
        Parameters
        ==========
        screen_pt : (x,y) 
            A point to test.
        threshold : integer
            Optional maximum screen space distance (pixels) between
            the line and the plot.  If 0.0, then the method returns the closest
            line regardless of distance from the plot.

        Returns
        =======
        (x1, y1, x2, y2, dist) of the endpoints of the line segment
        closest to *screen_pt*.  The *dist* element is the perpendicular 
        distance from *screen_pt* to the line.  If there is only a single point
        in the renderer's data, then the method returns the same point twice.
           
        If no data points are within *threshold* of *screen_pt*, returns None.
        """
        ndx = self.map_index(screen_pt, threshold=0.0)
        if ndx is None:
            return None

        index_data = self.index.get_data()
        value_data = self.value.get_data()
        x = self.x_mapper.map_screen(index_data[ndx])
        y = self.y_mapper.map_screen(value_data[ndx])

        # We need to find another index so we have two points; in the
        # even that we only have 1 point, just return that point.
        datalen = len(index_data)
        if datalen == 1:
            dist = (x, y, sqrt((x-screen_pt[0])**2 + (y-screen_pt[1])**2))
            if (threshold == 0.0) or (dist <= threshold):
                return (x, y, x, y, dist)
            else:
                return None
        else:
            if (ndx == 0) or (screen_pt[0] >= x):
                ndx2 = ndx + 1
            elif (ndx == datalen - 1) or (screen_pt[0] <= x):
                ndx2 = ndx - 1
            x2 = self.x_mapper.map_screen(index_data[ndx2])
            y2 = self.y_mapper.map_screen(value_data[ndx2])
            dist = point_line_distance(screen_pt, (x,y), (x2,y2))
            if (threshold == 0.0) or (dist <= threshold):
                return (x, y, x2, y2, dist)
            else:
                return None


    #------------------------------------------------------------------------
    # AbstractPlotRenderer interface
    #------------------------------------------------------------------------

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
    
    def map_data(self, screen_pt, all_values=False):
        """ Maps a screen space point into the "index" space of the plot.
        
        Implements the AbstractPlotRenderer interface.
        
        If *all_values* is True, returns an array of (index, value) tuples; 
        otherwise, it returns only the index values.
        """
        x, y = screen_pt
        if self.orientation == 'v':
                x, y = y, x
        if all_values:
            return array((self.index_mapper.map_data(x),
                      self.value_mapper.map_data(y)))
        else:
            return self.index_mapper.map_data(x)
    
    def map_index(self, screen_pt, threshold=2.0, outside_returns_none=True, \
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
        if index_only and ((threshold == 0.0) or (screen_pt[0]-sx) < threshold):
            return ndx
        elif ((screen_pt[0]-sx)**2 + (screen_pt[1]-sy)**2 < threshold*threshold):
            return ndx
        else:
            return None

    def get_screen_points(self):
        """Returns the currently visible screen-space points.  
        
        Intended for use with overlays.
        """
        self._gather_points()
        if self.use_downsampling:
            # The BaseXYPlot implementation of _downsample doesn't actually
            # do any downsampling.
            return self._downsample()
        else:
            return self.map_screen(self._cached_data_pts)

    
    #------------------------------------------------------------------------
    # PlotComponent interface
    #------------------------------------------------------------------------
    
    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        """ Draws the 'plot' layer.
        """
        self._draw_component(gc, view_bounds, mode)
        return

    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        # This method should be folded into self._draw_plot(), but is here for
        # backwards compatibilty with non-draw-order stuff.

        pts = self.get_screen_points()
        self._render(gc, pts)
        return

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
                start = around(start)
                end = around(end)
                gc.move_to(int(start[0]), int(start[1]))
                gc.line_to(int(end[0]), int(end[1]))
                gc.stroke_path()
        gc.restore_state()
        return

    def _post_load(self):
        super(BaseXYPlot, self)._post_load()
        self._update_mappers()
        self.invalidate_draw()
        self._cache_valid = False
        self._screen_cache_valid = False
        return

    def _update_subdivision(self):
        
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

    def _get_hgrid(self):
        for obj in self.underlays+self.overlays:
            if isinstance(obj, PlotGrid) and obj.orientation=="horizontal":
                return obj
        else:
            return None
    
    def _get_vgrid(self):
        for obj in self.underlays+self.overlays:
            if isinstance(obj, PlotGrid) and obj.orientation=="vertical":
                return obj
        else:
            return None

    def _get_x_axis(self):
        for obj in self.underlays+self.overlays:
            if isinstance(obj, PlotAxis) and obj.orientation in ("bottom", "top"):
                return obj
        else:
            return None

    def _get_y_axis(self):
        for obj in self.underlays+self.overlays:
            if isinstance(obj, PlotAxis) and obj.orientation in ("left", "right"):
                return obj
        else:
            return None

    def _get_labels(self):
        labels = []
        for obj in self.underlays+self.overlays:
            if isinstance(obj, PlotLabel):
                labels.append(obj)
        return labels

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _update_mappers(self):
        x_mapper = self.index_mapper
        y_mapper = self.value_mapper
        
        if self.orientation == "v":
            x_mapper, y_mapper = y_mapper, x_mapper
        
        x = self.x
        x2 = self.x2
        y = self.y
        y2 = self.y2
        
        if "left" in self.origin:
            x_mapper.screen_bounds = (x, x2)
        else:
            x_mapper.screen_bounds = (x2, x)
        
        if "bottom" in self.origin:
            y_mapper.screen_bounds = (y, y2)
        else:
            y_mapper.screen_bounds = (y2, y)
        
        self.invalidate_draw()
        self._cache_valid = False
        self._screen_cache_valid = False

    def _bounds_changed(self, old, new):
        super(BaseXYPlot, self)._bounds_changed(old, new)
        self._update_mappers()

    def _bounds_items_changed(self, event):
        super(BaseXYPlot, self)._bounds_items_changed(event)
        self._update_mappers()

##     def _position_changed(self):
##         self._update_mappers()

##     def _position_items_changed(self):
##         self._update_mappers()

    def _orientation_changed(self):
        self._update_mappers()

    def _index_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._either_data_changed, "data_changed", remove=True)
            old.on_trait_change(self._either_metadata_changed, "metadata_changed",
                                remove=True)
        if new is not None:
            new.on_trait_change(self._either_data_changed, "data_changed")
            new.on_trait_change(self._either_metadata_changed, "metadata_changed")
        self._either_data_changed()
        return
    
    def _either_data_changed(self):
        self.invalidate_draw()
        self._cache_valid = False
        self._screen_cache_valid = False
        self.request_redraw()
        return

    def _either_metadata_changed(self):
        # By default, don't respond to metadata change events.
        pass
    
    def _value_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._either_data_changed, "data_changed", remove=True)
            old.on_trait_change(self._either_metadata_changed, "metadata_changed",
                                remove=True)
        if new is not None:
            new.on_trait_change(self._either_data_changed, "data_changed")
            new.on_trait_change(self._either_metadata_changed, "metadata_changed")
        self._either_data_changed()
        return
    
    def _origin_changed(self, old, new):
        # origin switch from left to right or vice versa?
        if old.split()[1] != new.split()[1]:
            xm = self.x_mapper
            xm.low_pos, xm.high_pos = xm.high_pos, xm.low_pos
        # origin switch from top to bottom or vice versa?
        if old.split()[0] != new.split()[0]:
            ym = self.y_mapper
            ym.low_pos, ym.high_pos = ym.high_pos, ym.low_pos

        self.invalidate_draw()
        self._screen_cache_valid = False
        return
    
    def _index_mapper_changed(self, old, new):
        self._either_mapper_changed(self, "index_mapper", old, new)
        if self.orientation == "h":
            self.trait_property_changed("x_mapper", old, new)
        else:
            self.trait_property_changed("y_mapper", old, new)
        return 
    
    def _value_mapper_changed(self, old, new):
        self._either_mapper_changed(self, "value_mapper", old, new)
        if self.orientation == "h":
            self.trait_property_changed("y_mapper", old, new)
        else:
            self.trait_property_changed("x_mapper", old, new)
        return

    def _either_mapper_changed(self, obj, name, old, new):
        if old is not None:
            old.on_trait_change(self._mapper_updated_handler, "updated", remove=True)
        if new is not None:
            new.on_trait_change(self._mapper_updated_handler, "updated")
        self.invalidate_draw()
        self._screen_cache_valid = False
        return
    
    def _mapper_updated_handler(self):
        self._cache_valid = False
        self._screen_cache_valid = False
        self.invalidate_draw()
        self.request_redraw()
        return

    def _bgcolor_changed(self):
        self.invalidate_draw()
    
    def _use_subdivision_changed(self, old, new):
        if new:
            self._set_up_subdivision()
        return
    
    #------------------------------------------------------------------------
    # Persistence
    #------------------------------------------------------------------------

    def __getstate__(self):
        state = super(BaseXYPlot,self).__getstate__()
        for key in ['_cache_valid', '_cached_data_pts', '_screen_cache_valid', 
                    '_cached_screen_pts']:
            if state.has_key(key):
                del state[key]

        return state

    def __setstate__(self, state):
        super(BaseXYPlot, self).__setstate__(state)
        if self.index is not None:
            self.index.on_trait_change(self._either_data_changed, "data_changed")
        if self.value is not None:
            self.value.on_trait_change(self._either_data_changed, "data_changed")

        self.invalidate_draw()
        self._cache_valid = False
        self._screen_cache_valid = False
        self._update_mappers()
        return



# EOF
