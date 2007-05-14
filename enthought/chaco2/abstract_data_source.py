"""
Defines the base class for data sources
"""

from enthought.traits.api import Any, Dict, Event, false, HasTraits, Instance, true

# Local relative imports
from base import DimensionTrait

class AbstractDataSource(HasTraits):
    """
    AbstractDataSource is an abstract interface that must be implemented by
    anything supplying data to Chaco.  For the most part, a DataSource looks
    like an array of values with an optional mask and metadata.
    
    Chaco provides some basic DataSource implementations, ArrayDataSource and
    PointDataSource, and Array2dDataSource.  In most cases it will be easier to
    take the numeric data from a domain model and create these basic
    datasources.  In cases when this is not possible, domain classes (or an
    adapter) should be implement DataSource.
    """
    
    # The dimensionality of the value at each index point.
    # Child classes should re-declare this trait as a ReadOnly trait with
    # the right default value.
    value_dimension = DimensionTrait
    
    # The dimensionality of the indices with which one indexes into this
    # Child classes should re-declare this trait as a ReadOnly trait with
    # the right default value.
    index_dimension = DimensionTrait
    
    # A dictionary keyed on strings.  In general, maps to indices (or tuples
    # of indices, depending on value_dimension), as in the case of selections
    # and annotations.  Applications and renderers can add their own custom
    # metadata, but should avoid using keys that might result in name collision.
    metadata = Dict
    
    # Event that fires when the data values change
    data_changed = Event
    
    # Event that fires when just the bounds change
    bounds_changed = Event
    
    # Event that fires when metadata structure is changed
    metadata_changed = Event
    
    # Should the data that this datasource refers to be serialized when
    # we are serialized?
    persist_data = true
    
    #------------------------------------------------------------------------
    # Abstract methods
    #------------------------------------------------------------------------
    
    def get_data(self):
        """get_data() -> data_array
        
        Returns a data array of dimensions self.dimension.  This data array
        should not be altered in-place, and the caller should assume it is
        read-only.  This data is contiguous and not masked.

        In the case of structured (gridded) 2D data, may return two 1D 
        ArrayDataSources as an optimization
        """
        raise NotImplementedError
    
    def get_data_mask(self):
        """get_data_mask() -> (data_array, mask_array)
        
        Returns the full, raw, source data array and a corresponding binary
        mask array.  Both should be treated as read-only.
        
        The mask is a superposition of the masks of all upstream data sources.
        The length of the returned array may be much larger than what
        get_size() returns; the unmasked portion, however, should match what
        get_size() returns.
        """
        raise NotImplementedError
    
    def is_masked(self):
        """is_masked() -> bool
        
        Returns True if this DataSource's data should be retrieved using
        get_data_mask() instead of get_data().  (get_data() should still return
        data, but it may not be the expected data.)
        """
        raise NotImplementedError
    
    def get_size(self):
        """get_size() -> int
        
        Returns an integer estimate or the exact size of the dataset that
        get_data will return.  This is useful for downsampling.
        """
        raise NotImplementedError

    def get_bounds(self):
        """get_bounds() -> tuple(min_val, max_val)
        
        Returns a tuple (min, max) of the bounding values for the data source.
        In the case of 2D data, min and max are 2D points represent the bounding
        corners of a rectangle enclosing the data set.  Note that these values
        are not view-dependent, but represent intrinsic properties of the
        DataSource.
        
        If data is the empty set, then the min and max vals are 0.0.
        """
        raise NotImplementedError


    ### Persistence ###########################################################
    
    def _metadata_default(self):
        return {"selections":[], "annotations":[]}
    
    def __getstate__(self):
        state = super(AbstractDataSource,self).__getstate__()

        # everything but 'metadata'
        for key in ['value_dimension', 'index_dimension', 'persist_data']:
            if state.has_key(key):
                del state[key]

        return state
        
        
    
# EOF
