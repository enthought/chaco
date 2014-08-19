
from __future__ import absolute_import

from itertools import izip
from math import sqrt
import numpy as np

from enable.api import black_color_trait, MarkerTrait
from traits.api import (Any, Bool, Callable, Enum, Float,
        Instance, Int, Property, Str, Trait, on_trait_change)

from .scatterplot_1d import ScatterPlot1D
from .abstract_mapper import AbstractMapper
from .array_data_source import ArrayDataSource
from .base import reverse_map_1d
from .scatterplot import render_markers


class JitterPlot(ScatterPlot1D):
    """A renderer for a jitter plot, a 1D plot with some width in the
    dimension perpendicular to the primary axis.  Useful for understanding
    dense collections of points.
    """

    # The size, in pixels, of the area over which to spread the data points
    # along the dimension orthogonal to the index direction.
    jitter_width = Int(50)

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

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
            xs = self.index_mapper.map_screen(data_array)
            ys = [sm[x] for x in xs]

        else:
            if self._jitter_seed is None:
                self._set_seed(data_array)
            xs = self.index_mapper.map_screen(data_array)
            ys = self._make_jitter_vals(len(data_array))

        if self.orientation == "h":
            return np.vstack((xs, ys)).T
        else:
            return np.vstack((ys, xs)).T

    def _make_jitter_vals(self, numpts):
        vals = np.random.uniform(0, self.jitter_width, numpts)
        vals += self._marker_position
        return vals

    def map_index(self, screen_pt, threshold=2.0, outside_returns_none=True, \
                  index_only = True):
        """ Maps a screen space point to an index into the plot's index array(s).
        """
        screen_points = self._cached_screen_pts

        if len(screen_points) == 0:
            return None

        data_pt = self.map_data(screen_pt)
        if ((data_pt < self.index_mapper.range.low) or \
            (data_pt > self.index_mapper.range.high)) and outside_returns_none:
            return None

        if self._cached_data_pts_sorted is None:
            self._cached_data_argsort = np.argsort(self._cached_data)
            self._cached_data_pts_sorted = self._cached_data[self._cached_data_argsort]

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
            pts = self.map_screen(self._cached_data)
            if self.orientation == "h":
                self._cached_screen_map = dict((x,y) for x,y in izip(pts[:,0], pts[:,1]))
            else:
                self._cached_screen_map = dict((y,x) for x,y in izip(pts[:,0], pts[:,1]))
            self._cached_screen_pts = pts
            self._screen_cache_valid = True
            self._cached_data_pts_sorted = None
            self._cached_data_argsort = None
        return self._cached_screen_pts

    def _set_seed(self, data_array):
        """ Sets the internal random seed based on some input data """
        if isinstance(data_array, np.ndarray):
            seed = np.random.seed(data_array.size)
        else:
            seed = np.random.seed(map(int, data_array[:100]))

        self._jitter_seed = seed

    def _get_marker_position(self):
        x, y = self.position
        w, h = self.bounds

        if self.orientation == 'v':
            y, h = x, w

        if self.alignment == 'center':
            position = y + h/2.0 - self.jitter_width/2.0
        elif self.alignment in ['left', 'bottom']:
            position = y
        elif self.alignment in ['right', 'top']:
            position = y + h - self.jitter_width/2.0

        position += self.marker_offset
        return position
