
from traits.api import Enum, Range, Bool, Array

from chaco.base_projection_plot import BaseProjectionPlot

class SequenceProjectionPlot(BaseProjectionPlot):
    """ A projection plot which plots the data source as a sequence of points
    """

    #------------------------------------------------------------------------
    # Appearance-related traits
    #------------------------------------------------------------------------

    # The orientation of the index axis.
    orientation = Enum("h", "v")

    # Overall alpha value of the image. Ranges from 0.0 for transparent to 1.0
    alpha = Range(0.0, 1.0, 1.0)

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # Are the cache traits valid? If False, new ones need to be compute.
    _cache_valid = Bool(False)

    # Cached array of (x,y) data-space points; regardless of self.orientation,
    # these points are always stored as (index_pt, value_pt).
    _cached_data_pts = Array

    # Cached array of (x,y) screen-space points.
    _cached_screen_pts = Array

    # Does **_cached_screen_pts** contain the screen-space coordinates
    # of the points currently in **_cached_data_pts**?
    _screen_cache_valid = Bool(False)

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

    #------------------------------------------------------------------------
    # PlotComponent interface
    #------------------------------------------------------------------------

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        """ Draws the 'plot' layer.
        """
        print 'draw plot'
        self._draw_component(gc, view_bounds, mode)
        return

    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        print 'draw component'
        # This method should be folded into self._draw_plot(), but is here for
        # backwards compatibilty with non-draw-order stuff.

        pts = self.get_screen_points()
        self._render(gc, pts)
        return

    def _draw_default_axes(self, gc):
        return
        if not self.origin_axis_visible:
            return

        with gc:
            gc.set_stroke_color(self.origin_axis_color_)
            gc.set_line_width(self.origin_axis_width)
            gc.set_line_dash(None)

            for range in (self.x_mapper.range, self.y_mapper.range):
                if (range.low < 0) and (range.high > 0):
                    if range == self.x_mapper.range:
                        dual = self.y_mapper.range
                        data_pts = array([[0.0,dual.low], [0.0, dual.high]])
                    else:
                        dual = self.x_mapper.range
                        data_pts = array([[dual.low,0.0], [dual.high,0.0]])
                    start,end = self.map_screen(data_pts)
                    start = around(start)
                    end = around(end)
                    gc.move_to(int(start[0]), int(start[1]))
                    gc.line_to(int(end[0]), int(end[1]))
                    gc.stroke_path()
        return

    def _post_load(self):
        super(SequenceProjectionPlot, self)._post_load()
        self._update_mappers()
        self.invalidate_draw()
        self._cache_valid = False
        self._screen_cache_valid = False
        return

    def _update_subdivision(self):

        return

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _update_mappers(self):
        x_mapper = self.x_mapper
        y_mapper = self.y_mapper

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
        super(SequenceProjectionPlot, self)._bounds_changed(old, new)
        self._update_mappers()

    def _bounds_items_changed(self, event):
        super(SequenceProjectionPlot, self)._bounds_items_changed(event)
        self._update_mappers()

    def _position_changed(self):
        self._update_mappers()

    def _position_items_changed(self):
        self._update_mappers()

    def _orientation_changed(self):
        self._update_mappers()
