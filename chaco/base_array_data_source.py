"""
Defines the BaseArrayDataSource class.

This is a base class that implements common logic for NumPy array-based data
sources, ie. where the underlying data is stored in a numpy array fairly
directly.

"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from contextlib import contextmanager
from numpy import isfinite, isnan, nanmax, nanmin, ones

from traits.api import ArrayOrNone, Bool, Either, Instance, Tuple

from .abstract_data_source import AbstractDataSource
from .base import DataInvalidError, DataUpdateError


class BaseArrayDataSource(AbstractDataSource):
    """ Base class for data sources which store data in a NumPy array

    This class provides basic implementation of the AbstractDataSource
    interface on top of a numpy array.  The class also guards against
    accessing the data while a change to the data is under way.

    Parameters
    ----------

    data : array-like or None (default is None)
        If None, the current data future queries to get_data will return an
        appropriate empty data object.  Otherwise the data must be an
        array-like compatible with the dimension and value type.

    mask : array-like of bool or None (default is None)
        If None, this clears the mask.  Otherwise the mask must be an
        array-like compatible with the dimension of the data source and the
        shape of the underlying data array.

    Notes
    -----

    This class is abstract and shouldn't be instantiated directly.  This class
    also should not be used as an interface: plots and renderers shouldn't care
    about the mechanics of data source internals (ie. whether the data is in
    an array) but on the dimensionality, value type, masking, etc.

    Subclasses must provide valid `dimension` and `value_type` traits, and
    implement the private `_empty_data()` method to return an appropriate
    value when the data is set to `None` (usually an empty array of the
    correct dimensionality, but with zeroed shape).

    The constructor does not check that the data array and mask array have the
    correct dimension, value type or compatible shapes. Subclasses should use
    appropriate trait types to ensure that the underlying arrays have
    appropriate dimension and value type.

    The implementation is designed for arrays that fit comfortably in memory
    and, in particular, for which is is not an imposition to create temporary
    copies and masks, since the `nanmin` and `nanmax` functions do that under
    the covers.

    """

    #------------------------------------------------------------------------
    # BaseArrayDataSource interface
    #------------------------------------------------------------------------

    def __init__(self, data=None, mask=None, **traits):
        super(BaseArrayDataSource, self).__init__(**traits)
        self.set_data(data, mask)

    def set_data(self, data, mask=None):
        """ Set the value of the data and (optional) mask.

        This method should be used if an atomic update of data and mask is
        required.

        Parameters
        ----------

        data : array-like or None
            If None, the current data is removed and future queries to
            get_data will return an appropriate empty data object.  Otherwise
            the data must be an array-like compatible with the dimension and
            value type.

        mask : array-like of bool or None
            If None, leaves the mask as-is.  Otherwise the mask must be an
            array-like compatible with the dimension of the data source and the
            shape of the underlying data array.

        Raises
        ------

        DataUpdateError:
            If the data is already being modified when `set_data` is called,
            a `DataUpdateError` will be raised.

        Notes
        -----

        This method does not check that the data array and mask array have the
        correct dimension, value type or compatible shapes.  If the shapes are
        incompatible, calls to `get_data_mask` will raise a `ValueError`.

        """
        with self._updating_data():
            self._data = data
            self._finite_mask = None
            self._cached_bounds = None
            if mask is not None:
                self._mask = mask

    def set_mask(self, mask):
        """ Set the value of the mask

        The actual mask will be the intesection of this mask and the
        finite data values.

        Parameters
        ----------

        mask : array-like of bool or None
            If None, this clears the mask.  Otherwise the mask must be an
            array-like compatible with the dimension of the data source and
            the shape of the underlying data array.

        Raises
        ------

        DataUpdateError:
            If the data is already being modified when `set_mask` is called,
            a `DataUpdateError` will be raised.

        Notes
        -----

        This method does not check that the data array and mask array have
        compatible shapes.  If the shapes are incompatible, calls to
        `get_data_mask` will raise a `ValueError`.

        """
        with self._updating_data():
            self._mask = mask

    def remove_mask(self):
        """ Remove the mask

        This is largely for backwards compatibility, it is equivalent to
        set_mask(None).

        Raises
        ------

        DataUpdateError:
            If the data is already being modified when `remove_mask` is called,
            a `DataUpdateError` will be raised.

        """
        self.set_mask(None)

    def invalidate_data(self):
        """ Mark the data value as invalid.

        Data can only become valid again after a successful `set_data`.

        """
        self._data_valid = False

    def access_guard(self):
        """ Context manager that detects data becoming invalid during access

        This listens for changes in internal state to detect if the
        data is initially invalid, or the `invalidate_data` method has been
        called during the context.

        Returns
        -------

        access_guard : context manager
            A context manager that raises a DataInvalidError if the data is
            invalidated.

        Raises
        ------

        DataInvalidError:
            When the data is invalid.

        """
        return Guard(self)

    #------------------------------------------------------------------------
    # AbstractDataSource interface
    #------------------------------------------------------------------------

    def get_data(self):
        """Get an array representing the data stored in the data source.

        Returns
        -------

        data_array : array of values
            An array of the dimensions specified by the index and value
            dimension traits. This data array must not be altered in-place,
            and the caller must assume it is read-only.  This data is
            contiguous and not masked.

        """
        with self.access_guard():
            data = self._get_data_unsafe()
        return data

    def get_data_mask(self):
        """Get arrays representing the data and the mask of the data source.

        Returns
        -------

        data_array, mask: array of values, array of bool
            Returns the full source data array and a corresponding binary
            mask array.  Treat both arrays as read-only.

        Raises
        ------

        ValueError:
            If mask's shape is incompatible with the data shape.

        """
        with self.access_guard():
            data, mask = self._get_data_mask_unsafe()

        return data, mask

    def is_masked(self):
        """Whether or not the data is masked.

        Returns
        -------

        is_masked : bool
            True if this data source's data uses a mask of has non-finite
            values.

        Raises
        ------

        ValueError:
            If mask's shape is incompatible with the data shape.

        """
        with self.access_guard():
            self._compute_finite()
            masked = self._mask is not None or not self._finite
        return masked

    def get_size(self):
        """The size of the data.

        This method is useful for down-sampling.

        Returns
        -------

        size : tuple of ints
            Returns the shape of the data for the index dimensions.

        """
        with self.access_guard():
            data = self._get_data_unsafe()

        return data.shape[:self.dimension]

    def get_bounds(self):
        """ Get the minimum and maximum finite values of the data.

        Returns
        -------

        bounds : tuple of min, max
            A tuple (min, max) of the bounding values for the data source.
            In the case of n-dimensional data values, min and max are
            n-dimensional points that represent the bounding corners of a
            rectangle enclosing the data set.

        Raises
        ------

        ValueError:
            If an all-nan axis is found.

        TypeError:
            If the dtype is not appropriate for min and max (eg. strings)

        """
        with self.access_guard():
            if self._cached_bounds is None:
                self._compute_bounds()
            bounds = self._cached_bounds

        return bounds

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _metadata_changed(self, event):
        self.metadata_changed = True

    def _metadata_items_changed(self, event):
        self.metadata_changed = True

    #------------------------------------------------------------------------
    # Private interface
    #------------------------------------------------------------------------

    #: the array holding the data.  This should be overridden with something
    #: more specific in concrete subclasses.
    _data = ArrayOrNone

    #: the user-supplied mask.
    _mask = ArrayOrNone(dtype=bool)

    #: locations where the data is finite
    _finite_mask = ArrayOrNone(dtype=bool)

    #: the actual mask taking into account non-finite values.
    _cached_mask = ArrayOrNone(dtype=bool)

    #: whether or not the data is finite at all locations
    _finite = Bool

    #: the min, max bounds of the (unmasked) data
    _cached_bounds = Either(Tuple, None)

    #: a flag indicating whether the data is currently valid
    _data_valid = Bool(False)

    #: a lock that should be acquired before modifying the data.  This should
    #: usually be acquired in a non-blocking fashion
    _update_lock = Instance('threading.Lock', args=())

    def _get_data_unsafe(self):
        """ Return the data without aquiring the update lock

        This method can be safely called by subclasses via super() without
        worrying about locking.

        """
        data = self._data
        if data is None:
            return self._empty_data()
        return data

    def _get_data_mask_unsafe(self):
        """ Return the data without aquiring the update lock

        This method can be safely called by subclasses via super() without
        worrying about locking.

        """
        data = self._get_data_unsafe()
        self._compute_mask()
        mask = self._cached_mask
        return data, mask

    def _empty_data(self):
        """ Method that returns an empty array of the appropriate type

        Concrete subclasses must implement this.

        """
        raise NotImplementedError

    def _compute_mask(self):
        """ Compute the mask and cache it """
        if self._cached_mask is None:
            self._compute_finite()
            if self._mask is None:
                    self._cached_mask = self._finite_mask
            elif self._finite:
                self._cached_mask = self._mask
            else:
                self._cached_mask = self._finite_mask & self._mask

    def _compute_finite(self):
        """ Compute locations where data is finite

        Subclasses with complex dtypes may need to override this method.

        """
        if self._finite_mask is None:
            data = self._get_data_unsafe()
            non_index_axes = tuple(range(self.dimension, len(data.shape)))
            try:
                self._finite_mask = isfinite(data).all(axis=non_index_axes)
                self._finite = self._finite_mask.all()
            except TypeError:
                # dtype for which isfinite doesn't work; finite by definition
                self._finite_mask = ones(shape=data.shape[:self.dimension],
                                         dtype=bool)
                self._finite = True

    def _compute_bounds(self):
        """ Compute bounds of values

        Subclasses may override this to avoid un-needed computation in cases
        where minimum and maximum values are known (eg. sorted data).

        Raises
        ------

        ValueError:
            If an all-nan axis is found.

        TypeError:
            If the dtype is not appropriate for min and max (eg. strings)

        """
        data = self._get_data_unsafe()

        index_axes = tuple(range(self.dimension))
        min_value = nanmin(data, axis=index_axes)
        max_value = nanmax(data, axis=index_axes)

        # only need to check min value: nans in max_value imply nans here too
        if isnan(min_value).any():
            raise ValueError("All-NaN axis encountered")

        self._cached_bounds = (min_value, max_value)


    @contextmanager
    def _updating_data(self):
        """ Context manager for updating data

        In the enter method this manager attempts to acquire the update lock,
        raising an exception if it is not immediately available, then sets the
        validity of the data to False.

        In the exit method it ensures that the update lock is released, and
        sets the
        """
        acquired = self._update_lock.acquire(False)
        if not acquired:
            msg = "data update conflict, {0} cannot acquire lock"
            raise DataUpdateError(msg.format(self))
        try:
            self.invalidate_data()
            yield self
            self._cached_mask = None
            self._data_valid = True
        finally:
            self._update_lock.release()

        self.data_changed = True


class Guard(object):
    """ Guard against trait becoming invalid during access

    Lightweight context manager that raises an exception if trait becomes
    invalid during an operation.

    """

    def __init__(self, obj, valid_trait='_data_valid'):
        self.valid_trait = valid_trait
        self.valid = True
        self.obj = obj

    def valid_change_listener(self, new):
        self.valid = self.valid and new

    def __enter__(self):
        self.obj.on_trait_change(self.valid_change_listener, self.valid_trait)
        self.valid = self.valid and getattr(self.obj, self.valid_trait)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if not self.valid:
            msg = "data source {0} data is not valid"
            raise DataInvalidError(msg.format(self))
