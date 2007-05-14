
# Standard library imports
from numpy import nanmax, nanmin, swapaxes

# Enthought library imports
from enthought.traits.api import false, Float, HasTraits, Int, Property, \
                             ReadOnly, Tuple

# Local relative imports
from base import DimensionTrait, ImageTrait
from abstract_data_source import AbstractDataSource

class ImageData(AbstractDataSource):
    """
    Represents a grid of data to be plotted using a numpy 2D grid 
    
    The data array has dimensions NxM, but it may have more than just 2
    dimensions.  The appropriate dimensionality of the value array depends
    on the  in which the ImageData instance will be used.  A ImagePlotValue 
    expects a length-3 or length-4 array (RGB or RGBA image).
    """
    dimension = ReadOnly(DimensionTrait('image'))
    
    # depth of the values at each i,j.  Uses:
    #    3: color images, with alpha channel
    #    4: color images, without alpha channel
    # TODO: Modify ImageData to explicitly support scalar value arrays, as 
    # needed by CMapImagePlot
    value_depth = Int(1)
    
    # Holds the grid data that forms the image.  The shape of the array should
    # be (N, M, D) where:
    #   D is 1, 3, or 4
    #   N is the length of y_index
    #   M is the length of x_index
    #
    # Thus, data[0,:,:] should be the first row of data.  If D is 1, then
    # the array should be of type float; if D is 3 or 4, then the array
    # should be of type uint8.
    #
    # NOTE: If ImageData was constructed with a transposed data array,
    # then internally it is still transposed (i.e. x-axis is the first axis
    # and y-axis is the second), and the 'data' array property may not be
    # contiguous.  If contiguousness is required and calling .copy() is too
    # expensive, use the raw_value attribute.
    # Also note that setting this trait does not change the value of 'transposed',
    # so be sure to set it to its proper value when using the same ImageData
    # instance interchangeably to store transposed and non-transposed data.
    data = Property(ImageTrait)

    # 'transposed' indicates that 'raw_value', the actual underlying image data
    # array, is transposed from 'value'. (i.e. the first axis corresponds to
    # the x direction and the second axis corresponds to the y direction.)
    #
    # Rather than doing swapaxis/transpose on the data and destroying
    # continuity, we expose the data as both 'value' and 'raw_value'.
    transposed = false

    # A read-only attribute that exposes the underlying array.
    raw_value = Property(ImageTrait)

    
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # The actual image data array.  May be MxN or NxM, depending on the value
    # of 'transposed'.
    _data = ImageTrait

    # Is the bounds cache valid or does it need to be computed
    _bounds_cache_valid = false

    # caches the value of min and max as long as data doesn't change
    _bounds_cache = Tuple

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    @classmethod
    def fromfile(cls, filename):
        """ Alternate constructor to create an ImageData from an image file
        on disk.
        """
        
        from enthought.kiva.backend_image import Image
        img = Image(filename)
        imgdata = cls(data=img.bmp_array, transposed=False)
        fmt = img.format()
        
        if fmt == "rgb24":
            imgdata.value_depth = 3
        elif fmt == "rgba32":
            imgdata.value_depth = 4
        else:
            raise ValueError("Unknown image format in file %s: %s" % 
                             (filename, fmt))
        return imgdata

    def get_width(self):
        if self.transposed:
            return self._data.shape[0]
        else:
            return self._data.shape[1]
    
    def get_height(self):
        if self.transposed:
            return self._data.shape[1]
        else:
            return self._data.shape[0]

    def get_array_bounds(self):
        "Always returns ((0, width), (0, height)) for xbounds and ybounds."
        if self.transposed:
            b = ((0,self._data.shape[0]), (0,self._data.shape[1]))
        else:
            b = ((0,self._data.shape[1]), (0,self._data.shape[0]))
        return b

    #------------------------------------------------------------------------
    # Datasource interface
    #------------------------------------------------------------------------

    def get_data(self):
        return self.data

    def is_masked(self):
        return False

    def get_bounds(self):
        if not self._bounds_cache_valid:
            if self.raw_value.size == 0: 
                self._cached_bounds = (0,0) 
            else: 
                self._cached_bounds = (nanmin(self.raw_value), 
                                       nanmax(self.raw_value))
            self._bounds_cache_valid = True
        return self._cached_bounds
    
    def get_size(self):
        if self._data is not None and self._data.shape[0] != 0:
            return self._data.shape[0] * self._data.shape[1]
        else:
            return 0

    def set_data(self, data):
        self._set_data(data)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------
    
    def _get_data(self):
        if self.transposed:
            return swapaxes(self._data, 0, 1)
        else:
            return self._data
    
    def _set_data(self, newdata):
        self._data = newdata
        self._bounds_cache_valid = False
        self.data_changed = True

    def _get_raw_value(self):
        return self._data


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _metadata_changed(self, event):
        self.metadata_changed = True

    def _metadata_items_changed(self, event):
        self.metadata_changed = True




# EOF
