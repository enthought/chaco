# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the FunctionDataSource class to create an ArrayDataSource from a
callable.
"""

from numpy import array

# Enthought library imports
from traits.api import Callable, Instance, observe

# Local, relative imports
from .abstract_data_source import AbstractDataSource
from .array_data_source import ArrayDataSource
from .data_range_1d import DataRange1D


class FunctionDataSource(ArrayDataSource):
    """A data source that lazily generates its data array from a callable.

    The signature of the :attr:`func` attribute is `func(low, high)` where
    `low` and `high` are attributes of the :attr:`data_range` attribute
    (instance of a :class:`DataRange1D`).

    This class does not listen to the array for value changes; if you need that
    behavior, create a subclass that hooks up the appropriate listeners.
    """

    #: The function to call with the low and high values of the range.
    #: It should return an array of values.
    func = Callable

    #: A reference to a datarange
    data_range = Instance(DataRange1D)

    def __init__(self, **kw):
        # Explicitly call the AbstractDataSource constructor because
        # the ArrayDataSource ctor wants a data array
        AbstractDataSource.__init__(self, **kw)
        self.recalculate()

    @observe("data_range.updated")
    def recalculate(self, event=None):
        if self.func is not None and self.data_range is not None:
            newarray = self.func(self.data_range.low, self.data_range.high)
            ArrayDataSource.set_data(self, newarray)
        else:
            self._data = array([], dtype=float)

    def set_data(self, *args, **kw):
        raise RuntimeError(
            "Cannot set numerical data on a {0}".format(self.__class__)
        )

    def set_mask(self, mask):
        # This would be REALLY FREAKING SLICK, but it's current unimplemented
        raise NotImplementedError

    def remove_mask(self):
        raise NotImplementedError
