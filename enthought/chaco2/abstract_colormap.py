
from enthought.traits.api import Enum, HasTraits, Instance

from data_range_1d import DataRange1D

class AbstractColormap(HasTraits):
    """
    A ColorMap maps from scalar values to color values.
    """
    
    # These define the data-space bounds of the mapper
    range = Instance(DataRange1D)
    
    # The color depth of the colors we use.
    color_depth = Enum('rgba', 'rgb')
    
    
    def map_screen(self, val):
        """
        map_screen(val) -> color
        
        Maps a single value to a single color.  Color is represented either as
        a length-3 array or length-4 array depending on the colordepth setting.
        """
        raise NotImplementedError()
    
    def map_data(self, ary):
        """
        map_data(ary) -> color_array
        
        Returns an array of values containing the colors mapping to ary.
        If the input ary is NxM, the returned array is NxMx3 or NxMx4
        depending on what the colordepth of the colormap is set to.
        """
        raise NotImplementedError()

    def map_index(self, ary):
        """
        map_index(ary) -> index into color_bands
        
        Like map_array(), but returns an array of indices into the colormap's
        color bands instead of an array of colors.  If the input is
        NxM, then output is NxM integer indices.
        
        This function might not apply to all colormaps.  Ones that cannot
        define a static set of color bands (e.g. function-defined colormaps)
        will not be able to implement this function.
        """
        raise NotImplementedError()


# EOF
