# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Defines the DataRange2D class.
"""

from numpy import compress, inf, transpose

# Enthought library imports
from traits.api import (
    Any,
    Bool,
    CFloat,
    Instance,
    Property,
    Trait,
    Tuple,
    observe,
)

# Local relative imports
from .base_data_range import BaseDataRange
from .data_range_1d import DataRange1D


class DataRange2D(BaseDataRange):
    """A range on (2-D) image data.

    In a mathematically general sense, a 2-D range is an arbitrary region in
    the plane.  Arbitrary regions are difficult to implement well, so this
    class supports only rectangular regions for now.
    """

    #: The actual value of the lower bound of this range. To set it, use
    #: **low_setting**.
    low = Property  # (2,) array of lower-left x,y
    #: The actual value of the upper bound of this range. To set it, use
    #: **high_setting**.
    high = Property  # (2,) array of upper-right x,y

    #: Property for the lower bound of this range (overrides AbstractDataRange).
    low_setting = Property
    #: Property for the upper bound of this range (overrides AbstractDataRange).
    high_setting = Property

    # The 2-D grid range is actually implemented as two 1-D ranges, which can
    # be accessed individually.  They can also be set to new DataRange1D
    # instances; in that case, the DataRange2D's sources are removed from
    # its old 1-D dataranges and added to the new one.

    #: Property for the range in the x-dimension.
    x_range = Property
    #: Property for the range in the y-dimension.
    y_range = Property

    #: Do "auto" bounds imply an exact fit to the data? (One Boolean per
    #: dimension) If False, the bounds pad a little bit of margin on either
    #: side.
    tight_bounds = Tuple(Bool(True), Bool(True))
    #: The minimum percentage difference between low and high for each
    #: dimension. That is, (high-low) >= epsilon * low.
    epsilon = Tuple(CFloat(1.0e-4), CFloat(1.0e-4))

    # ------------------------------------------------------------------------
    # Private traits
    # ------------------------------------------------------------------------

    # DataRange1D for the x-dimension.
    _xrange = Instance(DataRange1D, args=())
    # DataRange1D for the y-dimension.
    _yrange = Instance(DataRange1D, args=())

    # ------------------------------------------------------------------------
    # AbstractRange interface
    # ------------------------------------------------------------------------

    def clip_data(self, data):
        """Returns a list of data values that are within the range.

        Implements AbstractDataRange.
        """
        return compress(self.mask_data(data), data, axis=0)

    def mask_data(self, data):
        """Returns a mask array, indicating whether values in the given array
        are inside the range.

        Implements AbstractDataRange.
        """
        x_points, y_points = transpose(data)
        x_mask = (x_points >= self.low[0]) & (x_points <= self.high[0])
        y_mask = (y_points >= self.low[1]) & (y_points <= self.high[1])
        return x_mask & y_mask

    def bound_data(self, data):
        """Not implemented for this class."""
        raise NotImplementedError(
            "bound_data() has not been implemented for 2d pointsets."
        )

    def set_bounds(self, low, high):
        """Sets all the bounds of the range simultaneously.

        Implements AbstractDataRange.

        Parameters
        ----------
        low : (x,y)
            Lower-left corner of the range.
        high : (x,y)
            Upper right corner of the range.
        """
        self._do_set_low_setting(low, fire_event=False)
        self._do_set_high_setting(high)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def reset(self):
        """Resets the bounds of this range."""
        self.high_setting = ("auto", "auto")
        self.low_setting = ("auto", "auto")
        self.refresh()

    def refresh(self, event=None):
        """If any of the bounds is 'auto', this method refreshes the actual
        low and high values from the set of the view filters' data sources.
        """
        if "auto" not in self.low_setting and "auto" not in self.high_setting:
            # If the user has hard-coded bounds, then refresh() doesn't do
            # anything.
            return
        else:
            self._refresh_bounds()

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _refresh_bounds(self):
        self._xrange.refresh()
        self._yrange.refresh()

    # ------------------------------------------------------------------------
    # Property getters and setters
    # ------------------------------------------------------------------------

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

    def _do_set_high_setting(self, val, fire_event=True):
        self._xrange.high_setting = val[0]
        self._yrange.high_setting = val[1]

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
            source1d = getattr(source, dataname, None)
            if source1d:
                if oldrange:
                    oldrange.remove(source1d)
                if newrange:
                    newrange.add(source1d)

    # ------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------

    def _sources_items_changed(self, event):
        for source in event.removed:
            source.observe(self.refresh, "data_changed", remove=True)
        for source in event.added:
            source.observe(self.refresh, "data_changed")
        # the _xdata and _ydata of the sources may be created anew on every
        # access, so we can't just add/delete from _xrange and _yrange sources
        # based on object identity. So recreate lists each time:
        self._xrange.sources = [s._xdata for s in self.sources]
        self._yrange.sources = [s._ydata for s in self.sources]
        self.refresh()

    def _sources_changed(self, old, new):
        for source in old:
            source.observe(self.refresh, "data_changed", remove=True)
        for source in new:
            source.observe(self.refresh, "data_changed")
        # the _xdata and _ydata of the sources may be created anew on every
        # access, so we can't just add/delete from _xrange and _yrange sources
        # based on object identity. So recreate lists each time:
        self._xrange.sources = [s._xdata for s in self.sources]
        self._yrange.sources = [s._ydata for s in self.sources]
        self.refresh()

    @observe("_xrange.updated,_yrange.updated")
    def _set_updated(self, event):
        self.updated = True
