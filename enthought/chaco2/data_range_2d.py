"""
Defines AbstractRange, DataRange, and DataRange2D.
"""

from math import ceil, floor, log
from numpy import arange, array, compress, concatenate, inf, ones, transpose, zeros

# Enthought library imports
from enthought.traits.api import Any, Array, Delegate, Event, false, CFloat, \
                                 HasTraits, \
                                 Instance, List, Property, Trait, true, Tuple

# Local relative imports
from base_data_range import BaseDataRange
from data_range_1d import DataRange1D


    
class DataRange2D(BaseDataRange):
    """
    Range on ImageData.  In a mathematically general sense, a 2D range is an
    arbitrary region in the plane.  Since this is much more difficult to
    implement well, we just support rectangular regions for now.
    """
    
    # These are the actual values of the lower and upper bound of this range.
    # To set them, use low_setting and high_setting.  (Setting these directly
    # just calls the setter for low_setting and high_setting.)
    low = Property  # (2,) array of lower-left x,y
    high = Property  # (2,) array of upper-right x,y
    
    low_setting = Property
    high_setting = Property

    # The 2D grid range is actually implemented as two 1D ranges, which can
    # be accessed individually.  They can also be set to new DataRange1D
    # instances; in that case, the DataRange2D's sources are removed from
    # its old 1D dataranges and added to the new one.
    x_range = Property
    y_range = Property
    
    tight_bounds = Tuple(true, true)
    epsilon = Tuple(CFloat(1.0e-4), CFloat(1.0e-4))

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # The "_setting" attributes correspond to what the user has "set"; the
    # "_value" attributes are the actual numerical values for the given
    # setting.
    _low_setting = Trait(('auto','auto'), Any)
    _low_value = Trait((-inf,-inf), Tuple(CFloat, CFloat))
    _high_setting = Trait(('auto', 'auto'), Any)
    _high_value = Trait((inf,inf), Tuple(CFloat, CFloat))

    _xrange = Instance(DataRange1D, args=())
    _yrange = Instance(DataRange1D, args=())

    #------------------------------------------------------------------------
    # AbstractRange interface
    #------------------------------------------------------------------------
    
    def clip_data(self, data):
        return compress(self.mask_data(data), data, axis=0)
    
    def mask_data(self, data):
        x_points, y_points = transpose(data)
        x_mask = (x_points >= self.low[0]) & (x_points <= self.high[0])
        y_mask = (y_points >= self.low[1]) & (y_points <= self.high[1])
        return x_mask & y_mask
    
    def bound_data(self, data):
        raise NotImplementedError, "bound_data() has not been implemented for 2d pointsets."

    def set_bounds(self, low, high):
        """ Low is (x,y) of lower-left corner, and high is (x,y) of upper right 
        """
        self._do_set_low_setting(low, fire_event=False)
        self._do_set_high_setting(high)

    def set_bounds(self, low, high):
        self._do_set_low_setting(low, fire_event=False)
        self._do_set_high_setting(high)


    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super(DataRange2D, self).__init__(*args, **kwargs)
        

    def reset(self):
        """
        Resets the bounds of this range.
        """
        self._high_setting = ('auto', 'auto')
        self._low_setting = ('auto', 'auto')
        self._refresh_bounds()

    def refresh(self):
        """
        If any of the bounds are 'auto', this refreshes the actual low and high
        values from the set of viewfilters' datasources.
        """
        if 'auto' not in self._low_setting and \
           'auto' not in self._high_setting:
            # If the user has hard-coded bounds, then refresh() doesn't do
            # anything.
            return
        else:
            self._refresh_bounds()



    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------
    
    def _do_set_high_setting(self, val, fire_event=True):
        self._xrange.high_setting = val[0]
        self._yrange.high_setting = val[1]
         
    def _refresh_bounds(self):
        self._xrange.refresh()
        self._yrange.refresh()


    #------------------------------------------------------------------------
    # Property getters and setters
    #------------------------------------------------------------------------

    def _get_low(self):
        return (self._xrange.low, self._yrange.low)
    
    def _set_low(self, val):
        return self._set_low_setting(val)
    
    def _get_low_setting(self):
        return (self._xrange.low_setting, self._yrange.low_setting)
    
    def _set_low_setting(self, val):
        self._do_set_low_setting(val)
        
    def _do_set_low_setting(self, val, fire_event=True):
        self._xrange.low_setting = val[0]
        self._yrange.low_setting = val[1]

    def _get_high(self):
        return (self._xrange.high, self._yrange.high)
    
    def _set_high(self, val):
        return self._set_high_setting(val)
    
    def _get_high_setting(self):
        return (self._xrange.high_setting, self._yrange.high_setting)

    def _set_high_setting(self, val):
        self._do_set_high_setting(val)
    
    def _get_x_range(self):
        return self._xrange

    def _set_x_range(self, newrange):
        self._set_1d_range("_xdata", self._xrange, newrange)
        self._xrange = newrange
    
    def _get_y_range(self):
        return self._yrange

    def _set_y_range(self, newrange):
        self._set_1d_range("_ydata", self._yrange, newrange)
        self._yrange = newrange

    def _set_1d_range(self, dataname, oldrange, newrange):
        # dataname is the name of the underlying 1d data source of the
        # ImageData instances in self.sources, e.g. "_xdata" or "_ydata"
        for source in self.sources:
            source1d = getattr(source, datanamem, None)
            if source1d:
                if oldrange:
                    oldrange.remove(source1d)
                if newrange:
                    newrange.add(source1d)
        return

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------
    
    def _sources_items_changed(self, event):
        self.refresh()
        for source in event.removed:
            source.on_trait_change(self.refresh, "data_changed", remove=True)
            self._xrange.remove(source._xdata)
            self._yrange.remove(source._ydata)
        for source in event.added:
            source.on_trait_change(self.refresh, "data_changed")
            self._xrange.add(source._xdata)
            self._yrange.add(source._ydata)
    
    def _sources_changed(self, old, new):
        self.refresh()
        for source in old:
            source.on_trait_change(self.refresh, "data_changed", remove=True)
            self._xrange.remove(source._xdata)
            self._yrange.remove(source._ydata)
        for source in new:
            source.on_trait_change(self.refresh, "data_changed")
            self._xrange.add(source._xdata)
            self._yrange.add(source._ydata)

    

