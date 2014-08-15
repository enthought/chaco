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
    """ A color bar for a color-mapped plot.
    """

    # The data source of values
    index = Instance(ArrayDataSource)

    #: Screen mapper for index data.
    index_mapper = Instance(AbstractMapper)

    #: Corresponds to either **index_mapper** or None, depending on
    #: the orientation of the plot.
    x_mapper = Property(depends_on='orientation')

    #: Corresponds to either **index_mapper** or None, depending on
    #: the orientation of the plot.
    y_mapper = Property(depends_on='orientation')

    # The orientation of the index axis.
    orientation = Enum('v', 'h')

    # Should the plot go left-to-right or bottom-to-top (normal) or the reverse?
    direction = Enum('normal', 'flipped')

    # Faux origin for the axis to look at
    origin = Property(
        Enum('bottom left', 'top left', 'bottom right', 'top right'),
        depends_on=['orientation', 'direction']
    )

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    _cache_valid = Bool(False)

    _cached_data = Any()
    _cached_data_pts_sorted = Any()
    _cached_data_argsort = Any()

    _screen_cache_valid = Bool(False)
    _cached_screen_pts = Any()

    #------------------------------------------------------------------------
    # AbstractPlotRenderer interface
    #------------------------------------------------------------------------

    def map_screen(self, data_pts):
        """ Maps a 1D array of data points into screen space and returns it as
        a 1D array.

        """
        # data_pts is array of length N
        if len(data_pts) == 0:
            return []
        return asarray(self.index_mapper.map_screen(data_pts))

    def map_data(self, screen_pts):
        """ Maps 2D screen space points into the 1D "index" space of the plot.

        """
        x, y = screen_pts
        if self.orientation == "v":
            return asarray(self.index_mapper.map_data(y))
        else:
            return asarray(self.index_mapper.map_data(x))

    def map_index(self, screen_pt, threshold=2.0, outside_returns_none=True,
                  index_only = True):
        """ Maps a screen space point to an index into the plot's index array.

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
        if not self._screen_cache_valid:
            self._gather_points()
            pts = self.map_screen(self._cached_data)
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
            self._cached_data = []
            self._cache_valid = True
            return

        self._cached_data = index
        self._cache_valid = True
        self._cached_screen_points = None
        self._screen_cached_valid = False

    def _update_mappers(self):
        mapper = self.index_mapper
        if mapper is None:
            return

        x = self.x
        x2 = self.x2
        y = self.y
        y2 = self.y2

        if "left" in self.origin and self.orientation == 'h':
            mapper.screen_bounds = (x, x2)
        elif "right" in self.origin and self.orientation == 'h':
            mapper.screen_bounds = (x2, x)
        elif "bottom" in self.origin  and self.orientation == 'v':
            mapper.screen_bounds = (y, y2)
        elif "top" in self.origin  and self.orientation == 'v':
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

    def _orientation_changed(self):
        self._update_mappers()
