"""
Defines the DataView class.
"""

from enthought.traits.api import Dict, Event, HasTraits, Instance, List, Property

from base import DimensionTrait
from datarange import AbstractRange, DataRange, DataRange2D

class DataView(HasTraits):
    """
    A DataView represents a "window" into data space.  It is characterized by a
    range and decorators (e.g. selections and annotations).  A DataView can
    serve as a shared "window" for multiple DataSources because it does not
    fit directly into the data pipeline.  Instead, it produces associated
    ViewFilter instances which can be inserted into the data pipeline.
    
    Child ViewFilters are of the same dimension as the DataView.
    """

    # Since pipelines have dimensionality, a DataView must create ViewFilters
    # of matching dimension.  Although we use DimensionTrait here, the
    # dimensionality of the value space is what matters, so 'point' and 'image'
    # DimensionTraits are treated the same.
    dimension = DimensionTrait
    
    # The range that's shared amongst all child ViewFilters.
    range = Instance("AbstractRange")
    
    # The metadata on a DataView is shared among all of DataSources that
    # are viewed using it.
    metadata = Dict
    
    #------------------------------------------------------------------------
    # Events
    # These are not used internally by the classes in the data pipeline,
    # but instead allow external classes to get notified about things
    # changing.  (Updates can be forced by calling methods on the dataview.)
    #------------------------------------------------------------------------
    
    # Whenever the range bounds change, we fire this event.
    range_changed = Event
    
    # This event is fired whenever the list of viewfilters is changed.
    viewfilters_changed = Event
    
    # TODO: somehow tap into metadata so we get notified when its contents
    #       get changed
    metadata_changed = Event
    
    
    # --- Private traits -------------------------------------------------
    
    # A list of the ViewFilters this DataView controls.
    _viewfilters = List      # List(AbstractViewFilter)


    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------
    
    def __init__(self, dimension, metadata={}):
        """__init__(dimension: DimensionTrait, metadata={})
        
        Creates a new DataView with the given dimensionality.
        """
        self.dimension = dimension
        if dimension == "scalar":
            self.range = DataRange(self)
        else:
            self.range = DataRange2D(self)
        return
    

    def refresh_range(self):
        """
        Updates the shared range object given the values of the datasources
        attached to viewfilters.
        """
        self.range.refresh()
        return

    
    #------------------------------------------------------------------------
    # Private/protected methods
    #------------------------------------------------------------------------

    def _add_filter(self, viewfilter):
        # adds a filter to this DataView; called by ViewFilter
        self._viewfilters.append(viewfilter)
        self.viewfilters_changed = True
        self.refresh_range()
        return
    
    def _remove_filter(self, viewfilter):
        # removes a filter from this DataView; called by ViewFilter
        self._viewfilters.remove(viewfilter)
        self.viewfilters_changed = True
        self.refresh_range()
        return

    #------------------------------------------------------------------------
    # Notifier callbacks
    # Methods that are called by associated objects when they are updated
    #------------------------------------------------------------------------

    def _notify_viewfilter_updated(self, vf=None):
        # Notifies us that a particular viewfilter's data has changed, or
        # that the list of viewfilters has changed (if vf==None).
        
        # Let our range know that the viewfilters list has changed:
        self.range._notify_viewfilter_updated(vf)
        return
        
    
    def _notify_range_updated(self):
        # Let our viewfilters know that the range bounds have updated
        for vf in self._viewfilters:
            vf._notify_range_changed()
        return


# EOF
