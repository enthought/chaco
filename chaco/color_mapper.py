""" Defines the ColorMapper and ColorMapTemplate classes.
"""

# Major library imports
from numpy import arange, array, asarray, clip, divide, float32, int8, isinf, \
        isnan, ones, searchsorted, sometrue, sort, take, uint8, where, zeros, \
        linspace, ones_like

# Enthought library imports
from traits.api import Any, Array, Bool, Dict, Event, Float, HasTraits, \
                                 Int, Property, Str, Trait

# Relative imports
from .abstract_colormap import AbstractColormap
from .data_range_1d import DataRange1D

from .speedups import map_colors, map_colors_uint8


class ColorMapTemplate(HasTraits):
    """
    A class representing the state of a ColorMapper, for use when persisting
    plots.
    """
    #: The segment data of the color map.
    segment_map = Any
    #: The number of steps in the color map.
    steps = Int(256)
    #: Low end of the color map range.
    range_low_setting = Trait('auto', 'auto', Float)
    #: High end of the color map range.
    range_high_setting = Trait('auto', 'auto', Float)

    def __init__(self, colormap=None, **kwtraits):
        """
        Creates this template from a color map instance or creates an empty
        template.
        """
        if colormap:
            self.from_colormap(colormap)
        return

    def from_colormap(self, colormap):
        """ Populates this template from a color map.
        """
        self.segment_map = colormap._segmentdata.copy()
        self.steps = colormap.steps
        self.range_low_setting = colormap.range.low_setting
        self.range_high_setting = colormap.range.high_setting
        return

    def to_colormap(self, range=None):
        """ Returns a ColorMapper instance from this template.
        """
        colormap = ColorMapper(self.segment_map, steps = self.steps)
        if range:
            colormap.range = range
        else:
            colormap.range = DataRange1D(low = self.range_low_setting,
                                       high = self.range_high_setting)
        return colormap



class ColorMapper(AbstractColormap):
    """ Represents a simple band-of-colors style of color map.

    The look-up transfer function is a simple linear function between defined
    intensities.  There is no limit to the number of steps that can be
    defined. If the segment intervals contain very few array
    locations, quantization errors will occur.

    Construction of a ColorMapper can be done through the factory methods
    from_palette_array() and from_segment_map(). Do not make direct calls to the
    ColorMapper constructor.
    """

    #: The color table.
    color_bands = Property(Array)

    #: The total number of color steps in the map.
    steps = Int(256)

    #: The name of this color map.
    name = Str

    #: Not used.
    low_pos = None
    #: Not used.
    high_pos = None

    #: A generic "update" event that generally means that anything that relies
    #: on this mapper for visual output should do a redraw or repaint.
    updated = Event

    # Are the mapping arrays out of date?
    _dirty = Bool(True)

    # The raw segment data for creating the mapping array.
    _segmentdata = Dict  # (Str, Tuple | List)


    #------------------------------------------------------------------------
    # Static methods.
    #------------------------------------------------------------------------

    @classmethod
    def from_palette_array(cls, palette, **traits):
        """ Creates a ColorMapper from a palette array.

        The palette colors are linearly interpolated across the range of
        mapped values.

        The *palette* parameter is a Nx3 or Nx4 array of intensity values, where
        N > 1::

            [[R0, G0, B0], ... [R(N-1), G(N-1), B(N-1)]]

            [[R0, G0, B0, A0], ... [R(N-1), G(N-1), B(N-1), A(N-1]]
        """

        palette = asarray(palette)
        n_colors, n_components = palette.shape
        if n_colors < 2:
            raise ValueError("Palette must contain at least two colors.")
        if n_components not in (3,4):
            raise ValueError("Palette must be of RGB or RGBA colors. "
                "Got %s color components." % n_components)

        # Compute the % offset for each of the color locations.
        offsets = linspace(0.0, 1.0, n_colors)

        # From the offsets and the color data, generate a segment map.
        segment_map = {}
        red_values = palette[:,0]
        segment_map['red'] = list(zip(offsets, red_values, red_values))
        green_values = palette[:,1]
        segment_map['green'] = list(zip(offsets, green_values, green_values))
        blue_values = palette[:,2]
        segment_map['blue'] = list(zip(offsets, blue_values, blue_values))
        if n_components == 3:
            alpha_values = ones(n_colors)
        else:
            alpha_values = palette[:,3]
        segment_map['alpha'] = list(zip(offsets, alpha_values, alpha_values))

        return cls(segment_map, **traits)

    @classmethod
    def from_segment_map(cls, segment_map, **traits):
        """ Creates a Colormapper from a segment map.

        The *segment_map* parameter is a dictionary with 'red', 'green', and
        'blue' (and optionally 'alpha') entries.  Each entry is a list of
        (x, y0, y1) tuples:

        * x: an offset in [0..1] (offsets within the list must be in ascending order)
        * y0: value for the color channel for values less than or equal to x
        * y1: value for the color channel for values greater than x

        When a data value gets mapped to a color, it will be normalized to be
        within [0..1]. For each RGB(A) component, the two adjacent values will
        be found in the segment_map. The mapped component value will be found by
        linearly interpolating the two values.

        Generally, y0==y1. Colormaps with sharp transitions will have y0!=y1 at
        the transitions.
        """

        if 'alpha' not in segment_map:
            segment_map = segment_map.copy()
            segment_map['alpha'] = [(0.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        return cls(segment_map, **traits)

    @classmethod
    def from_file(cls, filename, **traits):
        """ Creates a ColorMapper from a file.

        The *filename* parameter is the name of a file whose lines each contain
        4 or 5 float values between 0.0 and 1.0. The first value is an offset in
        the range [0..1], and the remaining 3 or 4 values are red, green, blue,
        and optionally alpha values for the color corresponding to that offset.

        The first line is assumed to contain the name of the colormap.
        """
        colormap_file = open(filename, 'r')
        lines = colormap_file.readlines()
        colormap_file.close()
        rgba_arr = [[],[],[],[]]
        for line in lines[1:]:
            strvalues = line.strip().split()
            values = [float32(value) for value in strvalues]
            if len(values) > 4:
                channels = (0,1,2,3)
            else:
                channels = (0,1,2)
            for i in channels:
                channeltuple = (values[0], values[i+1], values[i+1])
                rgba_arr[i].append(channeltuple)
        # Alpha is frequently unspecified.
        if len(rgba_arr[-1]) == 0:
            rgba_arr[-1] = [(0.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        if 'name' not in traits:
            # Don't override the code.
            traits['name'] = lines[0].strip()
        rgba_dict = {
            'red': rgba_arr[0],
            'green': rgba_arr[1],
            'blue': rgba_arr[2],
            'alpha': rgba_arr[3],
        }

        return cls(rgba_dict, **traits)


    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, segmentdata, **kwtraits):
        """ Creates a Colormapper from a segment map.

        The *segment_map* parameter is a dictionary with 'red', 'green', and
        'blue' (and optionally 'alpha') entries.  Each entry is a list of
        (x, y0, y1) tuples:

        * x: an offset in [0..1] (offsets within the list must be in ascending order)
        * y0: value for the color channel for values less than or equal to x
        * y1: value for the color channel for values greater than x

        When a data value gets mapped to a color, it will be normalized to be
        within [0..1]. For each RGB(A) component, the two adjacent values will
        be found in the segment_map. The mapped component value will be found by
        linearly interpolating the two values.

        Generally, y0==y1. Colormaps with sharp transitions will have y0!=y1 at
        the transitions.
        """
        self._segmentdata = segmentdata
        super(ColorMapper, self).__init__(**kwtraits)
        return


    def map_screen(self, data_array):
        """ Maps an array of data values to an array of colors.
        """
        if self._dirty:
            self._recalculate()

        rgba = map_colors(data_array, self.steps, self.range.low,
                self.range.high, self._red_lut, self._green_lut,
                self._blue_lut, self._alpha_lut)

        return rgba


    def map_index(self, ary):
        """ Maps an array of values to their corresponding color band index.
        """

        if self._dirty:
            self._recalculate()

        indices = (ary - self.range.low) / (self.range.high - self.range.low) * self.steps

        return clip(indices.astype(int), 0, self.steps - 1)

    def reverse_colormap(self):
        """ Reverses the color bands of this colormap.
        """
        for name in ("red", "green", "blue", "alpha"):
            data = asarray(self._segmentdata[name])
            data[:, (1,2)] = data[:, (2,1)]
            data[:,0] = (1.0 - data[:,0])
            self._segmentdata[name] = data[::-1]
        self._recalculate()

    def map_uint8(self, data_array):
        """ Maps an array of data values to an array of colors.
        """
        if self._dirty:
            self._recalculate()

        rgba = map_colors_uint8(data_array, self.steps, self.range.low,
                self.range.high, self._red_lut_uint8, self._green_lut_uint8,
                self._blue_lut_uint8, self._alpha_lut_uint8)

        return rgba


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------


    def _get_color_bands(self):
        """ Gets the color bands array.
        """
        if self._dirty:
            self._recalculate()

        luts = [self._red_lut, self._green_lut, self._blue_lut]
        if self.color_depth is 'rgba':
            luts.append(self._alpha_lut)

        result = list(zip(*luts))

        return result

    def _recalculate(self):
        """ Recalculates the mapping arrays.
        """

        self._red_lut = self._make_mapping_array(
            self.steps, self._segmentdata['red']
        )
        self._green_lut = self._make_mapping_array(
            self.steps, self._segmentdata['green']
        )
        self._blue_lut = self._make_mapping_array(
            self.steps, self._segmentdata['blue']
        )
        self._alpha_lut = self._make_mapping_array(
            self.steps, self._segmentdata['alpha']
        )
        self._red_lut_uint8 = (self._red_lut * 255.0).astype('uint8')
        self._green_lut_uint8 = (self._green_lut * 255.0).astype('uint8')
        self._blue_lut_uint8 = (self._blue_lut * 255.0).astype('uint8')
        self._alpha_lut_uint8 = (self._alpha_lut * 255.0).astype('uint8')
        self.updated = True
        self._dirty = False

        return

    #### matplotlib ####
    def _make_mapping_array(self, n, data):
        """Creates an N-element 1-D lookup table

        The *data* parameter is a list of x,y0,y1 mapping correspondences (which
        can be lists or tuples), where all the items are values between 0 and 1,
        inclusive. The items in the mapping are:

        * x: a value being mapped
        * y0: the value of y for values of x less than or equal to the given x value.
        * y1: the value of y for values of x greater than the given x value.

        The two values of y allow for discontinuous mapping functions (for
        example, as might be found in a sawtooth function)

        The list must start with x=0, end with x=1, and
        all values of x must be in increasing order. Values between
        the given mapping points are determined by simple linear interpolation.

        The function returns an array "result" where result[x*(N-1)]
        gives the closest value for values of x between 0 and 1.
        """

        try:
            adata = array(data)
        except:
            raise TypeError("data must be convertable to an array")
        shape = adata.shape
        if len(shape) != 2 and shape[1] != 3:
            raise ValueError("data must be nx3 format")

        x  = adata[:,0]
        y0 = adata[:,1]
        y1 = adata[:,2]

        if x[0] != 0. or x[-1] != 1.0:
            raise ValueError(
                "data mapping points must start with x=0. and end with x=1")
        if sometrue(sort(x)-x):
            raise ValueError(
                "data mapping points must have x in increasing order")
        # begin generation of lookup table
        x = x * (n-1)
        lut = zeros((n,), float32)
        xind = arange(float32(n), dtype=float32)
        ind = searchsorted(x, xind)[1:-1]

        lut[1:-1] = ( divide(xind[1:-1] - take(x,ind-1),
                             take(x,ind)-take(x,ind-1) )
                      *(take(y0,ind)-take(y1,ind-1)) + take(y1,ind-1))
        lut[0] = y1[0]
        lut[-1] = y0[-1]

        # ensure that the lut is confined to values between 0 and 1 by clipping it
        lut = lut.clip(0, 1)
        return lut

    #### matplotlib ####
    def _map(self, X):
        """ Maps from a scalar or an array to an RGBA value or array.

        The *X* parameter is either a scalar or an array (of any dimension).
        If it is scalar, the function returns a tuple of RGBA values; otherwise
        it returns an array with the new shape = oldshape+(4,).  Any values
        that are outside the 0,1 interval are clipped to that interval before
        generating RGB values.

        This is no longer used in this class. It has been deprecated and
        retained for API compatibility.

        """

        if type(X) in [int, float]:
            vtype = 'scalar'
            xa = array([X])
        else:
            vtype = 'array'
            xa = asarray(X)

        # assume the data is properly normalized
        #xa = where(xa>1.,1.,xa)
        #xa = where(xa<0.,0.,xa)


        nanmask = isnan(xa)
        xa = where(nanmask, 0, (xa * (self.steps-1)).astype(int))
        rgba = zeros(xa.shape+(4,), float)
        rgba[...,0] = where(nanmask, 0, take(self._red_lut, xa))
        rgba[...,1] = where(nanmask, 0, take(self._green_lut, xa))
        rgba[...,2] = where(nanmask, 0, take(self._blue_lut, xa))
        rgba[...,3] = where(nanmask, 0, take(self._alpha_lut, xa))
        if vtype == 'scalar':
            rgba = tuple(rgba[0,:])

        return rgba

    def _range_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._range_change_handler, "updated",
                                remove = True)
        if new is not None:
            new.on_trait_change(self._range_change_handler, "updated")

        self.updated = new

    def _range_change_handler(self, obj, name, new):
        "Handles the range changing; dynamically attached to our ranges"
        self.updated = obj
