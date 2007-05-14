"""
Defines PointDataSeries
"""

# Major library imports
from numpy import array, transpose

# Enthought library imports
from enthought.traits.api import Enum, Property, ReadOnly, Tuple

# Local, relative imports
from base import PointTrait, reverse_map_1d, SortOrderTrait
from array_data_source import ArrayDataSource

class PointDataSource(ArrayDataSource):
    """
    DataSource representing a (possibly unordered) set of (X,Y) points.
    This is internally always represented by an Nx2 array, so that data[i]
    refers to a single point (represented as a length-2 array).
    """
    
    # Most of the traits and methods of ArrayDataSeries work for the
    # PointDataSeries as well, since its _data is linear.  This class
    # just overrides the methods and traits that are different.
    
    # Redefine the index dimension from the parent class
    index_dimension = ReadOnly('scalar')
    
    # Redefine the value dimension from the parent class
    value_dimension = ReadOnly('point')
    
    # Although sort order is less common with point data, it can be useful
    # in instances when the value data is sorted along some axis.  Note
    # that sort_index is only used if sort_order is not "none".
    sort_order = SortOrderTrait
    
    # Indicates which of the value axes the sort_order refers to.
    # If sort_order is "none", this is ignored.
    # In the unlikely event that the value data is sorted along both
    # X and Y (i.e. monotonic in both axes), then set sort_index to whichever
    # one will have the best binary-search performance for hit testing.
    sort_index = Enum(0, 1)
    
    
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # The actual data
    _data = PointTrait
    
    # caches the value of min and max as long as data doesn't change
    # ((min_x, max_x), (min_y, max_y))
    _cached_bounds = Tuple
    
    # These return lists of all the x and y positions, respectively
    _xdata = Property
    _ydata = Property
    
    #------------------------------------------------------------------------
    # AbstractDataSource interface
    #------------------------------------------------------------------------
    
    def __init__(self, data = transpose(array([[],[]])), **kw):
        shape = data.shape
        if (len(shape) != 2) or (shape[1] != 2):
            raise RuntimeError, "PointDataSource constructor requires Nx2 array, but got array of shape " + str(shape) + " instead."
        super(PointDataSource, self).__init__(data, **kw)
        return
    
    def get_data(self):
        if self._data is not None:
            return self._data
        else:
            return (0.0, 0.0)
    
    def reverse_map(self, pt, index=0, outside_returns_none=True):
        # reverse_map is of limited utility for a PointDataSeries and thus
        # we only perform reverse-mapping if the data is sorted along an axis.
        
        if self.sort_order == "none":
            # By default, only provide reverse_map if the value data is sorted
            # along one of its axes.
            raise NotImplementedError
        
        if index != 0 and index != 1:
            raise ValueError, "Index must be 0 or 1."
        
        # This basically reduces to a scalar data search along self.data[index].
        lowerleft, upperright= self._cached_bounds
        min_val = lowerleft[index]
        max_val = upperright[index]
        val = pt[index]
        if (val < minval):
            if outside_returns_none:
                return None
            else:
                return self._min_index
        elif (val > maxval):
            if outside_returns_none:
                return None
            else:
                return self._max_index
        else:
            return reverse_map_1d(self._data[:,index], val, self.sort_order)
    
    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------
    
    def _compute_bounds(self):
        """
        Computes the minimum and maximum values of self._data.
        """
        if len(self._data) == 0:
            self._cached_bounds = ((0.0,0.0), (0.0,0.0))
        elif len(self._data) == 1:
            x,y = self._data[0]
            self._cached_bounds = ((x,y), (x,y))
        else:
            # calculate the X and Y values independently
            x = self._data[:,0]
            min_x = min(x)
            max_x = max(x)
            y = self._data[:,1]
            min_y = min(y)
            max_y = max(y)
            self._cached_bounds = ((min_x,min_y), (max_x,max_y))
        return

    def _get__xdata(self):
        return ArrayDataSource(self._data[:,0])

    def _get__ydata(self):
        return ArrayDataSource(self._data[:,1])

# EOF
