""" Defines the ImageData class.
"""
# Standard library imports
from numpy import nanmax, nanmin, swapaxes

# Enthought library imports
from traits.api import Bool, Int, Property, ReadOnly, Tuple

# Local relative imports
from base import DimensionTrait, ImageTrait
from abstract_data_source import AbstractDataSource

class ImageData(AbstractDataSource):
    """
    Represents a grid of data to be plotted using a Numpy 2-D grid.

    The data array has dimensions NxM, but it may have more than just 2
    dimensions.  The appropriate dimensionality of the value array depends
    on the context in which the ImageData instance will be used.
    """
    # The dimensionality of the data.
    dimension = ReadOnly(DimensionTrait('image'))

    # Depth of the values at each i,j. Values that are used include:
    #
    # * 3: color images, without alpha channel
    # * 4: color images, with alpha channel
    value_depth = Int(1) # TODO: Modify ImageData to explicitly support scalar
                         # value arrays, as needed by CMapImagePlot

    # Holds the grid data that forms the image.  The shape of the array is
    # (N, M, D) where:
    #
    # * D is 1, 3, or 4.
    # * N is the length of the y-axis.
    # * M is the length of the x-axis.
    #
    # Thus, data[0,:,:] must be the first row of data.  If D is 1, then
    # the array must be of type float; if D is 3 or 4, then the array
    # must be of type uint8.
    #
    # NOTE: If this ImageData was constructed with a transposed data array,
    # then internally it is still transposed (i.e., the x-axis is the first axis
    # and the y-axis is the second), and the **data** array property might not be
    # contiguous.  If contiguousness is required and calling copy() is too
    # expensive, use the **raw_value** attribute. Also note that setting this
    # trait does not change the value of **transposed**,
    # so be sure to set it to its proper value when using the same ImageData
    # instance interchangeably to store transposed and non-transposed data.
    data = Property(ImageTrait)

    # Is **raw_value**, the actual underlying image data
    # array, transposed from **value**? (I.e., does the first axis correspond to
    # the x-direction and the second axis correspond to the y-direction?)
    #
    # Rather than transposing or swapping axes on the data and destroying
    # continuity, this class exposes the data as both **value** and **raw_value**.
    transposed = Bool(False)

    # A read-only attribute that exposes the underlying array.
    raw_value = Property(ImageTrait)


    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # The actual image data array.  Can be MxN or NxM, depending on the value
    # of **transposed**.
    _data = ImageTrait

    # Is the bounds cache valid? If False, it needs to be computed.
    _bounds_cache_valid = Bool(False)

    # Cached value of min and max as long as **data** doesn't change.
    _bounds_cache = Tuple

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    @classmethod
    def fromfile(cls, filename):
        """ Alternate constructor to create an ImageData from an image file
        on disk. 'filename' may be a file path or a file object.
        """

        from kiva.image import Image
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
        """ Returns the shape of the x-axis.
        """
        if self.transposed:
            return self._data.shape[0]
        else:
            return self._data.shape[1]

    def get_height(self):
        """ Returns the shape of the y-axis.
        """
        if self.transposed:
            return self._data.shape[1]
        else:
            return self._data.shape[0]

    def get_array_bounds(self):
        """ Always returns ((0, width), (0, height)) for x-bounds and y-bounds.
        """
        if self.transposed:
            b = ((0,self._data.shape[0]), (0,self._data.shape[1]))
        else:
            b = ((0,self._data.shape[1]), (0,self._data.shape[0]))
        return b

    #------------------------------------------------------------------------
    # Datasource interface
    #------------------------------------------------------------------------

    def get_data(self):
        """ Returns the data for this data source.

        Implements AbstractDataSource.
        """
        return self.data

    def is_masked(self):
        """is_masked() -> False

        Implements AbstractDataSource.
        """
        return False

    def get_bounds(self):
        """ Returns the minimum and maximum values of the data source's data.

        Implements AbstractDataSource.
        """
        if not self._bounds_cache_valid:
            if self.raw_value.size == 0:
                self._cached_bounds = (0,0)
            else:
                self._cached_bounds = (nanmin(self.raw_value),
                                       nanmax(self.raw_value))
            self._bounds_cache_valid = True
        return self._cached_bounds

    def get_size(self):
        """get_size() -> int

        Implements AbstractDataSource.
        """
        if self._data is not None and self._data.shape[0] != 0:
            return self._data.shape[0] * self._data.shape[1]
        else:
            return 0

    def set_data(self, data):
        """ Sets the data for this data source.

        Parameters
        ----------
        data : array
            The data to use.
        """
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
