"""
PlotData objects put together multiple DataSources in a way that is compatible
with various Renderers.
"""

from enthought.traits.api import Any, Delegate, HasTraits, Instance, List, \
                             Property, ReadOnly

from base import DimensionTrait
from datasource import DataSource
from dataview import DataView
from datarange import AbstractRange

class AbstractPlotData(HasTraits):
    """
    PlotData is a pairing of index DataSeries with value DataSeries.  PlotData
    subclasses are tailored for certain categories of plots and renderers.  
    The actual types for index, value, and the multiplicity of index and value
    DataViews depends on the subclass.
    """
    
    index = Instance(DataSource)
    index_dimension = DimensionTrait

    values = List(DataSource)
    value_dimension = DimensionTrait

    def add_value(self, value):
        raise NotImplementedError
    
    def remove_value(self, value):
        raise NotImplementedError


class XYData(AbstractPlotData):
    index_dimension = ReadOnly('scalar')
    value_dimension = ReadOnly('scalar')

    index = Instance(DataView)
    value = Instance(DataView)

    index_range = Delegate('index', 'range')
    value_range = Delegate('value', 'range')


class MultiXYData(AbstractPlotData):
    """
    PlotData with a single index and multiple values.
    """
    index_dimension = ReadOnly('scalar')
    value_dimension = ReadOnly('scalar')
    
    index = Instance(DataSource)
    values = List(Instance(DataSource))
    
    # The value range is not a delegate because we need to aggregate the
    # ranges from all the value DataViews in our own way.
    
    # TODO: The value range *should* just be the same as the range on
    #       any of the values.  In fact, each PlotData should command its
    #       own view.  Two PlotData may be connected to the same view,
    #       but then they will both control it.  So there should be an
    #       index view and a value view.
    
    index_range = Delegate('index', 'range')
    value_range = Property(Instance(AbstractRange))
    
    # This shadow trait computes the range encompassing the ranges of all the
    # values.
    _value_range = Instance(AbstractRange)

    def __init__(self, index=None, values=[]):
        self.index = index
        self.values = values
        for value in values:
            value.view.on_trait_event(self._update_range, "range_changed", True)
        
        self._value_range = DataRange()
        self._update_range()
        return

    def _get_value_range(self):
        return self._value_range
    
    def _update_range(self):
        value_range = self._value_range
        
        # recalculates the locally-stored range object
        if value_range.low_setting != 'auto' and value_range.high_setting != 'auto':
            # Both upper and lower bounds are hard-set by the user, so don't do anything.
            return
        
        low = value_range.low
        high = value_range.high
        for value in self.values:
            if value.range.low < low:
                low = value.range.low
            if value.range.high > high:
                high = value.range.high
        
        if value_range.low_setting == 'auto':
            value_range._low_value = low
        else:
            value_range.low = low
        
        if value_range.high_setting == 'auto':
            value_range._high_value = high
        else:
            value_range.high = high
        return


class ImageData(AbstractPlotData):
    pass
    
class ImageData2D(AbstractPlotData):
    pass

class PointData(AbstractPlotData):
    pass

class PointData2D(AbstractPlotData):
    pass


