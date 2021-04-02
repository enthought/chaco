"""
Defines the AbstractDataSource class.
"""

from traits.api import Bool, Dict, Event, HasTraits

# Local relative imports
from .base import DimensionTrait


class AbstractDataSource(HasTraits):
    """This abstract interface must be implemented by any class supplying data
    to Chaco.

    Chaco does not have a notion of a "data format". For the most part, a data
    source looks like an array of values with an optional mask and metadata.
    If you implement this interface, you are responsible for adapting your
    domain-specific or application-specific data to meet this interface.

    Chaco provides some basic data source implementations. In most cases, the
    easiest strategy is to create one of these basic data source with the
    numeric data from a domain model. In cases when this strategy is not
    possible, domain classes (or an adapter) must implement AbstractDataSource.
    """

    #: The dimensionality of the value at each index point.
    #: Subclasses re-declare this trait as a read-only trait with
    #: the right default value.
    value_dimension = DimensionTrait

    #: The dimensionality of the indices into this data source.
    #: Subclasses re-declare this trait as a read-only trait with
    #: the right default value.
    index_dimension = DimensionTrait

    #: A dictionary keyed on strings.  In general, it maps to indices (or tuples
    #: of indices, depending on **value_dimension**), as in the case of
    #: selections and annotations.  Applications and renderers can add their own
    #: custom metadata, but must avoid using keys that might result in name
    #: collision.
    metadata = Dict

    #: Event that fires when the data values change.
    data_changed = Event

    #: Event that fires when just the bounds change.
    bounds_changed = Event

    #: Event that fires when metadata structure is changed.
    metadata_changed = Event

    #: Should the data that this datasource refers to be serialized when
    #: the datasource is serialized?
    persist_data = Bool(True)

    # ------------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------------

    def get_data(self):
        """get_data() -> data_array

        Returns a data array of the dimensions of the data source. This data
        array must not be altered in-place, and the caller must assume it is
        read-only.  This data is contiguous and not masked.

        In the case of structured (gridded) 2-D data, this method may return
        two 1-D ArrayDataSources as an optimization.
        """
        raise NotImplementedError

    def get_data_mask(self):
        """get_data_mask() -> (data_array, mask_array)

        Returns the full, raw, source data array and a corresponding binary
        mask array.  Treat both arrays as read-only.

        The mask is a superposition of the masks of all upstream data sources.
        The length of the returned array may be much larger than what
        get_size() returns; the unmasked portion, however, matches what
        get_size() returns.
        """
        raise NotImplementedError

    def is_masked(self):
        """is_masked() -> bool

        Returns True if this data source's data uses a mask. In this case,
        to retrieve the data, call get_data_mask() instead of get_data().
        If you call get_data() for this data source, it returns data, but that
        data might not be the expected data.
        """
        raise NotImplementedError

    def get_size(self):
        """get_size() -> int

        Returns an integer estimate or the exact size of the dataset that
        get_data() returns for this object.  This method is useful for
        down-sampling.
        """
        raise NotImplementedError

    def get_bounds(self):
        """get_bounds() -> tuple(min, max)

        Returns a tuple (min, max) of the bounding values for the data source.
        In the case of 2-D data, min and max are 2-D points that represent the
        bounding corners of a rectangle enclosing the data set.  Note that
        these values are not view-dependent, but represent intrinsic properties
        of the data source.

        If data is the empty set, then the min and max vals are 0.0.
        """
        raise NotImplementedError

    ### Persistence ###########################################################

    def _metadata_default(self):
        return {"selections": [], "annotations": []}

    def __getstate__(self):
        state = super(AbstractDataSource, self).__getstate__()

        # everything but 'metadata'
        for key in ["value_dimension", "index_dimension", "persist_data"]:
            if key in state:
                del state[key]

        return state
