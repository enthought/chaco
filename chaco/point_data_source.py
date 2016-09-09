"""
Defines the PointDataSource class.
"""

# Major library imports
from numpy import array, transpose

# Enthought library imports
from traits.api import Enum, Property, ReadOnly, Tuple

# Local, relative imports
from .base import PointTrait, reverse_map_1d, SortOrderTrait
from .array_data_source import ArrayDataSource


class PointDataSource(ArrayDataSource):
    """ A data source representing a (possibly unordered) set of (X,Y) points.

    This is internally always represented by an Nx2 array, so that data[i]
    refers to a single point (represented as a length-2 array).

    Most of the traits and methods of ArrayDataSeries work for the
    PointDataSeries as well, since its data is linear.  This class
    overrides only the methods and traits that are different.

    """


    # The dimensionality of the indices into this data source (overrides
    # ArrayDataSource).
    index_dimension = ReadOnly('scalar')

    # The dimensionality of the value at each index point (overrides
    # ArrayDataSource).
    value_dimension = ReadOnly('point')

    # The sort order of the data. Although sort order is less common with point
    # data, it can be useful in case where the value data is sorted along some
    # axis.  Note that **sort_index** is used only if **sort_order** is not
    # 'none'.
    sort_order = SortOrderTrait

    # Which of the value axes the **sort_order** refers to.
    # If **sort_order** is 'none', this attribute is ignored.
    # In the unlikely event that the value data is sorted along both
    # X and Y (i.e., monotonic in both axes), then set **sort_index** to
    # whichever one has the best binary-search performance for hit-testing.
    sort_index = Enum(0, 1)


    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # The actual data (overrides ArrayDataSource).
    _data = PointTrait

    # Cached values of min and max as long as **_data** doesn't change
    # (overrides ArrayDataSource). ((min_x, max_x), (min_y, max_y))
    _cached_bounds = Tuple

    # These return lists of all the x and y positions, respectively

    # List of X positions.
    _xdata = Property
    # List of Y positions.
    _ydata = Property

    #------------------------------------------------------------------------
    # AbstractDataSource interface
    #------------------------------------------------------------------------

    def __init__(self, data = transpose(array([[],[]])), **kw):
        shape = data.shape
        if (len(shape) != 2) or (shape[1] != 2):
            raise RuntimeError("PointDataSource constructor requires Nx2 array, but got array of shape " + str(shape) + " instead.")
        super(PointDataSource, self).__init__(data, **kw)
        return

    def get_data(self):
        """ Returns the data for this data source, or (0.0, 0.0) if it has no
        data.

        Overrides ArryDataSource.
        """
        if self._data is not None:
            return self._data
        else:
            return (0.0, 0.0)

    def reverse_map(self, pt, index=0, outside_returns_none=True):
        """Returns the index of *pt* in the data source.

        Overrides ArrayDataSource.

        Parameters
        ----------
        pt : (x, y)
            value to find
        index : 0 or 1
            Which of the axes of *pt* the *sort_order* refers to.
        outside_returns_none : Boolean
            Whether the method returns None if *pt* is outside the range of
            the data source; if False, the method returns the value of the
            bound that *pt* is outside of, in the *index* dimension.

        """
        # reverse_map is of limited utility for a PointDataSeries and thus
        # we only perform reverse-mapping if the data is sorted along an axis.

        if self.sort_order == "none":
            # By default, only provide reverse_map if the value data is sorted
            # along one of its axes.
            raise NotImplementedError

        if index != 0 and index != 1:
            raise ValueError("Index must be 0 or 1.")

        # This basically reduces to a scalar data search along self.data[index].
        lowerleft, upperright= self._cached_bounds
        min_val = lowerleft[index]
        max_val = upperright[index]
        val = pt[index]
        if (val < min_val):
            if outside_returns_none:
                return None
            else:
                return self._min_index
        elif (val > max_val):
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
        """ Computes the minimum and maximum values of self._data.

        Overrides ArrayDataSource.
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
