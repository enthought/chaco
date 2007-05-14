"""
Defines ScalarDataSeries.
"""

from numpy import argmin, argmax, array, ones, UInt8

from enthought.traits.api import Any, Constant, Enum, Int, String, Tuple

# Chaco imports
from base import NumericalSequenceTrait, reverse_map_1d, SortOrderTrait
from dataseries import AbstractDataSeries


class ScalarDataSeries(AbstractDataSeries):
    """
    DataSeries representing a single, continuous array of numerical data.
    """
    
    # --- DataSource traits ----------------------------------------------
    
    # Redefine the index dimension from the parent class.
    index_dimension = Constant('scalar')
    
    # Redefine the value dimension from the parent class
    value_dimension = Constant('scalar')
    
    # The sort order of the data.
    # This is a specialized optimization for 1D arrays, but it's an important
    # one that's used everywhere.
    sort_order = SortOrderTrait

    # Can guarantee a single index for any point within the value range.
    rmap_accuracy = "precise"

    # --- Private traits -------------------------------------------------
    
    # The data array itself
    _data = NumericalSequenceTrait
    
    # caches the value of min and max as long as data doesn't change
    _cached_bounds = Tuple
    
    # Non-filters should never actually have a mask, but if we keep
    # getting asked to return one, then we might as well cache it.
    _cached_mask = Any
    
    # The index of the (first) minimum value in self._data
    _min_index = Int
    
    # The index of hte (first) maximum value in self._data
    _max_index = Int
    
    # --- Public methods -------------------------------------------------
    
    def __init__(self, data=array([]), sort_order="none"):
        AbstractDataSeries.__init__(self)
        self._data = data
        self.sort_order = sort_order
        self._compute_bounds()
    
    def set_data(self, newdata):
        self._data = newdata
        self._compute_bounds()
        return
    
    # --- DataSource interface -------------------------------------------
    
    def get_data(self):
        if self._data is not None:
            return self._data
        else:
            return 0.0
    
    def get_data_mask(self):
        if self._cached_mask is None:
            self._cached_mask = ones(len(self._data), UInt8)
        return self._cached_mask
    
    def is_masked(self):
        return False
    
    def get_size(self):
        if self._data is not None:
            return len(self._data)
        else:
            return 0
    
    def get_bounds(self):
        if self._cached_bounds == ():
            self._compute_bounds()
        return self._cached_bounds

    def reverse_map(self, pt, index=0, outside_returns_none=True):
        if self.sort_order == "none":
            raise NotImplementedError
        
        # index is ignored for dataseries with 1-dimensional indices
        minval, maxval = self._cached_bounds
        if (pt < minval):
            if outside_returns_none:
                return None
            else:
                return self._min_index
        elif (pt > maxval):
            if outside_returns_none:
                return None
            else:
                return self._max_index
        else:
            return reverse_map_1d(self._data, pt, self.sort_order)


    # --- Private methods ------------------------------------------------

    def _compute_bounds(self):
        """
        Computes the minimum and maximum values of self._data.
        """
        # TODO: as an optimization, perhaps create and cache a sorted
        #       version of the dataset?
        if len(self._data) == 0:
            self._min_index = 0
            self._max_index = 0
            self._cached_bounds = (0.0, 0.0)
        elif len(self._data) == 1:
            self._min_index = 0
            self._max_index = 0
            self._cached_bounds = (self._data[0], self._data[0])
        else:
            if self.sort_order == "ascending":
                self._min_index = 0
                self._max_index = -1
            elif self.sort_order == "descending":
                self._min_index = -1
                self._max_index = 0
            else:
                self._min_index = argmin(self._data)
                self._max_index = argmax(self._data)
            self._cached_bounds = (self._data[self._min_index],
                                   self._data[self._max_index])
        return

# EOF
