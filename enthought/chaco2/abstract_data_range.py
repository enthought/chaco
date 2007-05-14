"""
Defines AbstractRange
"""

# Enthought library imports
from enthought.traits.api import Event, Float, HasTraits, Instance, List, Trait

# Local relative imports
from abstract_data_source import AbstractDataSource


class AbstractDataRange(HasTraits):
    """
    Ranges represent sub-regions of data space.  They support "autoscaling"
    by querying their associated DataSources.
    """
    
    # The list of datasources to which this range responds
    sources = List(Instance(AbstractDataSource))
    
    # These are the actual values of the lower and upper bound of this range.
    # To set them, use low_setting and high_setting.  (Setting these directly
    # just calls the setter for low_setting and high_setting.)
    # Although the default values specified here are 0 and 1.0, subclasses
    # can redefine them.  Also, subclasses can redefine the type to
    # correspond to their dimensionality.
    low = Float(0.0)
    high = Float(1.0)
    
    low_setting = Trait('auto', 'auto', Float)
    high_setting = Trait('auto', 'auto', Float)

    # Event that gets fired when the actual bounds values change; the value
    # of the event is a tuple (low_bound, high_bound)
    updated = Event

    #------------------------------------------------------------------------
    # Abstract methods that subclasses must implement
    #------------------------------------------------------------------------
    
    def clip_data(self, data):
        """
        Given an array of data values of the same dimensionality as the range,
        returns a list of data values that are inside the range.
        """
        raise NotImplementedError

    def mask_data(self, data):
        """
        Given an array of data values of the same dimensionality as the range,
        returns a mask array of the same length as data, and filled with 1s and
        0s corresponding to whether the data value at that index was inside
        or outside the range.
        """
        raise NotImplementedError

    def bound_data(self, data):
        """
        Given an array of data values of the same dimensionality as the range,
        returns a tuple of indices (start, end) corresponding to the first and
        last elements of the first run of data that falls within the range.
        For monotonic data, this basically returns the first and last elements
        that fall within the range; for non-monotonic data, this method
        really shouldn't be used, but if it is, it returns the first and last
        elements of the first "chunk" of data that falls within the range.
        """
        raise NotImplementedError
    
    def set_bounds(self, *new_bounds):
        """
        Sets all the bounds of the range simultaneously.  Since each bounds
        change probably fires an event, this allows tools to set all range
        elements in a single, atomic step.  new_bounds should be a tuple of
        (low, high), where the dimensionality and cardinality of new_bounds
        depends on the specific subclass.

        This not only reduces the number of spurious events (e.g. the ones
        that result from having to set both 'high' and 'low'), but also
        allows listeners to differentiate between translation and resize.
        """
        raise NotImplementedError
    
    def _refresh_bounds(self):
        """
        Resets the values of the bounds depending on the datasources
        referenced by the range.  Only called if one of the bounds
        settings is "auto".
        """
        raise NotImplementedError

