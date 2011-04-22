"""
Defines the base class for data ranges.
"""

# Enthought library imports
from traits.api import Event, Float, HasTraits, Instance, List, Trait

# Local relative imports
from abstract_data_source import AbstractDataSource


class AbstractDataRange(HasTraits):
    """ Abstract class for ranges that represent sub-regions of data space.

    They support "autoscaling" by querying their associated data sources.
    """

    # The list of data sources to which this range responds.
    sources = List(Instance(AbstractDataSource))

    # The actual value of the lower bound of this range. To set it, use
    # low_setting. (Setting this attribute directly just calls the setter for
    # low_setting.) Although the default value is specified as 0.0, subclasses
    # can redefine the default. Also, subclasses can redefined the type to
    # correspond to their dimensionality.
    low = Float(0.0)

    # The actual value of the upper bound of this range. To set it, use
    # high_setting. (Setting this attribute directly just calls the setter for
    # high_setting.) Although the default value is specified as 1.0, subclasses
    # can redefine the default. Also, subclasses can redefined the type to
    # correspond to their dimensionality.
    high = Float(1.0)

    # Setting for the lower bound of this range.
    low_setting = Trait('auto', 'auto', Float)
    # Setting for the upper bound of this range.
    high_setting = Trait('auto', 'auto', Float)

    # Event that is fired when the actual bounds values change; the value
    # of the event is a tuple (low_bound, high_bound)
    updated = Event

    #------------------------------------------------------------------------
    # Concrete methods
    #------------------------------------------------------------------------

    def __init__(self, *sources, **kwargs):
        if len(sources) > 0:
            if 'sources' in kwargs:
                raise RuntimeError("Datasources for data range provided as "
                                   "both positional and keyword arguments.")
            else:
                kwargs['sources'] = list(sources)
        super(AbstractDataRange, self).__init__(**kwargs)


    #------------------------------------------------------------------------
    # Abstract methods that subclasses must implement
    #------------------------------------------------------------------------

    def clip_data(self, data):
        """ Returns a list of data values that are within the range.

        Given an array of data values of the same dimensionality as the range,
        returns a list of data values that are inside the range.
        """
        raise NotImplementedError

    def mask_data(self, data):
        """ Returns a mask array, indicating whether values in the given array
        are inside the range.

        Given an array of data values of the same dimensionality as the range,
        this method returns a mask array of the same length as data, filled
        with 1s and 0s corresponding to whether the data value at that index
        is inside or outside the range.
        """
        raise NotImplementedError

    def bound_data(self, data):
        """ Returns a tuple of indices for the start and end of the first run
        of data that falls within the range.

        Given an array of data values of the same dimensionality as the range,
        returns a tuple of indices (start, end) corresponding to the first and
        last elements of the first run of data that falls within the range.
        For monotonic data, this basically returns the first and last elements
        that fall within the range. Using this method is not advised for
        non-monotonic data; in that case, it returns the first and last
        elements of the first "chunk" of data that falls within the range.
        """
        raise NotImplementedError

    def set_bounds(self, *new_bounds):
        """ Sets all the bounds of the range simultaneously.

        Because each bounds change probably fires an event, this method allows
        tools to set all range elements in a single, atomic step.

        Parameters
        ----------
        new_bounds : a tuple of (low, high)
            The new bounds for the range; the dimensionality and cardinality
            depend on the specific subclass.

        This method not only reduces the number of spurious events (the
        ones that result from having to set both **high** and **low**), but also
        allows listeners to differentiate between translation and resize
        operations.
        """
        raise NotImplementedError

    def _refresh_bounds(self):
        """ Resets the values of the bounds depending on the data sources
        referenced by the range.

        This method is called only if one of the bounds settings is "auto".
        """
        raise NotImplementedError

