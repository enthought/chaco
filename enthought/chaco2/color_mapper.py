""" Defines the ColorMapper and ColorMapTemplate classes.
"""

# Major library imports
from types import IntType, FloatType
from numpy import arange, array, asarray, clip, \
                  divide, isnan, ones, searchsorted, shape, \
                  sometrue, sort, take, where, zeros

# Enthought library imports
from enthought.traits.api import Any, Array, Bool, Dict, Event, Float, HasTraits, \
                                 Int, Property, Str, Trait

# Relative imports
from abstract_colormap import AbstractColormap
from data_range_1d import DataRange1D


class ColorMapTemplate(HasTraits):
    """
    A class representing the state of a ColorMapper, for use when persisting
    plots.
    """
    # The segment data of the color map.
    segment_map = Any
    # The number of steps in the color map.
    steps = Int(256)
    # Low end of the color map range.
    range_low_setting = Trait('auto', 'auto', Float)
    # High end of the color map range.
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

    # The color table.
    color_bands = Property(Array)

    # The total number of color steps in the map.
    steps = Int(256)

    # The name of this color map.
    name = Str
    
    # Not used.
    low_pos = None
    # Not used.
    high_pos = None
    
    # A generic "update" event that generally means that anything that relies
    # on this mapper for visual output should do a redraw or repaint.
    updated = Event

    # Are the mapping arrays out of date?
    _dirty = Bool(True)
    
    # The raw segment data for creating the mapping array.
    _segmentdata = Dict  # (Str, Tuple | List)


    #------------------------------------------------------------------------
    # Static methods.
    #------------------------------------------------------------------------

    def from_palette_array(palette, **traits):
        """ Creates a ColorMapper from a palette array.

        The palette colors are linearly interpolated across the range of
        mapped values.
        
        The *palette* parameter is a 3xN array of intensity values, where N > 1::

            [[R0, G0, B0], ... [R(N-1), G(N-1), B(N-1)]]
        """

        n_colors = shape(palette)[0]
        if n_colors < 2:
            raise ValueError("Palette must contain at least two colors.")

        # Compute the % offset for each of the color locations.
        offsets = zeros(n_colors, float)
        offsets[:-1] = arange(0.0, 1.0, 1.0/(n_colors-1))
        offsets[-1] = 1.0

        # From the offsets and the color data, generate a segment map.
        segment_map = {}
        red_values = palette[::,0]
        segment_map['red'] = zip(offsets, red_values, red_values)
        green_values = palette[::,1]
        segment_map['green'] = zip(offsets, green_values, green_values)
        blue_values = palette[::,2]
        segment_map['blue'] = zip(offsets, blue_values, blue_values)

        return ColorMapper(segment_map, **traits)

    from_palette_array = staticmethod(from_palette_array)

    def from_segment_map(segment_map, **traits):
        """ Creates a Colormapper from a segment map.

        The *segment_map* parameter is a dictionary with 'red', 'green', and 
        'blue' entries.  Each entry is a list of (x, y0, y1) tuples:
        
        * x: an offset (offsets within the list must be in ascending order)
        * y0: value for the color channel for values less than or equal to x
        * y1: value for the color channel for values greater than x
        """

        return ColorMapper(segment_map, **traits)

    from_segment_map = staticmethod(from_segment_map)

    def from_file(filename, **traits):
        """ Creates a ColorMapper from a file.
        
        The *filename* parameter is the name of a file whose lines each contain
        4 float values between 0.0 and 1.0. The first value is an offset, and
        the remaining 3 values are red, green, and blue values for the color
        corresponding to that offset.
        """
        colormap_file = open(filename, 'r')
        lines = colormap_file.readlines()
        rgbarr = [[],[],[]]
        for line in lines[1:]:
            strvalues = line.rstrip().split(' ')
            values = [float(value) for value in strvalues]
            for colorchannel in range(3):
                channeltuple = (values[0],
                                values[colorchannel+1],
                                values[colorchannel+1])
                rgbarr[colorchannel].append(channeltuple)
        traits['name'] = lines[0].rstrip()
        rgbdict = {'red':rgbarr[0],
                   'green':rgbarr[1],
                   'blue':rgbarr[2]}
        
        return ColorMapper(rgbdict, **traits)

    from_file = staticmethod(from_file)
        
            

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, segmentdata, **kwtraits):
        """ Creates a ColorMapper instance.
        
        The *segmentdata* parameter is a dictionary with red, green, and blue 
        entries. Each entry must be a list of (x, y0, y1) tuples:
            
        * x: an offset (offsets within the list must be in ascending order)
        * y0: value for the color channel for values less than or equal to x
        * y1: value for the color channel for values greater than x

        """
        self._segmentdata = segmentdata
        super(ColorMapper, self).__init__(**kwtraits)
        return
        
    
    def map_screen(self, data_array):
        """ Maps an array of data values to an array of colors.
        """
        if self._dirty:
            self._recalculate()

        high = self.range.high
        low = self.range.low
        
        # Handle null ranges
        if high == low:
            norm_data = ones(len(data_array))
        else:
            norm_data =clip((data_array - low) / (high - low), 0.0, 1.0)
        
        return self._map(norm_data)


    def map_index(self, ary):
        """ Maps an array of values to their corresponding color band index. 
        """

        if self._dirty:
            self._recalculate()

        indices = (ary - self.range.low) / (self.range.high - self.range.low) * self.steps

        return clip(indices.astype(IntType), 0, self.steps - 1)

    def reverse_colormap(self):
        """ Reverses the color bands of this colormap.
        """
        for name in ("red", "green", "blue"):
            data = asarray(self._segmentdata[name])
            data[:, (1,2)] = data[:, (2,1)]
            data[:,0] = (1.0 - data[:,0])
            self._segmentdata[name] = data[::-1]
        self._recalculate()


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------


    def _get_color_bands(self):
        """ Gets the color bands array. 
        """
        if self._dirty:
            self._recalculate()

        if self.color_depth is 'rgba':
            alpha = ones(self.steps)
            result = zip(self._red_lut, self._green_lut, self._blue_lut, alpha)

        else:
            result = zip(self._red_lut, self._green_lut, self._blue_lut)

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
        lut = zeros((n,), float)
        xind = arange(float(n))
        ind = searchsorted(x, xind)[1:-1]
        
        lut[1:-1] = ( divide(xind[1:-1] - take(x,ind-1),
                             take(x,ind)-take(x,ind-1) )
                      *(take(y0,ind)-take(y1,ind-1)) + take(y1,ind-1))
        lut[0] = y1[0]
        lut[-1] = y0[-1]
        
        # ensure that the lut is confined to values between 0 and 1 by clipping it
        lut = where(lut > 1., 1., lut)
        lut = where(lut < 0., 0., lut)
        return lut

    #### matplotlib ####
    def _map(self, X, alpha=1.0):
        """ Maps from a scalar or an array to an RGBA value or array.
        
        The *X* parameter is either a scalar or an array (of any dimension).
        If it is scalar, the function returns a tuple of RGBA values; otherwise
        it returns an array with the new shape = oldshape+(4,).  Any values
        that are outside the 0,1 interval are clipped to that interval before
        generating RGB values.  The *alpha* parameter must be a scalar
        """
        
        alpha = min(alpha, 1.0) # alpha must be between 0 and 1
        alpha = max(alpha, 0.0)
        if type(X) in [IntType, FloatType]:
            vtype = 'scalar'
            xa = array([X])
        else:
            vtype = 'array'
            xa = asarray(X)

        # assume the data is properly normalized
        #xa = where(xa>1.,1.,xa)
        #xa = where(xa<0.,0.,xa)

        
        nanmask = isnan(xa)
        xa = where(nanmask, 0, (xa *(self.steps-1)).astype(int))
        rgba = zeros(xa.shape+(4,), float)
        rgba[...,0] = where(nanmask, 0, take(self._red_lut, xa))
        rgba[...,1] = where(nanmask, 0, take(self._green_lut, xa))
        rgba[...,2] = where(nanmask, 0, take(self._blue_lut, xa))
        rgba[...,3] = where(nanmask, 0, alpha)        
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



# EOF
