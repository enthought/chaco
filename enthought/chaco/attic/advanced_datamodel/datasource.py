"""
Defines the DataSource base class.
"""

from enthought.traits.api import Any, Dict, Enum, Event, HasTraits, Instance, List, This

from base import DimensionTrait

class DataSource(HasTraits):
    """
    DataSource is an abstract interface that must be supported by all classes
    in the plotting pipeline which act as providers of data.  The primary
    subclasses of DataSource are DataSeries and Filters.  For the most part,
    a DataSource looks like an array of values with an optional mask and
    metadata.
    
    Domain classes which need to be adapted to provide data to Chaco should
    implement DataSource.  In some cases, it might be easier to subclasses
    one of the concrete subclasses (ScalarData, PointData, etc.) and override
    the necessary functions.  These classes also serve as examples of how
    to property implement the DataSource interface.
    """
    
    # The upstream parent of this DataSource.  Can be None.
    parent = This
    
    # The dimensionality of the value at each index point.
    # Child classes should re-declare this trait as a ReadOnly trait with
    # the right default value.
    value_dimension = DimensionTrait
    
    # The dimensionality of the indices with which one indexes into this
    # Child classes should re-declare this trait as a ReadOnly trait with
    # the right default value.
    index_dimension = DimensionTrait
    
    # The level of reverse mapping that this DataSource is capable of.
    # All DataSources must be able to reverse-map a value back to a set
    # of indices.  The levels of granularity that this reverse map can
    # return are:
    #
    #   1. "object": a reference to the object containing the point
    #   2. "range": a tuple of (lower,upper) indices that bracket the point
    #   3. "precise": a single index representing the position of the point
    rmap_accuracy = Enum("object", "range", "precise")

    # A dictionary keyed on string values.  Some string values are reserved
    # and have standardized value types.
    # TODO: where to put descriptions of these standard metadata?
    metadata = Dict()
    
    # Event that fires when the data values change
    data_changed = Event
    
    # Event that fires when just the bounds change
    bounds_changed = Event
    
    # Event that fires when metadata structure is changed
    # TODO: make this work; it relies on traits Dicts firing events
    metadata_changed = Event
    
    # Event that fires when the upstream datasource to which this instance is
    # attached changes..
    parent_changed = Event
    
    # --- Abstract methods -----------------------------------------------
    
    def get_data(self):
        """get_data() -> data_array
        
        Returns a data array of dimensions self.dimension.  This data array
        should not be altered in-place, and the caller should assume it is
        read-only.  This data is contiguous and not masked.
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

    def reverse_map(self, pt, index=0, outside_returns_none=True):
        """reverse_map0(pt, index={0,1}, outside_returns_none=True) 
                    -> None | objref | ndx | tuple(ndx,ndx)
        
        Returns as accurate an index as possible for the given value point.  If
        the input point cannot be mapped to an index, then None is returned.
        This can occur on sparse 2D data, and reverse_map_threshold should be
        used.
        
        If the datasource has 2-dimensional values, then "index" specifies which
        axis to reverse-map along.  (pt still has to be of the right value
        dimension.)  If reverse mapping along both axes is desired, then
        use reverse_map_threshold().
        
        If the given value point corresponds to a range of indices and if
        rmap_accuracy is "range", then a tuple (start_ndx, end_ndx) is returned.
        Otherwise, if the given value point corresponds to multiple indices,
        then only the first index is returned.  In either case, if a given value
        point corresponds to multiple non-contiguous indices, only the first one
        is returned.
        
        If the given value point is outside the range of the data, then either
        the appropriate edge index is given or the value of None is returned,
        depending on the value of "outside_returns_none".
        """
        raise NotImplementedError

    def reverse_map_threshold(self, pt, threshold, outside_returns_none=True):
        """reverse_map_threshold(self, pt, threshold, outside_returns_none=True)
                                -> None | objref | ndx | tuple(ndx,ndx)
        
        Reverse maps with a threshold.  Behaves like reverse_map() but is much
        more useful for sparse 2D data.
        
        threshold is a value of type self.value_dimension.  The data space defined
        by the box (pt-threshold, pt+threshold) is searched for a value in the
        value data.
        
        This is not meant to be used for general-purpose reverse-mapping of polygons
        from dataspace.  For that purpose, an actual datamapper should be inserted
        into the data pipeline and the datamapper's specialized reverse-mapping
        methods should be used.
        """
        raise NotImplementedError
    
    def get_view(self):
        """get_view() -> ViewFilter instance
        
        Returns the most immediate upstream ViewFilter.  Can return None,
        in which case attempts to adjust the range or decorate the _dataspace_
        of this DataSource will fail.
        """
        # TODO: What is the behavior if there is more than 1 view/viewfilter
        #       in a pipeline?  What is the protocol for traversing that list
        #       of upstream views?
        return None


# EOF
