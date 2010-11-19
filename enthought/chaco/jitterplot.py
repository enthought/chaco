
from itertools import izip
from math import sqrt
import numpy as np

from enthought.enable.api import black_color_trait, MarkerTrait
from enthought.traits.api import (Any, Bool, Callable, Enum, Float,
        Instance, Int, Property, Str, Trait, on_trait_change)

from abstract_plot_renderer import AbstractPlotRenderer
from abstract_mapper import AbstractMapper
from array_data_source import ArrayDataSource
from base import reverse_map_1d
from scatterplot import render_markers


class JitterPlot(AbstractPlotRenderer):
    """A renderer for a jitter plot, a 1D plot with some width in the 
    dimension perpendicular to the primary axis.  Useful for understanding
    dense collections of points.
    """

    # The data source of values
    index = Instance(ArrayDataSource)

    # The single mapper that this plot uses
    mapper = Instance(AbstractMapper)

    # Just an alias for "mapper"
    index_mapper = Property(lambda obj,attr: getattr(obj, "mapper"),
                            lambda obj,attr,val: setattr(obj, "mapper", val))

    x_mapper = Property()
    y_mapper = Property()

    orientation = Enum("h", "v")

    # The size, in pixels, of the area over which to spread the data points
    # along the dimension orthogonal to the index direction.
    jitter_width = Int(50)

    # How the plot should center itself along the orthogonal dimension if the
    # component's width is greater than the jitter_width
    #align = Enum("center", "left", "right", "top", "bottom")

    # The type of marker to use.  This is a mapped trait using strings as the
    # keys.
    marker = MarkerTrait

    # The pixel size of the marker, not including the thickness of the outline.
    marker_size = Float(4.0)

    # The CompiledPath to use if **marker** is set to "custom". This attribute
    # must be a compiled path for the Kiva context onto which this plot will
    # be rendered.  Usually, importing enthought.kiva.GraphicsContext will do
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

    # Override the base class default for **origin**, which specifies corners.
    # Since this is a 1D plot, it only makes sense to have the origin at the
    # edges.
    origin = Enum("bottom", "top", "left", "right")

    #------------------------------------------------------------------------
    # Built-in selection handling
    #------------------------------------------------------------------------

    # The name of the metadata attribute to look for on the datasource for
    # determine which points are selected and which are not.  The metadata
    # value returned should be a *list* of numpy arrays suitable for masking
    # the values returned by index.get_data().
    selection_metadata_name = Str("selections")

    # The color to use to render selected points
    selected_color = black_color_trait

    # Alpha value to apply to points that are not in the set of "selected"
    # points
    unselected_alpha = Float(0.3)
    unselected_line_width = Float(0.0)

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    _cache_valid = Bool(False)

    _cached_data_pts = Any()
    _cached_data_pts_sorted = Any()
    _cached_data_argsort = Any()
    
    _screen_cache_valid = Bool(False)
    _cached_screen_pts = Any()
    _cached_screen_map = Any()  # dict mapping index to value points

    # The random number seed used to generate the jitter.  We store this
    # so that the jittering is stable as the data is replotted.
    _jitter_seed = Trait(None, None, Int)
    
    #------------------------------------------------------------------------
    # Component/AbstractPlotRenderer interface
    #------------------------------------------------------------------------

    def map_screen(self, data_array):
        """ Maps an array of data points into screen space and returns it as
        an array.  Although the orthogonal (non-scaled) axis does not have
        a mapper, this method returns the scattered values in that dimension.

        Implements the AbstractPlotRenderer interface.
        """
        if len(data_array) == 0:
            return np.zeros(0)

        if self._screen_cache_valid:
            sm = self._cached_screen_map
            new_x = [x for x in data_array if x not in sm]
            if new_x:
                new_y = self._make_jitter_vals(len(new_x))
                sm.update(dict((new_x[i], new_y[i]) for i in range(len(new_x))))
            xs = self.mapper.map_screen(data_array)
            ys = [sm[x] for x in xs]
        
        else:
            if self._jitter_seed is None:
                self._set_seed(data_array)
            xs = self.mapper.map_screen(data_array)
            ys = self._make_jitter_vals(len(data_array))

        if self.orientation == "h":
            return np.vstack((xs, ys)).T
        else:
            return np.vstack((ys, xs)).T

    def _make_jitter_vals(self, numpts):
        vals = np.random.uniform(0, self.jitter_width, numpts)
        if self.orientation == "h":
            ymin = self.y
            height = self.height
            vals += ymin + height/2 - self.jitter_width/2
        else:
            xmin = self.x
            width = self.width
            vals += xmin + width/2 - self.jitter_width/2
        return vals

    def map_data(self, screen_pt):
        """ Maps a screen space point into the index space of the plot.
        """
        x, y = screen_pt
        if self.orientation == "v":
            x, y = y, x
        return self.mapper.map_data(x)

    def map_index(self, screen_pt, threshold=2.0, outside_returns_none=True, \
                  index_only = True):
        """ Maps a screen space point to an index into the plot's index array(s).
        """
        screen_points = self._cached_screen_pts

        if len(screen_points) == 0:
            return None

        data_pt = self.map_data(screen_pt)
        if ((data_pt < self.mapper.range.low) or \
            (data_pt > self.mapper.range.high)) and outside_returns_none:
            return None

        if self._cached_data_pts_sorted is None:
            self._cached_data_argsort = np.argsort(self._cached_data_pts)
            self._cached_data_pts_sorted = self._cached_data_pts[self._cached_data_argsort]

        data = self._cached_data_pts_sorted
        try:
            ndx = reverse_map_1d(data, data_pt, "ascending")
        except IndexError, e:
            if outside_returns_none:
                return None
            else:
                if data_pt < data[0]:
                    return 0
                else:
                    return len(data) - 1

        orig_ndx = self._cached_data_argsort[ndx]

        if threshold == 0.0:
            return orig_ndx

        sx, sy = screen_points[orig_ndx]
        if sqrt((screen_pt[0] - sx)**2 + (screen_pt[1] - sy)**2) <= threshold:
            return orig_ndx
        else:
            return None
        

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        pts = self.get_screen_points()
        self._render(gc, pts)

    
    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def get_screen_points(self):
        if not self._screen_cache_valid:
            self._gather_points()
            pts = self.map_screen(self._cached_data_pts)
            if self.orientation == "h":
                self._cached_screen_map = dict((x,y) for x,y in izip(pts[:,0], pts[:,1]))
            else:
                self._cached_screen_map = dict((y,x) for x,y in izip(pts[:,0], pts[:,1]))
            self._cached_screen_pts = pts
            self._screen_cache_valid = True
            self._cached_data_pts_sorted = None
            self._cached_data_argsort = None
        return self._cached_screen_pts

    def _gather_points(self):
        if self._cache_valid:
            return

        if not self.index:
            return

        index, index_mask = self.index.get_data_mask()
        if len(index) == 0:
            self._cached_data_pts = []
            self._cache_valid = True
            return

        # For the jitter plot, we do not mask or compress the data in any
        # way, because if we do, we have no way of transforming from screen
        # points back into dataspace.  (Tools will be able to find an index
        # into the screen points array, but won't be able to go from that
        # back into the original data points array.)

        #index_range_mask = self.mapper.range.mask_data(index)
        #self._cached_data_pts = np.compress(index_mask & index_range_mask, index)
        self._cached_data_pts = index
        self._cache_valid = True
        self._cached_screen_pts = None
        self._screen_cache_valid = False

    def _render(self, gc, pts):
        gc.save_state()
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        try:
            if not self.index:
                gc.restore_state()
                return
            name = self.selection_metadata_name
            md = self.index.metadata
            if name in md and md[name] is not None and len(md[name]) > 0:
                # FIXME: when will we ever encounter multiple masks in the list?
                sel_mask = md[name][0]
                sel_pts = np.compress(sel_mask, pts, axis=0)
                unsel_pts = np.compress(~sel_mask, pts, axis=0)
                color = list(self.color_)
                color[3] *= self.unselected_alpha
                outline_color = list(self.outline_color_)
                outline_color[3] *= self.unselected_alpha
                if unsel_pts.size > 0:
                    self.render_markers_func(gc, unsel_pts, self.marker, self.marker_size,
                            tuple(color), self.unselected_line_width, tuple(outline_color),
                            self.custom_symbol)
                if sel_pts.size > 0:
                    self.render_markers_func(gc, sel_pts, self.marker, self.marker_size,
                            self.selected_color_, self.line_width, self.outline_color_,
                            self.custom_symbol)
            else:
                self.render_markers_func(gc, pts, self.marker, self.marker_size,
                        self.color_, self.line_width, self.outline_color_,
                        self.custom_symbol)
        finally:
            gc.restore_state()

    def _set_seed(self, data_array):
        """ Sets the internal random seed based on some input data """
        if isinstance(data_array, np.ndarray):
            seed = np.random.seed(data_array.size)
        else:
            seed = np.random.seed(map(int, data_array[:100]))

        self._jitter_seed = seed
        
    @on_trait_change("index.data_changed")
    def _invalidate(self):
        self._cache_valid = False
        self._screen_cache_valid = False

    @on_trait_change("mapper.updated")
    def _invalidate_screen(self):
        self._screen_cache_valid = False

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _get_x_mapper(self):
        if self.orientation == "h":
            return self.mapper
        else:
            return None

    def _set_x_mapper(self, val):
        if self.orientation == "h":
            self.mapper = val
        else:
            raise ValueError("x_mapper is not defined for a vertical jitter plot")

    def _get_y_mapper(self):
        if self.orientation == "v":
            return self.mapper
        else:
            return None

    def _set_y_mapper(self, val):
        if self.orientation == "v":
            self.mapper = val
        else:
            raise ValueError("y_mapper is not defined for a horizontal jitter plot")

    def _update_mappers(self):
        mapper = self.mapper
        if mapper is None:
            return
        
        x = self.x
        x2 = self.x2
        y = self.y
        y2 = self.y2

        if "left" in self.origin:
            mapper.screen_bounds = (x, x2)
        elif "right" in self.origin:
            mapper.screen_bounds = (x2, x)
        elif "bottom" in self.origin:
            mapper.screen_bounds = (y, y2)
        elif "top" in self.origin:
            mapper.screen_bounds = (y2, y)
        
        self.invalidate_draw()
        self._cache_valid = False
        self._screen_cache_valid = False

    def _bounds_changed(self, old, new):
        super(JitterPlot, self)._bounds_changed(old, new)
        self._update_mappers()

    def _bounds_items_changed(self, event):
        super(JitterPlot, self)._bounds_items_changed(event)
        self._update_mappers()

    def _orientation_changed(self):
        self._update_mappers()

