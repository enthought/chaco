

# Major library imports
from types import IntType, FloatType
from numpy import add, arange, array, asarray, choose, clip, concatenate, \
                  divide, ones, put, ravel, resize, searchsorted, shape, \
                  sometrue, sort, take, where, zeros

# Enthought library imports
from enthought.traits.api import Any, Array, Dict, Float, HasTraits, Int, \
                                 Property, Str, Trait, true, Tuple

# Relative imports
from abstract_colormap import AbstractColormap
from data_range_1d import DataRange1D


class ColorMapTemplate(HasTraits):
    """
    A class representing the state of a ColorMapper, for use when persisting
    plots.
    """
    
    segment_map = Any
    steps = Int(256)
    range_low_setting = Trait('auto', 'auto', Float)
    range_high_setting = Trait('auto', 'auto', Float)

    def __init__(self, colormap=None, **kwtraits):
        """
        Creates this template from a colormap instance or creates an empty template.
        """
        if colormap:
            self.from_colormap(colormap)
        return

    def from_colormap(self, colormap):
        self.segment_map = colormap._segmentdata.copy()
        self.steps = colormap.steps
        self.range_low_setting = colormap.range.low_setting
        self.range_high_setting = colormap.range.high_setting
        return

    def to_colormap(self, range=None):
        """ Returns a ColorMapper instance from this template """
        colormap = ColorMapper(self.segment_map, steps = self.steps)
        if range:
            colormap.range = range
        else:
            colormap.range = DataRange1D(low = self.range_low_setting,
                                       high = self.range_high_setting)
        return colormap



class ColorMapper(AbstractColormap):
    """
    Represents a simple band-of-colors style of colormap.
    
    The lookup transfer function is a simple linear function between defined
    intensities.  There is no limit to the number of steps that may be
    defined. As the segment intervals start containing fewer and fewer array
    locations, there will be inevitable quantization errors.

    Construction of a ColorMapper be done through the factory methods 
    'from_palette_array' and 'from_segment_map'.  Direct calls to the
    ColorMapper constructor are discouraged.
    """

    # The color table.
    color_bands = Property(Array)

    # The total number of color steps in the map.
    steps = Int(256)

    # The name of this colormap
    name = Str
    
    # Redefine inherited traits
    low_pos = None
    high_pos = None
    

    # Flag to indicate the mapping arrays are out of date.
    _dirty = true
    
    # The raw segment data for creating the mapping array.
    _segmentdata = Dict  # (Str, Tuple | List)


    #------------------------------------------------------------------------
    # Static methods.
    #------------------------------------------------------------------------

    def from_palette_array(palette, **traits):
        """ Create a ColorMapper from a palette array.

        The palette colors will be linearly interpolated across the range of
        mapped values.

        palette - A 3 by n array of intensity values, where n > 1:
          [[R0, G0, B0], ... [R(n-1), G(n-1), B(n-1)]]
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
        """ Create a LinearSegmentedColormap from a segment map.

        segment_map: a dictionary with red, green, and blue entries.  Each
        entry is a list of x, y0, y1 tuples.  See makeMappingArray for details
        on how segment maps are converted to color maps.
        """

        return ColorMapper(segment_map, **traits)

    from_segment_map = staticmethod(from_segment_map)

    def from_file(filename, **traits):
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
        """
        segmentdata is a dictionary with red, green and blue entries. Each entry
        should be a list of x, y0, y1 tuples.  See makeMappingArray for details
        on how segmentdata is converted to a color map.
        """
        self._segmentdata = segmentdata
        super(ColorMapper, self).__init__(**kwtraits)
        return
        
    
    def map_screen(self, data_array):

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
        """ Maps an array of values to their corresponding color band index. """

        if self._dirty:
            self._recalculate()

        indices = (ary - self.range.low) / (self.range.high - self.range.low) * self.steps

        return clip(indices.astype(IntType), 0, self.steps - 1)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------


    def _get_color_bands(self):
        """ Gets the color bands array. """
        if self._dirty:
            self._recalculate()

        if self.color_depth is 'rgba':
            alpha = ones(self.steps)
            result = zip(self._red_lut, self._green_lut, self._blue_lut, alpha)

        else:
            result = zip(self._red_lut, self._green_lut, self._blue_lut)

        return result
    
    def _recalculate(self):
        """ Recalculate the mapping arrays. """

        self._red_lut = self._make_mapping_array(
            self.steps, self._segmentdata['red']
        )
        self._green_lut = self._make_mapping_array(
            self.steps, self._segmentdata['green']
        )
        self._blue_lut = self._make_mapping_array(
            self.steps, self._segmentdata['blue']
        )

        self._dirty = False
        
        return

    #### matplotlib ####
    def _make_mapping_array(self, n, data):
        """Create an N-element 1-d lookup table
        
        data represented by a list of x,y0,y1 mapping correspondences.
        Each element in this list represents how a value between 0 and 1
        (inclusive) represented by x is mapped to a corresponding value
        between 0 and 1 (inclusive). The two values of y are to allow 
        for discontinuous mapping functions (say as might be found in a
        sawtooth) where y0 represents the value of y for values of x
        <= to that given, and y1 is the value to be used for x > than
        that given). The list must start with x=0, end with x=1, and 
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
        """
        X is either a scalar or an array (of any dimension).
        If scalar, a tuple of rgba values is returned, otherwise
        an array with the new shape = oldshape+(4,).  Any values
        that are outside the 0,1 interval are clipped to that
        interval before generating rgb values.  
        Alpha must be a scalar
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

        xa = (xa *(self.steps-1)).astype(int)
        rgba = zeros(xa.shape+(4,), float)
        rgba[...,0] = take(self._red_lut, xa)
        rgba[...,1] = take(self._green_lut, xa)
        rgba[...,2] = take(self._blue_lut, xa)
        rgba[...,3] = alpha
        if vtype == 'scalar':
            rgba = tuple(rgba[0,:])
            
        return rgba

# EOF
