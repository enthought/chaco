""" Defines the base class for color maps
"""
from enthought.traits.api import Enum, HasTraits, Instance

from data_range_1d import DataRange1D

class AbstractColormap(HasTraits):
    """
    Abstract class for color maps, which map from scalar values to color values.
    """

    # The data-space bounds of the mapper.
    range = Instance(DataRange1D)

    # The color depth of the colors to use.
    color_depth = Enum('rgba', 'rgb')


    def map_screen(self, val):
        """
        map_screen(val) -> color

        Maps a single value to a single color.  Color is represented as either
        a length-3 array or length-4 array, depending on the **color_depth**
        setting.
        """
        raise NotImplementedError()

    def map_data(self, ary):
        """
        map_data(ary) -> color_array

        Returns an array of values containing the colors mapping to the values
        in *ary*. If the input array is NxM, the returned array is NxMx3 or
        NxMx4, depending on the **color_depth** setting.
        """
        raise NotImplementedError()

    def map_index(self, ary):
        """
        map_index(ary) -> index into color_bands

        This method is like map_data(), but it returns an array of indices
        into the color map's color bands instead of an array of colors.  If the
        input array is NxM, then the output is NxM integer indices.

        This method might not apply to all color maps.  Ones that cannot
        define a static set of color bands (e.g., function-defined color maps)
        are not able to implement this function.
        """
        raise NotImplementedError()


# EOF
