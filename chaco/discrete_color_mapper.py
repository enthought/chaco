from numpy import asarray, floor, ones

from traits.api import Array, Str, observe
from chaco.abstract_colormap import AbstractColormap
from chaco.data_range_1d import DataRange1D


class DiscreteColorMapper(AbstractColormap):
    """Very simple colormaper for categorical data

    This colormapper holds a palette of colors and expects to be given
    and array of integer values between 0 and the number of colors - 1.

    Values outside this range will be clipped.
    """

    #: the name of the colormap
    name = Str

    #: the palette of colors
    palette = Array(shape=(None, (3, 4)), dtype=float)

    #: the palette of colors adjusted for color depth
    _palette = Array(shape=(None, (3, 4)), dtype=float)

    #: the palette as uint8 values
    _uint8_palette = Array(shape=(None, (3, 4)), dtype="uint8")

    @classmethod
    def from_palette_array(cls, palette, **traits):
        """ Creates a discrete color mapper from a palette array. """
        palette = asarray(palette, dtype=float)
        # ignore range passed in and use fixed range instead
        traits.pop("range", None)
        range = DataRange1D(low=-0.5, high=len(palette) - 0.5)
        return cls(palette=palette, range=range, **traits)

    @classmethod
    def from_colormap(cls, colormap, steps, **traits):
        """ Creates a discrete color mapper from a palette array. """
        from chaco.data_range_1d import DataRange1D

        traits.pop("range", None)
        range = DataRange1D(low=-0.5, high=steps - 0.5)
        # create the colormapper and sample from it
        colormapper = colormap(range, steps=steps)
        palette = colormapper.color_bands
        return cls(palette=palette, **traits)

    def map_screen(self, data):
        """ Maps an array of data to an array of colors """
        return self._palette[self.map_index(data)]

    def map_index(self, data):
        """ Maps an array of data to an array of indexes into the palette """
        index = asarray(data).round()
        index = index.clip(0, len(self.palette) - 1).astype(int, copy=False)
        return index

    def map_uint8(self, data):
        """ Maps an array of data to an array of colors """
        return self._uint8_palette[self.map_index(data)]

    def reverse_colormap(self):
        """ Reverses the palette of this colormap. """
        self.palette = self.palette[::-1]

    @observe("palette, color_depth")
    def _update_palettes(self, event):
        """ Generate palette adjusted for color depth and fire update event"""
        n_colors, n_components = self.palette.shape
        if self.color_depth == "rgba":
            if n_components == 3:
                palette = ones(shape=(n_colors, 4))
                palette[:, :3] = self.palette
            else:
                palette = self.palette
        else:
            palette = self.palette[:, :3]
        palette = palette.clip(0.0, 1.0)

        uint8_palette = floor(palette * 256).clip(0, 255).astype("uint8")

        self._palette = palette
        self._uint8_palette = uint8_palette
        self.updated = True
