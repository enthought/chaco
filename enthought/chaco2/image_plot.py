
# Standard library imports
from math import ceil, floor

# Enthought library imports.
from enthought.traits.api import Either, false, Instance, \
                                 List, Range, Trait, Tuple
from enthought.kiva.agg import GraphicsContextArray, pix_format_string_map

# Local relative imports
from base import reverse_map_1d
from base_2d_plot import Base2DPlot


class ImagePlot(Base2DPlot):

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------
    
    # overall alpha value of the image.  0=transparent, 1=full intensity.
    alpha = Trait(1.0, Range(0.0, 1.0))

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # Are the cache traits below valid, or do new ones need to be computed?
    _image_cache_valid = false

    # Cache the image of the bmp data (not the bmp data in self.data.value)
    _cached_image = Instance(GraphicsContextArray)
    
    # This is a tuple (x, y, dx, dy) in screen space in which the _cached_image
    # should be drawn.
    _cached_dest_rect = Either(Tuple, List)

    #------------------------------------------------------------------------
    # Base2DPlot interface
    #------------------------------------------------------------------------

    def _render(self, gc):
        if not self._image_cache_valid:
            self._compute_cached_image()
            
        gc.save_state()
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        gc.draw_image(self._cached_image, self._cached_dest_rect)
        gc.restore_state()

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _compute_cached_image(self, data=None):
        """ Computes the correct sub-image coordinates and renders an image 
        into self._cached_image. Parameter 'data' is for subclasses that may 
        not store an RGB(A) image as the value, but need to compute one to 
        display (colormaps, etc)
        """
        
        if data == None:
                data = self.value.data

        x_index, y_index = self.index.get_data()
        lpt = (x_index.get_data()[0], y_index.get_data()[0])
        ll_x, ll_y = self.map_screen([lpt])[0]
        upt = (x_index.get_data()[-1], y_index.get_data()[-1])
        ur_x, ur_y = self.map_screen([upt])[0]
        virtual_width = ur_x - ll_x
        virtual_height = ur_y - ll_y
        
        args = self.position \
             + self.bounds \
             + [ll_x, ll_y, virtual_width, virtual_height]
        img_pixels, gc_rect = self._calc_zoom_coords(*args)

        # Grab the appropriate sub-image, if necessary
        if img_pixels is not None:
            i1, j1, i2, j2 = img_pixels
            y_length = self.value.get_array_bounds()[1][1]
            j1 = y_length + 1 - j1
            j2 = y_length + 1 - j2
            
            # swap so that j1 < j2
            j1, j2 = j2, j1
            
            # Since data is row-major, j1 and j2 go first
            data = data[j1:j2, i1:i2]
        
        # Furthermore, the data presented to the GraphicsContextArray needs to 
        # be contiguous.  If it is not, we need to make a copy.
        if not data.flags['C_CONTIGUOUS']:
            data = data.copy()
        
        if data.shape[2] == 3:
            kiva_depth = "rgb24"
        elif data.shape[2] == 4:
            kiva_depth = "rgba32"
        else:
            raise RuntimeError, "Unknown colormap depth value: %i" \
                                % data.value_depth
        
        self._cached_image = GraphicsContextArray(data, pix_format=kiva_depth)
        if gc_rect is not None:
            self._cached_dest_rect = gc_rect
        else:
            self._cached_dest_rect = (ll_x, ll_y, virtual_width, virtual_height)
        self._image_cache_valid = True

    def _calc_zoom_coords(self, px, py, plot_width, plot_height,
                                ix, iy, image_width, image_height):
        """
        _calc_zoom_coords() -> ((sub-image i1, j1, i2, j2),
                                (dest_gc x, y, dx, dy))
        Given the plot pixel bounds (x,y,dx,dy) and the image virtual pixel
        bounds, returns the pixels of the sub-image that needs to be extracted
        (as lower left indices and upper right indices), and the origin and
        extents that sub-image should be drawn into.

        Returns (None, None) if no zoom image extraction is necessary.

        Because of floating point limitations, it is not advisable to request a
        ludicrous level of zoom, i.e. idx or idy > 10^10.
        """
        if (image_width < 1.5*plot_width) and (image_height < 1.5*plot_height):
            return (None, None)

        # We figure out the subimage coordinates using a two-step process:
        # 1. convert the plot boundaries from screen space into pixel offsets
        #    in the virtual image
        # 2. convert the coordinates in the virtual image into indices
        #    into the image data array
        # 3. from the data array indices, compute the screen coordinates of
        #    the corners of the data array sub-indices
        # in all the cases below, x1,y1 refers to the lower-left corner, and
        # x2,y2 refers to the upper-right corner.
        
        # 1. screen space -> pixel offsets
        x1 = px - ix
        x2 = (px + plot_width) - ix
        y1 = py - iy
        y2 = (py + plot_height) - iy

        # 2. pixel offsets -> data array indices
        # X and Y are transposed because for image plot data
        pixel_bounds = self.value.get_array_bounds()
        xpixels = pixel_bounds[0][1] - pixel_bounds[0][0]
        ypixels = pixel_bounds[1][1] - pixel_bounds[1][0]
        i1 = max(floor(float(x1) / image_width * xpixels), 0)
        i2 = min(ceil(float(x2) / image_width * xpixels), xpixels)
        j1 = max(floor(float(y1) / image_height * ypixels), 0)
        j2 = min(ceil(float(y2) / image_height * ypixels), ypixels)
        
        # 3. array indices -> new screen space coordinates
        x1 = float(i1)/xpixels * image_width + ix
        x2 = float(i2)/xpixels * image_width + ix
        y1 = float(j1)/ypixels * image_height + iy
        y2 = float(j2)/ypixels * image_height + iy

        # Handle really, really, subpixel cases
        subimage_index = [i1, j1, i2, j2]
        subimage_coords = [x1, y1, x2-x1, y2-y1]
        plot_dimensions = (px, py, plot_width, plot_height)
        xparams = (0, 2)
        yparams = (1, 3)
        for pos_index, size_index in (xparams, yparams):
            if subimage_index[pos_index] == subimage_index[pos_index+2]-1:
                # xcoords lie inside the same pixel, so set the subimage
                # coords to be the width of the image
                subimage_coords[pos_index] = plot_dimensions[pos_index]
                subimage_coords[size_index] = plot_dimensions[size_index]
            elif subimage_index[pos_index] == subimage_index[pos_index+2]-2:
                # coords span across a pixel boundary.  Find the scaling
                # factor of the virtual (and potentially large) subimage
                # size to the image size, and scale it down.  We can do
                # this without distortion b/c we are straddling only one
                # pixel boundary.
                #
                # If we scale down the extent to twice the screen size, we can
                # be sure that no matter what the offset, we will cover the
                # entire screen, since we are only straddling one pixel boundary.
                # The formula for calculating the new origin can be worked out
                # on paper.
                extent = subimage_coords[size_index]
                pixel_extent = extent/2   # we are indexed into two pixels
                origin = subimage_coords[pos_index]
                scale = float(2 * plot_dimensions[size_index] / extent)
                subimage_coords[size_index] *= scale
                subimage_coords[pos_index] = origin + (1-scale)*pixel_extent

        subimage_index = map(int, subimage_index)

        return [subimage_index, subimage_coords]


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _index_data_changed_fired(self):
        self._image_cache_valid = False

    def _index_mapper_changed_fired(self):
        self._image_cache_valid = False

    def _value_data_changed_fired(self):
        self._image_cache_valid = False
