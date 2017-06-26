""" Defines the MultiArrayDataSource class.
"""
import warnings

# Major package imports
from numpy import nanmax, nanmin, array, shape, ones, bool, newaxis, nan_to_num

# Enthought library imports
from traits.api import Any, Int, Tuple

# Chaco imports
from base import NumericalSequenceTrait, SortOrderTrait
from abstract_data_source import AbstractDataSource


class MultiArrayDataSource(AbstractDataSource):
    """ A data source representing a single, continuous array of
    multidimensional numerical data.

    It is useful, for example, to define 2D vector data at each point of
    a scatter plot (as in QuiverPlot), or to represent multiple values
    for each index (as in MultiLinePlot).

    This class does not listen to the array for value changes;  To implement
    such behavior, define a subclass that hooks up the appropriate listeners.
    """

    #------------------------------------------------------------------------
    # AbstractDataSource traits
    #------------------------------------------------------------------------

    # The dimensionality of the indices into this data source (overrides
    # AbstractDataSource).
    index_dimension = Int(0)

    # The dimensionality of the value at each index point (overrides
    # AbstractDataSource).
    value_dimension = Int(1)

    # The sort order of the data.
    # This is a specialized optimization for 1-D arrays, but it's an important
    # one that's used everywhere.
    sort_order = SortOrderTrait


    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # The data array itself.
    _data = NumericalSequenceTrait

    # Cached values of min and max as long as **_data** doesn't change.
    _cached_bounds = Tuple

    # Not necessary, since this is not a filter, but provided for convenience.
    _cached_mask = Any

    # The index of the (first) minimum value in self._data.
    _min_index = Int

    # The index of the (first) maximum value in self._data.
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

        If called with no arguments, this method returns a data array.
        Treat this data array as read-only, and do not alter it in-place.
        This data is contiguous and not masked.

        If *axes* is an integer or tuple, this method returns the data array,
        sliced along the **index_dimension**.
        """

        if type(axes) == int:
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
        """get_data_mask() -> (data_array, mask_array)

        Implements AbstractDataSource.
        """
        if self._cached_mask is None:
            self._cached_mask = ones(shape(self._data), bool)
        return self._data, self._cached_mask

    def is_masked(self):
        """is_masked() -> bool

        Returns True if this data source's data uses a mask. In this case,
        retrieve the data using get_data_mask() instead of get_data().
        If you call get_data() for this data source, it returns data, but that
        data may not be the expected data.)
        """
        return False

    def get_size(self):
        """get_size() -> int

        Implements AbstractDataSource. Returns an integer estimate, or the
        exact size, of the dataset that get_data() returns. This method is
        useful for downsampling.
        """
        # return the size along the index dimension
        size = 0
        if self._data is not None:
            size = shape(self._data)[self.index_dimension]

        return size

    def get_value_size(self):
        """ get_value_size() -> size

        Returns the size along the value dimension.
        """
        size = 0
        if self._data is not None:
            size = shape(self._data)[self.value_dimension]

        return size


    def get_bounds(self, value = None, index = None):
        """get_bounds() -> tuple(min, max)

        Returns a tuple (min, max) of the bounding values for the data source.
        In the case of 2-D data, min and max are 2-D points that represent the
        bounding corners of a rectangle enclosing the data set.  Note that
        these values are not view-dependent, but represent intrinsic properties
        of the data source.

        If data is the empty set, then the min and max vals are 0.0.

        If *value* and *index* are both None, then the method returns the
        global minimum and maximum for the entire data set.
        If *value* is an integer, then the method returns the minimum and
        maximum along the *value* slice in the **value_dimension**.
        If *index* is an integer, then the method returns the minimum and
        maximum along the *index* slice in the **index_direction**.
        """

        if self._data is None or 0 in self._data.shape:
            return (0.0, 0.0)

        if type(value) == int:
            if self.value_dimension == 0:
                maxi = nanmax(self._data[value, ::])
                mini = nanmin(self._data[value, ::])
            else:
                # value_dimension == 1
                maxi = nanmax(self._data[::, value])
                mini = nanmin(self._data[::, value])
        elif type(index) == int:
            if self.index_dimension == 0:
                maxi = nanmax(self._data[index, ::])
                mini = nanmin(self._data[index, ::])
            else:
                # index_dimension == 1
                maxi = nanmax(self._data[::, index])
                mini = nanmin(self._data[::, index])
        else:
            # value is None and index is None:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    'ignore', "All-NaN (slice|axis) encountered", RuntimeWarning)
                maxi = nanmax(self._data)
                mini = nanmin(self._data)

        return (mini, maxi)

    def get_shape(self):
        """ Returns the shape of the multi-dimensional data source.
        """
        return shape(self._data)

    def set_data(self, value):
        """ Sets the data for this data source.

        Parameters
        ----------
        value : array
            The data to use.
        """
        self._set_data(value)
        self.data_changed = True
        return

    def _set_data(self, value):
        """ Forces 1-D data to 2-D.
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
