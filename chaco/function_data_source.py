
from numpy import array

# Enthought library imports
from traits.api import Callable, Instance, on_trait_change

# Local, relative imports
from abstract_data_source import AbstractDataSource
from array_data_source import ArrayDataSource
from data_range_1d import DataRange1D


class FunctionDataSource(ArrayDataSource):

    # The function to call with the low and high values of the range.
    # It should return an array of values.
    func = Callable

    # A reference to a datarange
    data_range = Instance(DataRange1D)

    def __init__(self, **kw):
        # Explicitly call the AbstractDataSource constructor because
        # the ArrayDataSource ctor wants a data array
        AbstractDataSource.__init__(self, **kw)
        self.recalculate()

    @on_trait_change('data_range.updated')
    def recalculate(self):
        if self.func is not None and self.data_range is not None:
            newarray = self.func(self.data_range.low, self.data_range.high)
            ArrayDataSource.set_data(self, newarray)
        else:
            self._data = array([], dtype=float)

    def set_data(self, *args, **kw):
        raise RuntimeError("Cannot set numerical data on a FunctionDataSource")

    def set_mask(self, mask):
        # This would be REALLY FREAKING SLICK, but it's current unimplemented
        raise NotImplementedError

    def remove_mask(self):
        raise NotImplementedError


