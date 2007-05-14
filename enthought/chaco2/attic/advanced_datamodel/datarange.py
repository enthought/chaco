"""
Defines AbstractRange, DataRange, and DataRange2D.
"""

from enthought.traits.api import Any, Array, Delegate, Event, Float, HasTraits, \
                             Instance, Property, Trait

from enthought.chaco2.base import PointTrait
import pdb

# Ideally we'd be able to handle true -INF and +INF, but for now just use
# extremely large values which are unlikely to occur in real life.
INF = 2e500

class AbstractRange(HasTraits):
    """
    Ranges are used by DataViews to encapsulate the representation of
    sub-regions of data space, shared among multiple data series.  They
    support "autoscaling" by querying the associated ViewFilters.
    
    Ranges are not meant to be used directly by anything in Chaco except
    the DataView.  They are not meant to be dynamically added and removed
    from DataViews.
    """
    
    # These are the actual values of the lower and upper bound of this range.
    # To set them, use low_setting and high_setting.  (Setting these directly
    # just calls the setter for low_setting and high_setting.)
    # Although the default values specified here are 0 and 1.0, subclasses
    # can redefine them.
    low = Float(0.0)
    high = Float(1.0)
    
    low_setting = Trait('auto', Float)
    high_setting = Trait('auto', Float)

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    _view = Any    # Instance("DataView")
    
    _viewfilters = Delegate("_view")

    
    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------
    
    def __init__(self, view, **kwtraits):
        """__init__(self, view: DataView, **traits)
        
        Initializes the DataRange with a DataView and, optionally,
        a list of traits defined using keyword arguments.
        """
        HasTraits.__init__(self, **kwtraits)
        self._view = view
        return

    def reset(self):
        """
        Resets the bounds of this range.
        """
        self._high_setting = 'auto'
        self._low_setting = 'auto'
        self._refresh_bounds()
        return

    def refresh(self):
        """
        If any of the bounds are 'auto', this refreshes the actual low and high
        values from the set of viewfilters' datasources.
        """
        if 'auto' not in (self._low_setting, self._high_setting):
            return
        else:
            self._refresh_bounds()
        return

    #------------------------------------------------------------------------
    # Abstract methods that subclasses must implement
    #------------------------------------------------------------------------
    
    def _refresh_bounds(self):
        raise NotImplementedError

    #------------------------------------------------------------------------
    # Notification methods
    #------------------------------------------------------------------------
    
    def _notify_viewfilter_updated(self, vf=None):
        # Notifies us that a particular viewfilter's data has changed, or
        # that the list of viewfilters has changed (if vf==None).
        
        # TODO: maybe we can do something more intelligent here in the
        #       future; for now, just recompute our bounds
        self._refresh_bounds()
        return


class DataRange(AbstractRange):
    
    low = Property(Float)
    high = Property(Float)
    
    low_setting = Property(Trait('auto', Float))
    high_setting = Property(Trait('auto', Float))


    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # The "_setting" attributes correspond to what the user has "set"; the
    # "_value" attributes are the actual numerical values for the given
    # setting.
    _low_setting = Trait('auto', Float)
    _low_value = Float
    _high_setting = Trait('auto', Float)
    _high_value = Float
    
    
    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------
    
    def __init__(self, view, **kwtraits):
        if "low" not in kwtraits:
            self._low_value = -INF
        if "high" not in kwtraits:
            self._high_value = INF
        AbstractRange.__init__(self, view, **kwtraits)
        return

    
    #------------------------------------------------------------------------
    # Private methods (getters and setters)
    #------------------------------------------------------------------------

    def _get_low(self):
        return self._low_value
    
    def _set_low(self, val):
        return self._set_low_setting(val)
    
    def _get_low_setting(self):
        return self._low_setting
    
    def _set_low_setting(self, val):
        if self._low_setting != val:
            self._low_setting = val
            if val == 'auto':
                val = min([v.get_bounds() for v in self._viewfilters])
            if self._low_value != val:
                self._low_value = val
                self._view._notify_range_updated()
        return

    def _get_high(self):
        return self._high_value
    
    def _set_high(self, val):
        return self._set_high_setting(val)
    
    def _get_high_setting(self):
        return self._high_setting
    
    def _set_high_setting(self, val):
        if self._high_setting != val:
            self._high_setting = val
            if val == 'auto':
                val = max([v.get_bounds() for v in self._viewfilters])
            if self._high_value != val:
                self._high_value = val
                self._view._notify_range_updated()
        return

    def _refresh_bounds(self):
        
        bounds_list = [v.get_bounds() for v in self._viewfilters]
        changed = False
        
        mins, maxes = zip(*bounds_list)
        
        if self._low_setting == 'auto':
            tmp = min(mins)
            if tmp != self._low_value:
                self._low_value = tmp
                changed = True
                
        if self._high_setting == 'auto':
            tmp = max(maxes)
            if tmp != self._high_value:
                self._high_value = tmp
                changed = True
        
        if changed:
            self._view._notify_range_updated()
        return
    
    
    
class DataRange2D(AbstractRange):
    """
    Range on ImageData.  In a mathematically general sense, a 2D range is an
    arbitrary region in the plane.  Since this is much more difficult to
    implement well, we just support rectangular regions for now.
    """
    
    # These are the actual values of the lower and upper bound of this range.
    # To set them, use low_setting and high_setting.  (Setting these directly
    # just calls the setter for low_setting and high_setting.)
    low = Property(Array)    # (2,) array of lower-left x,y
    high = Property(Array)   # (2,) array of upper-right x,y
    
    low_setting = Property(Trait('auto', 'auto', Array))
    high_setting = Property(Trait('auto', 'auto', Array))

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # The "_setting" attributes correspond to what the user has "set"; the
    # "_value" attributes are the actual numerical values for the given
    # setting.
    _low_setting = Trait('auto', 'auto', Array)
    _low_value = Float
    _high_setting = Trait('auto', 'auto', Array)
    _high_value = Float





# EOF
