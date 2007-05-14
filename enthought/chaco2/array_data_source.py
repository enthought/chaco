""" Defines ArrayDataSource """

# Major library imports
from numpy import argmin, argmax, array, ones, nanargmin, nanargmax

# Enthought library imports
from enthought.traits.api import Any, Constant, Enum, Int, String, Tuple

# Chaco imports
from base import NumericalSequenceTrait, reverse_map_1d, SortOrderTrait
from abstract_data_source import AbstractDataSource


class ArrayDataSource(AbstractDataSource):
    """
    DataSource representing a single, continuous array of numerical data.
    Does not listen to the array for value changes;  If such behavior is
    desired, it is pretty straightforward to create a subclass that hooks
    up the appropriate listeners.
    """
    
    #------------------------------------------------------------------------
    # AbstractDataSource traits
    #------------------------------------------------------------------------
    
    # Redefine the index dimension from the parent class.
    index_dimension = Constant('scalar')
    
    # Redefine the value dimension from the parent class
    value_dimension = Constant('scalar')
    
    # The sort order of the data.
    # This is a specialized optimization for 1D arrays, but it's an important
    # one that's used everywhere.
    sort_order = SortOrderTrait

    
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # The data array itself
    _data = NumericalSequenceTrait
    
    # caches the value of min and max as long as data doesn't change
    _cached_bounds = Tuple
    
    # Non-filters should never actually have a mask, but if we keep
    # getting asked to return one, then we might as well cache it.
    _cached_mask = Any
    
    # The index of the (first) minimum value in self._data
    _min_index = Int
    
    # The index of the (first) maximum value in self._data
    _max_index = Int
    
    
    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------
    
    def __init__(self, data=array([]), sort_order="none", **kw):
        AbstractDataSource.__init__(self, **kw)
        self.set_data(data, sort_order)
        return
    
    def set_data(self, newdata, sort_order=None):
        self._data = newdata
        if sort_order is not None:
            self.sort_order = sort_order
        self._compute_bounds()
        self.data_changed = True
        return
    
    def set_mask(self, mask):
        self._cached_mask = mask
        self.data_changed = True
        return
    
    def remove_mask(self):
        self._cached_mask = None
        self.data_changed = True
        return
    
    #------------------------------------------------------------------------
    # AbstractDataSource interface
    #------------------------------------------------------------------------
    
    def get_data(self):
        if self._data is not None:
            return self._data
        else:
            return 0.0
    
    def get_data_mask(self):
        if self._cached_mask is None:
            return self._data, ones(len(self._data), dtype=bool)
        else:
            return self._data, self._cached_mask
    
    def is_masked(self):
        if self._cached_mask is not None:
            return True
        else:
            return False
    
    def get_size(self):
        if self._data is not None:
            return len(self._data)
        else:
            return 0
    
    def get_bounds(self):
        """ Returns the minimum and maximum values of the datasource's data.
        """
        if self._cached_bounds is None or self._cached_bounds == () or \
               self._cached_bounds == 0.0:
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


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _compute_bounds(self, data=None):
        """
        Computes the minimum and maximum values of self._data.  If a data
        array is passed in, then that is used instead.  (Useful for subclasses)
        """
        # TODO: as an optimization, perhaps create and cache a sorted
        #       version of the dataset?
        
        if data is None:
            # Several sources weren't setting the _data attribute, so we
            # go through the interface.  This seems like the correct thing
            # to do anyway... right?
            #data = self._data
            data = self.get_data()
            
        data_len = 0
        try:
            data_len = len(data)
        except:
            pass
        if data_len == 0:
            self._min_index = 0
            self._max_index = 0
            self._cached_bounds = (0.0, 0.0)
        elif data_len == 1:
            self._min_index = 0
            self._max_index = 0
            self._cached_bounds = (data[0], data[0])
        else:
            if self.sort_order == "ascending":
                self._min_index = 0
                self._max_index = -1
            elif self.sort_order == "descending":
                self._min_index = -1
                self._max_index = 0
            else:
                # ignore NaN values.  This is probably a little slower,
                # but also much safer.                

                # data might be an array of strings or objects that 
                # can't have argmin calculated on them.
                try:
                    self._min_index = nanargmin(data)
                    self._max_index = nanargmax(data)
                except TypeError:
                    # For strings and objects, we punt...  These show up in
                    # label-ish data sources.
                    self._cached_bounds = (0.0, 0.0)
                    
            self._cached_bounds = (data[self._min_index],
                               data[self._max_index])
        return
    
    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _metadata_changed(self, event):
        self.metadata_changed = True

    def _metadata_items_changed(self, event):
        self.metadata_changed = True

    #------------------------------------------------------------------------
    # Persistence-related methods
    #------------------------------------------------------------------------
    
    def __getstate__(self):
        state = self.__dict__.copy()
        if not self.persist_data:
            state.pop("_data", None)
            state.pop("_cached_mask", None)
            state.pop("_cached_bounds", None)
            state.pop("_min_index", None)
            state.pop("_max_index", None)
        return state
    
    def _post_load(self):
        super(ArrayDataSource, self)._post_load()
        self._cached_bounds = ()
        self._cached_mask = None
        return


# EOF
