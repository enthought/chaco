""" Defines the Base1DMapper class.
"""
# Enthought library imports
from traits.api import Bool, Instance, Float, Property

# Local relative imports
from abstract_mapper import AbstractMapper
from data_range_1d import DataRange1D


class Base1DMapper(AbstractMapper):
    """ Defines an abstract mapping from a 1-D region in input space to a 1-D
    region in output space.
    """

    # The data-space bounds of the mapper.
    range = Instance(DataRange1D)

    # The screen space position of the lower bound of the data space.
    low_pos = Float(0.0)

    # The screen space position of the upper bound of the data space.
    high_pos  = Float(1.0)

    # Convenience property to get low and high positions in one structure.
    # Must be a tuple (low_pos, high_pos).
    screen_bounds = Property

    # Should the mapper stretch the dataspace when its screen space bounds are
    # modified (default), or should it preserve the screen-to-data ratio and
    # resize the data bounds?  If the latter, it will only try to preserve
    # the ratio if both screen and data space extents are non-zero.
    stretch_data = Bool(True)

    # The sign of the mapping: 1 if deltas match sign, -1 if opposite sign
    sign = Property

    # If the subclass uses a cache, _cache_valid is maintained to
    # monitor its status
    _cache_valid = Bool(False)

    # Indicates whether or not the bounds have been set at all, or if they
    # are at their initial default values.
    _bounds_initialized = Bool(False)

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _low_pos_changed(self):
        self._cache_valid = False
        self.updated = True
        return

    def _high_pos_changed(self):
        self._cache_valid = False
        self.updated = True
        return

    def _range_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._range_change_handler, "updated",
                                remove = True)
        if new is not None:
            new.on_trait_change(self._range_change_handler, "updated")

        self._cache_valid = False
        self.updated = new
        return

    def _range_change_handler(self, obj, name, new):
        "Handles the range changing; dynamically attached to our ranges"
        self._cache_valid = False
        self.updated = obj
        return

    def _get_screen_bounds(self):
        return (self.low_pos, self.high_pos)

    def _get_sign(self):
        delta_screen = (self.high_pos - self.low_pos)
        delta_data = (self.range.high-self.range.low)
        if delta_screen == 0 or delta_data == 0:
            return 0
        elif delta_screen/float(delta_data) < 0:
            return -1
        else:
            return 1

    def _set_screen_bounds(self, new_bounds):
        if new_bounds[0] == self.low_pos and new_bounds[1] == self.high_pos:
            return
        if not self.stretch_data and self.range is not None and self._bounds_initialized:
            rangelow = self.range.low
            rangehigh = self.range.high
            d_data = rangehigh - rangelow
            d_screen = self.high_pos - self.low_pos
            if d_data != 0 and d_screen != 0:
                new_data_extent = d_data / d_screen * abs(new_bounds[1] - new_bounds[0])
                self.range.set_bounds(rangelow, rangelow + new_data_extent)
        self.set(low_pos = new_bounds[0], trait_change_notify=False)
        self.set(high_pos = new_bounds[1], trait_change_notify=False)
        self._cache_valid = False
        self._bounds_initialized = True
        self.updated = True
        return

