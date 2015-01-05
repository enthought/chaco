"""
Defines the BaseArrayDataSource class.

This is a base class that implements common logic for NumPy array-based data
sources, ie. where the underlying data is stored in a numpy array fairly
directly.

"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from traits.api import ArrayOrNone, Array, Property, cached_property

from .base_data_source import BaseDataSource


class BaseArrayDataSource(BaseDataSource):
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
        self.set_data(data, mask=mask)

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
        with self.updating_data():
            self._data = data
            if mask is not None:
                self._user_mask = mask

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
        with self.updating_data():
            self._user_mask = mask

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

    #------------------------------------------------------------------------
    # Private interface
    #------------------------------------------------------------------------

    #: the array holding the data.  This should be overridden with something
    #: more specific in concrete subclasses.
    _data = ArrayOrNone

    #: the user-supplied mask.
    _user_mask = ArrayOrNone(dtype=bool)

    #: the actual mask, combining the user and finite masks
    _mask = Property(Array(dtype=bool), depends_on='_data_valid')

    def _get_data_unsafe(self):
        """ Return the data without guarding against changes

        This method can be safely called by subclasses via super() without
        worrying about locking.

        """
        data = self._data
        if data is None:
            return self._empty_data()
        return data

    def _get_mask_unsafe(self):
        """ Return the data without guarding against changes

        This method can be safely called by subclasses via super() without
        worrying about locking.

        """
        return self._mask

    def _is_masked_unsafe(self):
        """ Is the data masked, without guarding against changes

        """
        return self._user_mask is not None or not self._finite

    def _empty_data(self):
        """ Method that returns an empty array of the appropriate type

        Concrete subclasses must implement this.

        """
        raise NotImplementedError

    @cached_property
    def _get__mask(self):
        if self._user_mask is None:
            return self._finite_mask
        elif self._finite:
            return self._user_mask
        else:
            return self._user_mask & self._finite_mask
