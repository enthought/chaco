"""
Defines the BaseDataSource class.

This is a base class that implements common logic for reasonably safe access
to data, raising exceptions if data is modified during a get operation, and
locking to prevent simultaneous set operations on different threads.

"""

from __future__ import \
    absolute_import, division, print_function, unicode_literals

from contextlib import contextmanager
from numpy import isfinite, isnan, nanmax, nanmin, ones, prod

from traits.api import \
    Array, Bool, Event, Instance, Property, Tuple, cached_property

from .abstract_data_source import AbstractDataSource
from .base import DataBoundsError, DataInvalidError, DataUpdateError


class BaseDataSource(AbstractDataSource):
    """ Base class for data sources which store data in a NumPy array

    This class provides basic implementation of the AbstractDataSource
    interface on top of a numpy array.  The class also guards against
    accessing the data while a change to the data is under way.

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
    # BaseDataSource interface
    #------------------------------------------------------------------------

    def invalidate_data(self):
        """ Mark the data value as invalid.

        Data can only become valid again after data is successfully updated.

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

    @contextmanager
    def updating_data(self):
        """ Context manager for updating data

        Subclasses should guard data-changing operations with this context
        manager.

        In the enter method this manager attempts to acquire the update lock,
        raising an exception if it is not immediately available, then sets the
        validity of the data to False.

        In the exit method it ensures that the update lock is released,
        and if there was no error, flags the data as valid, clears the caches,
        and fires the data changed event.

        """
        acquired = self._update_lock.acquire(False)
        if not acquired:
            msg = "data update conflict, {0} cannot acquire lock"
            raise DataUpdateError(msg.format(self))
        try:
            self.invalidate_data()
            yield self
            self._data_valid = True
        finally:
            self._update_lock.release()

        self.data_changed = True

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
            data = self._get_data_unsafe()
            mask = self._get_mask_unsafe()

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
            is_masked = self._is_masked_unsafe()
        return is_masked

    def get_shape(self):
        """The size of the data.

        This method is useful for down-sampling.

        Returns
        -------

        size : tuple of ints
            Returns the shape of the data for the index dimensions.

        """
        with self.access_guard():
            shape = self._get_shape_unsafe()
        return shape

    def get_size(self):
        """The size of the data.

        This method is useful for down-sampling.

        Returns
        -------

        size : tuple of ints
            Returns the shape of the data for the index dimensions.

        """
        return prod(self.get_shape())

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
            bounds = self._get_bounds_unsafe()
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

    #: whether or not the data is finite at all values
    _finite = Property(Bool, depends_on='_data_valid')

    #: a mask of finite values of the data.
    _finite_mask = Property(Array(dtype=bool), depends_on='_data_valid')

    #: the min, max bounds of the (unmasked) data
    _bounds = Property(Tuple, depends_on='_data_valid')

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
        raise NotImplementedError

    def _get_mask_unsafe(self):
        """ Return the data without aquiring the update lock

        A default method which computes where the array is finite is provided.

        Subclasses should override this method if they have more sophisticated
        mask handling.  This method can be safely called by subclasses via
        super() without worrying about locking.

        """
        return self._finite_mask

    def _is_masked_unsafe(self):
        """ Return the data without aquiring the update lock

        A default implementation which returns True if there are any infinte
        values.

        Subclasses may want to override this method if they have more
        sophisticated mask handling.  This method can be safely called by
        subclasses via super() without worrying about locking.

        """
        print('called _is_masked_unsafe')
        return not self._finite

    def _get_shape_unsafe(self):
        """ Return the data without aquiring the update lock

        A default implementation is provided.  Subclasses may want to override
        as needed. This method can be safely called by subclasses via super()
        without worrying about locking.

        """
        data = self._get_data_unsafe()
        return data.shape[:self.dimension]

    def _get_bounds_unsafe(self):
        """ Return the data without aquiring the update lock

        A default implementation is provided.  Subclasses may want to override
        as needed, particularly if they have complex value types. This method
        can be safely called by subclasses via super() without worrying about
        locking.

        """
        return self._bounds

    @cached_property
    def _get__finite_mask(self):
        """ Compute the mask and cache it """
        data = self._get_data_unsafe()
        non_index_axes = tuple(range(self.dimension, len(data.shape)))
        try:
            return isfinite(data).all(axis=non_index_axes)
        except TypeError:
            # dtype for which isfinite doesn't work; finite by definition
            return ones(shape=self._get_shape_unsafe(), dtype=bool)

    @cached_property
    def _get__finite(self):
        """ Whether or not the data is finite in all positions

        This can be overridden in situations where it is known that the data
        is finite, or if there is a more efficient way to compute the fact.

        """
        print('called _get_finite')
        return self._finite_mask.all()

    @cached_property
    def _get__bounds(self):
        """ Compute bounds of values, setting the `_cached_bounds` attribute

        Subclasses may override this to avoid un-needed computation in cases
        where minimum and maximum values are known (eg. sorted data).

        Returns
        -------

        bounds : tuple of (min, max)

        Raises
        ------

        DataBoundsError:
            If the data is empty, has an all-NaN axis, or otherwise has a
            value where the bounds can't be computed.

        TypeError:
            If the dtype is not appropriate for min and max (eg. strings)

        """
        data = self._get_data_unsafe()
        if prod(data.shape[:self.dimension]) == 0:
            raise DataBoundsError("Empty data has no valid bounds")

        index_axes = tuple(range(self.dimension))
        min_value = nanmin(data, axis=index_axes)
        max_value = nanmax(data, axis=index_axes)

        # only need to check min value: nans in max_value imply nans here too
        if isnan(min_value).any():
            raise DataBoundsError("All-NaN axis encountered")

        return (min_value, max_value)


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
