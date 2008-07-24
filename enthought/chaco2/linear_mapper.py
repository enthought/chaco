"""
Defines the LinearMapper class, which maps from a 1-D region in data space
into a 1-D output space.
"""

# Major library imports
from numpy import array, ndarray

# Enthought library imports
from enthought.traits.api import Bool, Float

# Local relative imports
from base_1d_mapper import Base1DMapper


class LinearMapper(Base1DMapper):
    """ Maps a 1-D data space to and from screen space by specifying a range in
    data space and a corresponding fixed line in screen space.

    This class concerns itself only with metric and not with orientation. So, to
    "flip" the screen space orientation, simply swap the values for **low_pos**
    and **high_pos**.
    """

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # Number of screen space units per data space unit.
    _scale = Float(1.0)
    # Is the range of the screen space empty?
    _null_screen_range = Bool(False)
    # Is the range of the data space empty?
    _null_data_range = Bool(False)

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def map_screen(self, data_array):
        """ map_screen(data_array) -> screen_array

        Overrides AbstractMapper. Maps values from data space into screen space.
        """
        self._compute_scale()
        if self._null_data_range:
            if isinstance(data_array, (tuple, list, ndarray)):
                return array([self.low_pos] * len(data_array))
            else:
                return array([self.low_pos])
        else:
            return (data_array - self.range.low) * self._scale + self.low_pos

    def map_data(self, screen_val):
        """ map_data(screen_val) -> data_val

        Overrides AbstractMapper. Maps values from screen space into data space.
        """
        self._compute_scale()
        if self._null_screen_range:
            return array([self.range.low])
        else:
            return (screen_val - self.low_pos) / self._scale + self.range.low

    def map_data_array(self, screen_vals):
        """ map_data_array(screen_vals) -> data_vals

        Overrides AbstractMapper. Maps an array of values from screen space
        into data space.
        """
        return self.map_data(screen_vals)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _compute_scale(self):
        if self._cache_valid:
            return

        if self.range is None:
            self._cache_valid = False
            return

        r = self.range
        screen_range = self.high_pos - self.low_pos
        data_range = r.high - r.low
        if screen_range == 0.0:
            self._null_screen_range = True
        else:
            self._null_screen_range = False
        if data_range == 0.0:
            self._null_data_range = True
        else:
            self._scale = screen_range / data_range
            # The screen_range might be small enough that dividing by the
            # data_range causes it to go to 0. Explicitly call bool because
            # _scale might also be a numpy scalar and yield another numpy scalar
            # that the Bool trait rejects.
            self._null_data_range = bool(self._scale == 0.0)

        self._cache_valid = True
        return

# EOF
