
# Major package imports
from numpy import nanmax, nanmin, array, shape, ones, bool, newaxis, nan_to_num
import types
    
# Enthought library imports
from enthought.traits.api import Any, Int, Tuple

# Chaco imports
from base import NumericalSequenceTrait, SortOrderTrait
from abstract_data_source import AbstractDataSource


class MultiArrayDataSource(AbstractDataSource):
    """
    DataSource representing a single, continuous array of numerical data
    of potentially more than one dimension.
    Does not listen to the array for value changes;  If such behavior is
    desired, it is pretty straightforward to create a subclass that hooks
    up the appropriate listeners.
    """
    
    #------------------------------------------------------------------------
    # AbstractDataSource traits
    #------------------------------------------------------------------------
    
    # Redefine the index dimension from the parent class.
    index_dimension = Int(0)
    
    # Redefine the value dimension from the parent class
    value_dimension = Int(1)
    
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
    
    # The index of hte (first) maximum value in self._data
    _max_index = Int

    def __init__(self, data=array([]), sort_order="ascending", **traits):
        super(MultiArrayDataSource, self).__init__(**traits)
        self._set_data(data)
        self.sort_order = sort_order
        #self._compute_bounds()
        self.data_changed = True
        return

    def get_data(self, axes = None, remove_nans=False):
        """get_data() -> data_array

        With no additional arguments, returns a data array of dimensions
        self.dimension.  This data array should not be altered in-place,
        and the caller should assume it is
        read-only.  This data is contiguous and not masked.

        If axes is an integer or tuple, returns the array sliced along
        the index_dimension.
        """

        if type(axes) == types.IntType:
            if self.index_dimension == 0:
                data = self._data[::, axes]
            else:
                data = self._data[axes, ::]
        elif axes is None:
            data = self._data

        # fixme: we need to handle the multi-dimensional case.

        if remove_nans:
            return nan_to_num(data)
        else:
            return data
    
    def get_data_mask(self):
        if self._cached_mask is None:
            self._cached_mask = ones(shape(self._data), bool)
        return self._data, self._cached_mask
    
    def is_masked(self):
        """is_masked() -> bool
        
        Returns True if this DataSource's data should be retrieved using
        get_data_mask() instead of get_data().  (get_data() should still return
        data, but it may not be the expected data.)
        """
        return False
    
    def get_size(self):
        """get_size() -> int
        
        Returns an integer estimate or the exact size of the dataset that
        get_data will return.  This is useful for downsampling.
        """
        # return the size along the index dimension
        size = 0
        if self._data is not None:
            size = shape(self._data)[self.index_dimension]

        return size

    def get_value_size(self):
        # return the size along the value dimension
        size = 0
        if self._data is not None:
            size = shape(self._data)[self.value_dimension]

        return size
        

    def get_bounds(self, value = None, index = None):
        """get_bounds() -> tuple(min_val, max_val)
        
        Returns a tuple (min, max) of the bounding values for the data source.
        In the case of 2D data, min and max are 2D points represent the
        bounding corners of a rectangle enclosing the data set.  Note that
        these values are not view-dependent, but represent intrinsic
        properties of the DataSource.
        
        If data is the empty set, then the min and max vals are 0.0. 

        If value and index are both None, then returns the global min and
        max for the entire data set.
        If value is an integer, returns the minimum and maximum along the
        value slice in the value_dimension.
        If index is an integer, returns the minimum and maximum along the
        index slice in the index_direction.
        """

        if self._data is None or 0 in self._data.shape:
            return (0.0, 0.0)

        if type(value) == types.IntType:
            if self.value_dimension == 0:
                maxi = nanmax(self._data[value, ::])
                mini = nanmin(self._data[value, ::])
            else:
                # value_dimension == 1
                maxi = nanmax(self._data[::, value])
                mini = nanmin(self._data[::, value])
        elif type(index) == types.IntType:
            if self.index_dimension == 0:
                maxi = nanmax(self._data[index, ::])
                mini = nanmin(self._data[index, ::])
            else:
                # index_dimension == 1
                maxi = nanmax(self._data[::, index])
                mini = nanmin(self._data[::, index])
        else:
            # value is None and index is None:
            maxi = nanmax(self._data)
            mini = nanmin(self._data)
            
        return (mini, maxi)

    def get_shape(self):

        # returns the shape of the multi-dimensional data source
        return shape(self._data)
    
    def set_data(self, value):
        self._set_data(value)
        self.data_changed = True
        return
    
    def _set_data(self, value):
        """ If we get 1D data in, force it to 2D
        """
        if len(value.shape) == 1:
            if self.index_dimension == 0:
                value = value[:,newaxis]
            else:
                value = value[newaxis,:]
        
        if len(value.shape) != 2:
            msg = 'Input is %d dimensional, but it must be 1 or 2' \
                  'dimensional.' % len(value.shape)
            raise ValueError, msg
        
        self._data = value

# EOF
