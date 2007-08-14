""" Defines the Base1DMapper class.
"""
# Major library imports
from numpy import array

# Enthought library imports
from enthought.traits.api import Event, Instance, HasTraits, Float, false, Property

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

    # If the subclass uses a cache, _cache_valid is maintained to 
    # monitor its status
    _cache_valid = false


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

    def _set_screen_bounds(self, new_bounds):
        self.set(low_pos = new_bounds[0], trait_change_notify=False)
        self.set(high_pos = new_bounds[1], trait_change_notify=False)
        self._cache_valid = False
        self.updated = True
        return

# EOF
