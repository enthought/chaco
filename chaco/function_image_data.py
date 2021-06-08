# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from numpy import array
from traits.api import Instance, Callable, observe
from .data_range_2d import DataRange2D
from .image_data import ImageData

# Adapted (ie. copied and modified) from function_data_source.

# Given the time frequently required for image manipulation,
# it would be awesome if there was a mechanism for returning
# partial results as they become available.


class FunctionImageData(ImageData):
    """A class that provides data for a 2-D image based upon the range
    supplied.  This class can be used as the data source for an image plot
    or contour plot.

    Computation should be fairly swift for acceptable interactive performance.
    """

    #: The function to call with the low and high values of the range
    #: in the x and y dimensions.  It should return either a 2-D array
    #: of numerical values, or an array of RGB or RGBA values (shape should
    #: be (n, m), (n, m, 3) or (n, m, 4)).
    func = Callable

    #: the 2D data_range required for the data shown
    data_range = Instance(DataRange2D)

    def __init__(self, **kw):
        super().__init__(**kw)
        # Explicitly construct the initial data set for ImageData
        self.recalculate()

    @observe("data_range.updated")
    def recalculate(self, event=None):
        if self.func is not None and self.data_range is not None:
            newarray = self.func(
                self.data_range.x_range.low,
                self.data_range.x_range.high,
                self.data_range.y_range.low,
                self.data_range.y_range.high,
            )
            ImageData.set_data(self, newarray)
        else:
            self._data = array([], dtype=float)

    def set_data(self, *args, **kw):
        raise RuntimeError("Cannot set numerical data on a FunctionImageData")

    def set_mask(self, mask):
        # This would be REALLY FREAKING SLICK, but it's currently unimplemented
        raise NotImplementedError

    def remove_mask(self):
        raise NotImplementedError
