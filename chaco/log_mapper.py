""" Defines the LogMapper and InvalidDataRangeException classes.
"""
# Major library imports
from numpy import array, isnan, log, log10, exp, zeros, sometrue,\
    floor, ceil, ndarray
import numpy as np

# Enthought library imports
from traits.api import Bool, Float

#Local relative imports
from .base_1d_mapper import Base1DMapper


LOG_MINIMUM = 0.0

class InvalidDataRangeException(Exception):
    pass

class LogMapper(Base1DMapper):
    """ Defines a 1-D logarithmic scale mapping from a 1-D region in input
    space to a 1-D region in output space.
    """

    # The value to map when asked to map values <= LOG_MINIMUM to screen space.
    fill_value = Float(1.0)

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    _inter_scale = Float(0.0)
    _inter_offset = Float(0.0)
    _screen_scale = Float(0.0)
    _screen_offset = Float(0.0)
    _null_screen_range = Bool(False)
    _null_data_range = Bool(False)

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def map_screen(self, data_array):
        """ map_screen(data_array) -> screen_array

        Overrides AbstractMapper. Maps values from data space to screen space.
        """
        # Ensure that data_array is actually an array.
        if not isinstance(data_array, ndarray):
            data_array = array(data_array, ndmin=1)
        # First convert to a [0,1] space, then to the screen space.
        if not self._cache_valid:
            self._compute_scale()
        if self._inter_scale == 0.0:
            intermediate = data_array*0.0
        else:
            try:
                with np.errstate(invalid='ignore'):
                    mask = (data_array <= LOG_MINIMUM) | isnan(data_array)
                if sometrue(mask):
                    data_array = array(data_array, copy=True, ndmin=1)
                    data_array[mask] = self.fill_value
                intermediate = (log(data_array) - self._inter_offset)/self._inter_scale
            except ValueError:
                intermediate = zeros(len(data_array))

        result = intermediate * self._screen_scale + self._screen_offset
        return result

    def map_data(self, screen_val):
        """ map_data(screen_val) -> data_val

        Overrides Abstract Mapper. Maps values from screen space into data space.
        """
        if not self._cache_valid:
            self._compute_scale()
        if self._null_screen_range or self._null_data_range:
            return array([self.range.low])
        #First convert to a [0,1] space, then to the data space
        intermediate = (screen_val-self._screen_offset)/self._screen_scale
        return exp(self._inter_scale*intermediate + self._inter_offset)

    def map_data_array(self, screen_vals):
        return self.map_data(screen_vals)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _get_safe_scale(self, range):
        orig_low = range.low
        orig_high = range.high
        if orig_low < LOG_MINIMUM:
            low = LOG_MINIMUM
        else:
            low = orig_low

        if orig_high < LOG_MINIMUM:
            high = LOG_MINIMUM
        else:
            high = orig_high

        if low == high:
            if low == LOG_MINIMUM:
                low = 1.0
                high = 10.0
            else:
                log_val = log10(low)
                low = pow(10, floor(log_val))
                if ceil(log_val) != floor(log_val):
                    high = pow(10, ceil(log_val))
                else:
                    high = pow(10, ceil(log_val) + 1)

        return (low, high)

    def _compute_scale(self):
        if self._cache_valid:
            return

        if self.range is None:
            self._cache_valid = False
            return

        screen_range = self.high_pos - self.low_pos
        if screen_range == 0.0:
            self._null_screen_range = True

        # Get dataspace low and high from the range that are "safe" for a
        # logarithmic mapper, i.e. constrained to be between LOG_MINIMUM and inf.
        low, high = self._get_safe_scale(self.range)
        if high - low == 0:
            self._null_data_range = True
        else:
            if low == LOG_MINIMUM:
                self._inter_scale = log(high)
                self._inter_offset = 0.0
            else:
                self._inter_scale = log(high)-log(low)
                self._inter_offset = log(low)
            self._screen_scale = screen_range
            self._screen_offset = self.low_pos

        self._cache_valid = True
        return

# EOF
