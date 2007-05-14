"""
The Filter interface is one of the two basic components of the Chaco data-
manipulation pipeline.  (Mapper is the other.)

This module defines the AbstractFilter interface and some of the common
Filter subclasses.
"""

from enthought.traits.api import Enum, Instance, List

from datasource import DataSource

class AbstractFilter(DataSource):
    """
    DataFilters of different dimensionalities will have very different
    interfaces, so this base class can't declare much.  The defining characteristic
    of a filter is that it has both an input and an output (as opposed to a
    DataSeries, which only has output, or a PlotData, which only has input).
    
    Thus, there are basic implementations of methods for handling propagation
    of events down the pipeline.
    """
    
    # --- Public methods -------------------------------------------------
    
    def is_masked(self):
        # Most filters will return masks with their values.
        return True

    def get_view(self):
        # Most filters do not reference DataViews.
        return self.parent.get_view()


    # --- Event handlers -------------------------------------------------
    
    def _parent_changed(self, oldparent, newparent):
        if oldparent is not None:
            oldparent.on_trait_event(self._parent_data_changed, "data_changed", True)
            oldparent.on_trait_event(self._parent_bounds_changed, "bounds_changed", True)
            oldparent.on_trait_event(self._parent_metadata_changed, "metadata_changed", True)
        if newparent is not None:
            newparent.on_trait_event(self._parent_data_changed, "data_changed")
            newparent.on_trait_event(self._parent_bounds_changed, "bounds_changed")
            newparent.on_trait_event(self._parent_metadata_changed, "metadata_changed")
        
        # If our parent has changed, then invariably our data and metadata have changed.
        self.data_changed = True
        self.metadata_changed = True
        return

    def _parent_data_changed(self):
        # Propagate the event downstream.
        self.data_changed = True
        
    def _parent_bounds_changed(self):
        # Propagate the event downstream.
        self.bounds_changed = True
        
    def _parent_metadata_changed(self):
        # Propagate the event downstream.
        self.metadata_changed = True
    



class ComplexFilter(AbstractFilter):
    """
    A composition of filters using the logical operations AND, OR, NOT and XOR.
    """
    
    filters = List(AbstractFilter)
    operation = Enum("and", "or", "not", "xor")


# EOF
