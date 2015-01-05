"""
Defines the AbstractDataSource class.

This is the abstract base class for all sources which provide data to Chaco
plots and renderers.


"""

from __future__ import absolute_import, division, print_function, unicode_literals

from traits.api import ABCHasTraits, Dict, Event, Int, Str

# Local relative imports
from .base import ValueType


class AbstractDataSource(ABCHasTraits):
    """ Abstract interface for data sources used by Chaco renderers

    This abstract interface must be implemented by any class supplying data
    to Chaco renderers. Chaco does not have a notion of a "data format".
    For the most part, a data source looks like an array of values with an
    optional mask and metadata. If you implement this interface, you are
    responsible for adapting your domain-specific or application-specific data
    to meet this interface.

    Chaco provides some basic data source implementations. In most cases, the
    easiest strategy is to create one of these basic data source with the
    numeric data from a domain model. In cases when this strategy is not
    possible, domain classes (or an adapter) must implement AbstractDataSource.

    Notes
    -----

    The contract implied by the AbstractDataSource interface is that data
    arrays provided by the get methods of the class should not be treated as
    read-only arrays, and that any change to the data or mask (such as by
    subclasses which provide a `set_data` method) will be accompanied by the
    `data_changed` event being fired.

    """

    #: The dimension of the values provided by the data source.
    #: Implementations of the interface will typically redefine this as a
    #: read-only trait with a particular value.
    value_type = ValueType('scalar')

    #: The dimension of the indices into the data source.
    #: Implementations of the interface will typically redefine this as a
    #: read-only trait with a particular value.
    dimension = Int(1)

    #: The metadata for the data source.
    #: Metadata values are typically used for annotations and selections
    #: on the data source, and so each keyword corresponds to a collection of
    #: indices into the data source.  Applications and renderers can add their
    #: own custom metadata, but must avoid using keys that might result in name
    #: collision.
    metadata = Dict(Str)

    #: Event that fires when the data values change.
    data_changed = Event

    #: Event that fires when the bounds (ie. the extent of the values) change.
    bounds_changed = Event

    #: Event that fires when metadata structure is changed.
    metadata_changed = Event

    #------------------------------------------------------------------------
    # AbstractDataSource interface
    #------------------------------------------------------------------------

    def get_data(self):
        """Get an array representing the data stored in the data source.

        Returns
        -------

        data_array : array
            An array of the dimensions specified by the index and value
            dimension traits. This data array must not be altered in-place,
            and the caller must assume it is read-only.  This data is
            contiguous and not masked.

        """
        raise NotImplementedError

    def get_data_mask(self):
        """Get arrays representing the data and the mask of the data source.

        Returns
        -------

        data_array, mask: array of values, array of bool
            Returns the full, raw, source data array and a corresponding binary
            mask array.  Treat both arrays as read-only.

            The mask is a superposition of the masks of all upstream data sources.
            The length of the returned array may be much larger than what
            get_size() returns; the unmasked portion, however, matches what
            get_size() returns.

        """
        raise NotImplementedError

    def is_masked(self):
        """Whether or not the data is masked.

        Returns
        -------

        is_masked : bool
            True if this data source's data uses a mask. In this case,
            to retrieve the data, call get_data_mask() instead of get_data().

        """
        raise NotImplementedError

    def get_size(self):
        """The size of the data.

        This method is useful for down-sampling.

        Returns
        -------

        size : int or tuple of ints
            An estimate (or the exact size) of the dataset that get_data()
            returns for this object.  For data sets with n-dimensional index
            values, this can return an n-tuple indicating the size in each
            dimension.

        """
        raise NotImplementedError

    def get_bounds(self):
        """Get the minimum and maximum finite values of the data.

        Returns
        -------

        bounds : tuple of min, max
            A tuple (min, max) of the bounding values for the data source.
            In the case of n-dimensional data values, min and max are
            n-dimensional points that represent the bounding corners of a
            rectangle enclosing the data set.  Note that these values are not
            view-dependent, but represent intrinsic properties of the data
            source.

        Raises
        ------

        TypeError:
            If data's value type is not amenable to sorting, a TypeError can
            be raised.

        ValueError:
            If data is empty, all NaN, or otherwise has no sensible ordering,
            then this should raise a ValueError.

        """
        raise NotImplementedError


    ### Trait defaults #######################################################

    def _metadata_default(self):
        return {"selections":[], "annotations":[]}
