""" Defines the base class for color maps
"""
from traits.api import Enum, Event, HasTraits, Instance

from .data_range_1d import DataRange1D

class AbstractColormap(HasTraits):
    """
    Abstract class for color maps, which map from scalar values to color values.
    """

    # The data-space bounds of the mapper.
    range = Instance(DataRange1D)

    # The color depth of the colors to use.
    color_depth = Enum('rgba', 'rgb')

    # A generic "update" event that generally means that anything that relies
    # on this mapper for visual output should do a redraw or repaint.
    updated = Event

    def map_screen(self, val):
        """
        map_screen(val) -> color

        Maps an array of values to an array of colors.  If the input array is
        NxM, the returned array is NxMx3 or NxMx4, depending on the
        **color_depth** setting.
        """
        raise NotImplementedError()

    def map_data(self, ary):
        """
        map_data(ary) -> color_array

        Returns an array of values containing the colors mapping to the values
        in *ary*. If the input array is NxM, the returned array is NxMx3 or
        NxMx4, depending on the **color_depth** setting.
        """
        # XXX this seems bogus: by analogy with AbstractMapper, this should map
        # colors to data values, and that will be generally hard to do well.
        # no subclass implements this - CJW
        raise NotImplementedError()

    def map_index(self, ary):
        """
        map_index(ary) -> index into color_bands

        This method is like map_screen(), but it returns an array of indices
        into the color map's color bands instead of an array of colors.  If the
        input array is NxM, then the output is NxM integer indices.

        This method might not apply to all color maps.  Ones that cannot
        define a static set of color bands (e.g., function-defined color maps)
        are not able to implement this function.
        """
        raise NotImplementedError()

    def map_uint8(self, val):
        """
        map_uint8(val) -> rgb24 or rgba32 color

        Maps a single value to a single color.  Color is represented as either
        length-3 or length-4 array of rgb(a) uint8 values, depending on the
        **color_depth** setting.
        """
        # default implementation (not efficient)
        return (self.map_screen(val)*255.0).astype('uint8')



# EOF
