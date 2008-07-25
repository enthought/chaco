"""
Defines the ViewFilter and ViewFilter2D classes.
"""

from numpy import array, compress, concatenate, ones, zeros

from enthought.traits.api import Any, Delegate, Enum, false, Instance, Property, true

from base import bin_search, SortOrderTrait
from filters import AbstractFilter
from datarange import AbstractRange, DataRange, DataRange2D
from dataview import DataView


class BaseViewFilter(AbstractFilter):
    """
    ViewFilters are basically range filters with references to a parent DataView.
    They are one of the few DataSource subclasses to provide a concrete
    implementation of get_view().  Any data pipeline containing a ViewFilter
    will return a DataView when get_view() is called on a downstream DataSource.
    Callers can then manipulate the shared range, selections, etc.
    
    The primary difference between a ViewFilter and a RangeFilter is that
    multiple ViewFilters connected to a single DataView will behave reasonably
    in concert, whereas RangeFilters are meant for programmatically controlling
    the output range of a data pipeline.
    
    Downstream data consumers that wish to display shared metadata residing
    in the view must look through it manually; there is no magical merging
    of the parent DataSource's metadata with the shared DataView metadata.
    
    This base class defines the protected interface between ViewFilters and
    DataViews (consisting of traits and methods) and provides implementations
    for some DataSource interface methods.
    """

    #------------------------------------------------------------------------
    # Public traits
    #------------------------------------------------------------------------

    # Delegate the traits we're not going to change/intercept
    value_dimension = Delegate("parent")
    index_dimension = Delegate("parent")
    metadata = Delegate("parent")

    # Even though we are doing a range restriction, we don't change the
    # nature of how reverse mapping is done, so the rmap_accuracy doesn't
    # change from our parent.
    rmap_accuracy = Delegate("parent")

    view = Property(Instance(DataView))

    
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # Our parent view
    _view = Instance(DataView)

    
    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, dataview, **traits):
        """__init__(dataview, **traits)
        
        Creates this viewfilter as a child of dataview.  An Upstream (parent)
        DataSource can be specified with the "parent=" keyword argument.
        """
        AbstractFilter.__init__(self, **traits)
        self.view = dataview
        return

    def __del__(self):
        if self._view is not None:
            self._view._remove_filter(self)

    def get_view(self):
        # Part of the DataSource interface
        return self._view


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------
    
    def _view_range_changed(self):
        # Trait event handler for when self._view.range changes.
        self.bounds_changed = True
        return
    
    def _view_metadata_changed(self):
        # Trait event handler for when self._view.metadata changes.
        # TODO: metadata_changed event does not currently fire, and we have
        #       no good way of merging/unifying the metadata from the View
        #       and inherits from upstream datasources.
        return


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _get_view(self):
        return self._view

    def _set_view(self, dataview):
        """set_dataview(dataview: DataView)
        
        Re-parents this viewfilter from one dataview to another while keeping
        the rest of the data pipeline intact.  If dataview is None, removes
        this ViewFilter from its parent DataView.
        """
        if self.parent is not None:
            # we need a valid upstream DataSource since these are delegates
            if self.value_dimension != dataview.dimension:
                raise ValueError, "Mismatched dimensions"
        
        if self._view is not None:
            # unhook the previous event notifier
            self._view.on_trait_event(self._view_metadata_changed, "metadata_changed", True)
            self._view._remove_filter(self)
            
        self._view = dataview
        self._view._add_filter(self)
        self._view.range.on_trait_event(self._view_metadata_changed, "metadata_changed")
        
        # manually call our own event handlers
        self._view_range_changed()
        self._view_metadata_changed()
        return
    


class ViewFilter(BaseViewFilter):
    """
    A ViewFilter for 1-dimensional datasources.
    """

    # Although the general DataSource interface does not define any notion of
    # sorting order for data, the vast majority of uses of ViewFilter will be
    # with ScalarData and PointData dataseries, which *do* support sorting.
    # Consequently, we define a sort_order trait and either propagate the
    # value downstream.
    sort_order = SortOrderTrait


    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    _cache_valid = false
    _cached_indices = Any  # (start, end) indices; only works for sorted data
    _cached_mask = Any
    _cached_data = Any

    #------------------------------------------------------------------------
    # DataSource and AbstractFilter interface
    #------------------------------------------------------------------------
    
    def get_data(self):
        self._cache_data()
        if self.sort_order != "none":
            ret_data = self._cached_data[self._cached_indices[0]:self._cached_indices[1]+1]
        else:
            ret_data = compress(self._cached_mask, self._cached_data)
        return ret_data
    
    def get_data_mask(self):
        self._cache_data()
        return self._cached_data, self._cached_mask
    
    def get_size(self):
        self._cache_data()
        indices = self._cached_indices
        return indices[1]-indices[0]
    
    def get_bounds(self):
        data = self.get_data()
        return min(data), max(data)
    
    def _parent_changed(self, oldparent, newparent):
        if oldparent is not None and newparent is not None:
            if newparent.value_dimension != oldparent.value_dimension or \
               newparent.index_dimension != oldparent.index_dimension:
                raise ValueError, "Mismatched dimensions"
        self._invalidate_cache()
        if hasattr(newparent, "sort_order"):
            self.sort_order = newparent.sort_order
        BaseViewFilter._parent_changed(self, oldparent, newparent)
        return
    
    def _parent_data_changed(self):
        # invalidate any cached information about the data
        self._invalidate_cache()
        self.data_changed = True
        return

    def _parent_bounds_changed(self):
        # We ignore parent bounds changes.  This may lead to undesirable behavior,
        # but for the time being I don't see it being a problem.  (ViewFilters
        # should be the only source of bounds_changed events, anyway)
        pass


    #------------------------------------------------------------------------
    # BaseViewFilter interface
    #------------------------------------------------------------------------
    
    def _notify_range_changed(self):
        self._invalidate_cache()
        self._calculate_bounds(self.get_data())
        self.bounds_changed = True
        return
        
    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _invalidate_cache(self):
        self._cache_valid = False
        self._cached_indices = None
        self._cached_mask = None
        return

    def _cache_data(self):
        if not self._cache_valid:
            self._calculate_bounds(self.parent.get_data())
        return

    def _calculate_bounds(self, data):
        """
        Calculates the various cached index bounds and masks for the current
        input data and view.range.  This always returns the *bounding points*,
        that is, one point to the outside of the bounds in view.range.  This
        ensures that line plots, etc. which stretch outside the view range
        will continue to the edge of the screen.
        """
        if self.sort_order == "none":
            raise NotImplementedError
        else:
            if self.sort_order == "ascending":
                min_index = 0
                max_index = len(data)-1
                order = 1
            elif self.sort_order == "descending":
                min_index = len(data)-1
                max_index = 0
                order = -1
            
            max_val = data[max_index]
            min_val = data[min_index]
            
            # short-circuit for all-out or all-in cases
            if (max_val < self._view.range.low) or (min_val > self._view.range.high):
                self._cached_mask = array([])
                self._cached_indices = None
            elif (max_val <= self._view.range.high) and (min_val >= self._view.range.low):
                self._cached_mask = ones(len(data))
                self._cached_indices = (0, len(data)-1)
            else:
                # subtract 1 to grab an extra point outside the region
                start = bin_search(data, self._view.range.low, order) - 1
                if start < 0:
                    start = 0
                
                # bin_search usually returns the cell index of the largest
                # value less than the search value, but if the value of a
                # cell matches the search value exactly, that cell is returned.
                # Thus, we usually have to add 1 to the value of "end".  We then
                # add another 1 to get an extra point outside the region.
                end = bin_search(data, self._view.range.high, order)
                last_index = len(data) - 1
                if end == -1:
                    end = last_index
                else:
                    end += 2
                    if end > last_index:
                        end = last_index
                
                # generate the mask
                mask_arrays = []
                if start != 0:
                    mask_arrays.append( zeros(start) )
                mask_arrays.append( ones(end-start+1) )
                if end < last_index:
                    mask_arrays.append( zeros(last_index-end+1) )
                
                self._cached_mask = concatenate(mask_arrays)
                self._cached_indices = (start, end)
        
        self._cached_data = data
        self._cache_valid = True
        return



class ViewFilter2D(BaseViewFilter):
    """
    A ViewFilter for 2-dimensional datasources.
    """

    pass



# EOF
