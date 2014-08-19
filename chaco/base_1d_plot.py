"""
Abstract base class for 1-D plots which only use one axis
"""

from __future__ import absolute_import

# Standard library imports
from numpy import argsort, asarray

# Enthought library imports
from traits.api import (Any, Bool, Enum, Instance, Property, cached_property,
                        on_trait_change)

# local imports
from .abstract_plot_renderer import AbstractPlotRenderer
from .abstract_mapper import AbstractMapper
from .array_data_source import ArrayDataSource
from .base import reverse_map_1d


class Base1DPlot(AbstractPlotRenderer):
    """ Base class for one-dimensional plots

    This class provides a base for plots such as jitter plots, color bars,
    single-axis scatter plots, and geophysical horizon and tops plots.

    """

    #: The data source of values
    index = Instance(ArrayDataSource)

    #: Screen mapper for index data.
    index_mapper = Instance(AbstractMapper)

    #: Corresponds to either **index_mapper** or None, depending on
    #: the orientation of the plot.
    x_mapper = Property(depends_on='orientation')

    #: Corresponds to either **index_mapper** or None, depending on
    #: the orientation of the plot.
    y_mapper = Property(depends_on='orientation')

    #: The orientation of the index axis.
    orientation = Enum('v', 'h')

    #: Should the plot go left-to-right or bottom-to-top (normal) or the reverse?
    direction = Enum('normal', 'flipped')

    #: Faux origin for the axes and other objects to look at
    origin = Property(
        Enum('bottom left', 'top left', 'bottom right', 'top right'),
        depends_on=['orientation', 'direction']
    )

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    #: flag whether the data cache is valid
    _cache_valid = Bool(False)

    #: cache of the index values in data space
    _cached_data = Any()

    #: cache of the sorted index values in data space
    _cached_data_pts_sorted = Any()

    #: cache of the sorted indices of the index values
    _cached_data_argsort = Any()

    #: flag whether the screen coordinates are valid
    _screen_cache_valid = Bool(False)

    #: cache holding the screen coordinates of the index values
    _cached_screen_pts = Any()

    #------------------------------------------------------------------------
    # AbstractPlotRenderer interface
    #------------------------------------------------------------------------

    def map_screen(self, data_array):
        """ Maps a 1D array of data points into screen space and returns it as
        a 1D array.

        Parameters
        ----------

        data_array : 1D array
            An array of data-space values to be mapped to screen coordinates.

        Returns
        -------

        screen_array : 1D array
            An array of points in screen space, either x-values (if
            orientation is 'h') or y-values (if orientation is 'v').

        Notes
        -----

        Returning a 1D array is experimental, and may break some tools and
        overlays.  If needs be we can refactor so that it returns a 2D array.

        """
        # data_array is 1D array of length N
        if len(data_array) == 0:
            return []
        return asarray(self.index_mapper.map_screen(data_array))

    def map_data(self, screen_pts):
        """ Maps 2D screen space points into the 1D index space of the plot.

        Parameters
        ----------

        screen_pts : tuple of x-array, y-array
            2 arrays (or values) screen space coordinates.

        Returns
        -------

        data_array : 1D array
            An array of points in data space corresponding to the screen-space
            points.

        """
        x, y = screen_pts
        if self.orientation == "v":
            return asarray(self.index_mapper.map_data(y))
        else:
            return asarray(self.index_mapper.map_data(x))

    def map_index(self, screen_pt, threshold=2.0, outside_returns_none=True,
                  index_only=True):
        """ Maps a screen space point to an index into the plot's index array.

        Parameters
        ----------

        screen_pts: tuple of x-array, y-array
            2 arrays (or values) screen space coordinates.
        threshold : float
            Optional screen-space distance allowed between *screen_pt* and the
            plot; if non-zero, then a *screen_pt* within this distance is
            mapped to the neared plot index. (This feature is useful for sparse
            data.)
        outside_returns_none : Boolean
            If True, then if *screen_pt* is outside the range of the data, the
            method returns None. If False, it returns the nearest end index in
            such a case.
        index_only : Boolean
            This is included for compatibity with the base class, but is
            ignored, as it is always true for 1D plots.

        Returns
        -------

        index : int
            An index into the index array. If the input point cannot be mapped
            to an index, then None is returned.

            If *screen_pt* corresponds to multiple indices, then only the first
            index is returned.

        """
        data_pt = self.map_data(screen_pt)

        if ((data_pt < self.index_mapper.range.low) or \
                (data_pt > self.index_mapper.range.high)) and \
                outside_returns_none:
            return None

        if self._cached_data_pts_sorted is None:
            self._cached_data_argsort = argsort(self._cached_data)
            self._cached_data_pts_sorted = self._cached_data[self._cached_data_argsort]

        # XXX better to just use argmin(abs(data - data_pt))?

        data = self._cached_data_pts_sorted
        try:
            ndx = reverse_map_1d(data, data_pt, "ascending")
        except IndexError:
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

        screen_points = self._cached_screen_pts
        x = screen_points[orig_ndx]
        if self.orientation == 'v':
            x0 = screen_pt[1]
        else:
            x0 = screen_pt[0]

        if abs(x - x0) <= threshold:
            return orig_ndx
        else:
            return None

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _compute_screen_coord(self):
        """ Compute the screen coordinates of the index values """
        if not self._screen_cache_valid:
            self._gather_points()
            pts = self.map_screen(self._cached_data)
            self._cached_screen_pts = pts
            self._screen_cache_valid = True
            self._cached_data_pts_sorted = None
            self._cached_data_argsort = None
        return self._cached_screen_pts

    def _gather_points(self):
        """ Ensure that data cache is valid """
        if self._cache_valid:
            return
        if not self.index:
            return

        index, index_mask = self.index.get_data_mask()
        if len(index) == 0:
            self._cached_data = []
            self._cache_valid = True
            return

        self._cached_data = index
        self._cache_valid = True
        self._cached_screen_points = None
        self._screen_cached_valid = False

    def _update_mappers(self):
        """ Update the mapper when the bounds, orientation or direction change
        """
        mapper = self.index_mapper
        if mapper is None:
            return

        x = self.x
        x2 = self.x2
        y = self.y
        y2 = self.y2

        if self.orientation == 'h':
            if self.direction == 'normal':
                mapper.screen_bounds = (x, x2)
            elif self.direction == 'flipped':
                mapper.screen_bounds = (x2, x)
        elif self.orientation == 'v':
            if self.direction == 'normal':
                mapper.screen_bounds = (y, y2)
            elif self.direction == 'flipped':
                mapper.screen_bounds = (y2, y)

        self.invalidate_draw()
        self._cache_valid = False
        self._screen_cache_valid = False

    #------------------------------------------------------------------------
    # Property setters and getters
    #------------------------------------------------------------------------

    @cached_property
    def _get_x_mapper(self):
        if self.orientation == "h":
            return self.index_mapper
        else:
            return None

    @cached_property
    def _get_y_mapper(self):
        if self.orientation == "h":
            return None
        else:
            return self.index_mapper

    @cached_property
    def _get_origin(self):
        if self.orientation == 'h':
            if self.direction == 'normal':
                return 'bottom left'
            else:
                return 'bottom right'
        else:
            if self.direction == 'normal':
                return 'bottom left'
            else:
                return 'top left'

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    @on_trait_change("index.data_changed")
    def _invalidate(self):
        self._cache_valid = False
        self._screen_cache_valid = False

    @on_trait_change("index_mapper.updated")
    def _invalidate_screen(self):
        self._screen_cache_valid = False

    def _bounds_changed(self, old, new):
        super(Base1DPlot, self)._bounds_changed(old, new)
        self._update_mappers()

    def _bounds_items_changed(self, event):
        super(Base1DPlot, self)._bounds_items_changed(event)
        self._update_mappers()

    def _position_changed(self, old, new):
        super(Base1DPlot, self)._position_changed(old, new)
        self._update_mappers()

    def _position_items_changed(self, event):
        super(Base1DPlot, self)._position_items_changed(event)
        self._update_mappers()

    def _updated_changed_for_index_mapper(self):
        self._update_mappers()

    def _orientation_changed(self):
        self._update_mappers()

    def _direction_changed(self):
        self._update_mappers()
