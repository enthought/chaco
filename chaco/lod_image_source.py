from traits.api import HasTraits, Any, Instance, Property, Tuple

from .image_data import ImageData


class LODDataBase(HasTraits):

    data_entry = Any

    def get_lod_image(self, lod):
        msg = "Subclasses of {} must implement `get_lod_image`"
        raise NotImplementedError(msg.format(self.__class__.__name__))


class LODImageSource(ImageData):
    """Base class for image sources for `engeo.plot`'s `ImageRenderer`.

    This data source, combined with `ImageRenderer`, allows plotting of images
    that are out of core memory and with multiple levels of detail.

    Subclasses must define a `nominal_shape` for the data. `ImageRenderer` will
    request data within an array of this nominal shape, but this image source
    controls how that requested data is sourced or generated.

    Note that the `screen_size` parameter passed to `get_data_bounded` allows
    the data source to choose the correct level of detail.
    """

    # Any data type that supports mapping lod to array and array slicing
    data = Instance(LODDataBase)

    # The nominal shape of the image.
    nominal_shape = Property(Tuple, depends_on='data')

    def _get_nominal_shape(self):
        return self.get_lod_shape(0)

    def get_width(self):
        """ Returns the length of the x-axis. """
        width_index = 0 if self.transposed else 1
        return self.nominal_shape[width_index]

    def get_height(self):
        """ Returns the length of the y-axis. """
        height_index = 1 if self.transposed else 0
        return self.nominal_shape[height_index]

    def get_array_bounds(self):
        """Return the x and y bounds of the array"""
        return (0, self.get_width()), (0, self.get_height())

    def get_lod_shape(self, lod):
        lod_image = self.data.get_lod_image(lod)
        return lod_image.shape

    def get_data_bounded(self, index_bounds, lod, screen_size=None):
        """Return data within the requested indexes to fill the screen.

        Parameters
        ----------
        index_bounds : 4-tuple
            Column and row indices (col_min, col_max, row_min, row_max)
            representing desired slices into the data. If None, return sensible
            default.
        screen_size : 2-tuple
            Screen size (width, height) to fill with data.
        """
        if index_bounds is None:
            index_bounds = self.get_array_bounds()

        # `ImageData` uses x/y order instead of row/column order.
        col_min, col_max, row_min, row_max = \
            self.lod_bounds_from_nominal_bounds(index_bounds, lod)

        current_lod_image = self.data.get_lod_image(lod)
        subarray = current_lod_image[row_min:row_max, col_min:col_max]
        return subarray

    def lod_bounds_from_nominal_bounds(self, nominal_bounds, lod_level):
        # `ImageData` uses x/y order instead of row/column order.
        col_min, col_max, row_min, row_max = nominal_bounds

        current_lod_image = self.data.get_lod_image(lod_level)
        current_shape = current_lod_image.shape
        col_min = int(col_min * current_shape[1] / self.nominal_shape[1])
        col_max = int(col_max * current_shape[1] / self.nominal_shape[1])
        row_min = int(row_min * current_shape[0] / self.nominal_shape[0])
        row_max = int(row_max * current_shape[0] / self.nominal_shape[0])
        return col_min, col_max, row_min, row_max
