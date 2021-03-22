""" Defines the ArrayDataSource class."""

# Major library imports
from numpy import array, isfinite, ones, ndarray
import numpy as np

# Enthought library imports
from traits.api import Any, Constant, Int, Tuple

# Chaco imports
from .base import NumericalSequenceTrait, reverse_map_1d, SortOrderTrait
from .abstract_data_source import AbstractDataSource


def bounded_nanargmin(arr):
    """ Find the index of the minimum value, ignoring NaNs.

    If all NaNs, return 0.
    """
    # Different versions of numpy behave differently in the all-NaN case, so we
    # catch this condition in two different ways.
    try:
        if np.issubdtype(arr.dtype, np.floating):
            min = np.nanargmin(arr)
        elif np.issubdtype(arr.dtype, np.number):
            min = np.argmin(arr)
        else:
            min = 0
    except ValueError:
        return 0
    if isfinite(min):
        return min
    else:
        return 0

def bounded_nanargmax(arr):
    """ Find the index of the maximum value, ignoring NaNs.

    If all NaNs, return -1.
    """
    try:
        if np.issubdtype(arr.dtype, np.floating):
            max = np.nanargmax(arr)
        elif np.issubdtype(arr.dtype, np.number):
            max = np.argmax(arr)
        else:
            max = -1
    except ValueError:
        return -1
    if isfinite(max):
        return max
    else:
        return -1

class ArrayDataSource(AbstractDataSource):
    """ A data source representing a single, continuous array of numerical data.

    This class does not listen to the array for value changes; if you need that
    behavior, create a subclass that hooks up the appropriate listeners.
    """

    #------------------------------------------------------------------------
    # AbstractDataSource traits
    #------------------------------------------------------------------------

    #: The dimensionality of the indices into this data source (overrides
    #: AbstractDataSource).
    index_dimension = Constant('scalar')

    #: The dimensionality of the value at each index point (overrides
    #: AbstractDataSource).
    value_dimension = Constant('scalar')

    #: The sort order of the data.
    #: This is a specialized optimization for 1-D arrays, but it's an important
    #: one that's used everywhere.
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

    # The index of the (first) minimum value in self._data
    # FIXME: This is an Any instead of an Int trait because of how Traits
    # typechecks numpy.int64 on 64-bit Windows systems.
    _min_index = Any

    # The index of the (first) maximum value in self._data
    # FIXME: This is an Any instead of an Int trait because of how Traits
    # typechecks numpy.int64 on 64-bit Windows systems.
    _max_index = Any


    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, data=array([]), sort_order="none", **kw):
        AbstractDataSource.__init__(self, **kw)
        self.set_data(data, sort_order)
        return

    def set_data(self, newdata, sort_order=None):
        """ Sets the data, and optionally the sort order, for this data source.

        Parameters
        ----------
        newdata : array
            The data to use.
        sort_order : SortOrderTrait
            The sort order of the data
        """
        self._data = newdata
        if sort_order is not None:
            self.sort_order = sort_order
        self._compute_bounds()
        self.data_changed = True
        return

    def set_mask(self, mask):
        """ Sets the mask for this data source.
        """
        self._cached_mask = mask
        self.data_changed = True
        return

    def remove_mask(self):
        """ Removes the mask on this data source.
        """
        self._cached_mask = None
        self.data_changed = True
        return

    #------------------------------------------------------------------------
    # AbstractDataSource interface
    #------------------------------------------------------------------------

    def get_data(self):
        """ Returns the data for this data source, or 0.0 if it has no data.

        Implements AbstractDataSource.
        """
        if self._data is not None:
            return self._data
        else:
            return 0.0

    def get_data_mask(self):
        """get_data_mask() -> (data_array, mask_array)

        Implements AbstractDataSource.
        """
        if self._cached_mask is None:
            return self._data, ones(len(self._data), dtype=bool)
        else:
            return self._data, self._cached_mask

    def is_masked(self):
        """is_masked() -> bool

        Implements AbstractDataSource.
        """
        if self._cached_mask is not None:
            return True
        else:
            return False

    def get_size(self):
        """get_size() -> int

        Implements AbstractDataSource.
        """
        if self._data is not None:
            return len(self._data)
        else:
            return 0

    def get_bounds(self):
        """ Returns the minimum and maximum values of the data source's data.

        Implements AbstractDataSource.
        """
        if self._cached_bounds is None or self._cached_bounds == () or \
               self._cached_bounds == 0.0:
            self._compute_bounds()
        return self._cached_bounds

    def reverse_map(self, pt, index=0, outside_returns_none=True):
        """Returns the index of *pt* in the data source.

        Parameters
        ----------
        pt : scalar value
            value to find
        index
            ignored for data series with 1-D indices
        outside_returns_none : Boolean
            Whether the method returns None if *pt* is outside the range of
            the data source; if False, the method returns the value of the
            bound that *pt* is outside of.
        """
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
        """ Computes the minimum and maximum values of self._data.

        If a data array is passed in, then that is used instead of self._data.
        This behavior is useful for subclasses.
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
        except Exception:
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
                    # the data may be in a subclass of numpy.array, viewing
                    # the data as a ndarray will remove side effects of
                    # the subclasses, such as different operator behaviors
                    self._min_index = bounded_nanargmin(data.view(ndarray))
                    self._max_index = bounded_nanargmax(data.view(ndarray))
                except (TypeError, IndexError, NotImplementedError):
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
