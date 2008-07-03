""" Defines the ImagePlot class.
"""
# Standard library imports
from math import ceil, floor, pi

# Enthought library imports.
from enthought.traits.api import Bool, Either, Enum, Instance, \
                                 List, Range, Trait, Tuple
from enthought.kiva.agg import GraphicsContextArray

# Local relative imports
from base_2d_plot import Base2DPlot


class ImagePlot(Base2DPlot):
    """ A plot based on an image.
    """
    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------
    
    # Overall alpha value of the image. Ranges from 0.0 for transparent to 1.0
    # for full intensity.
    alpha = Trait(1.0, Range(0.0, 1.0))

    # The interpolation method to use when rendering an image onto the GC.
    interpolation = Enum("nearest", "bilinear", "bicubic")

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # Are the cache traits valid? If False, new ones need to be computed.
    _image_cache_valid = Bool(False)

    # Cached image of the bmp data (not the bmp data in self.data.value).
    _cached_image = Instance(GraphicsContextArray)
    
    # Tuple-defined rectangle (x, y, dx, dy) in screen space in which the 
    # **_cached_image** is to be drawn.
    _cached_dest_rect = Either(Tuple, List)

    #------------------------------------------------------------------------
    # Base2DPlot interface
    #------------------------------------------------------------------------

    def _render(self, gc):
        """ Actually draws the plot. 
        
        Implements the Base2DPlot interface.
        """
        if not self._image_cache_valid:
            self._compute_cached_image()
        
        if "bottom" in self.origin:
            sy = -1
        else:
            sy = 1
        if "left" in self.origin:
            sx = 1
        else:
            sx = -1

        # If the orientation is flipped, the BR and TL cases are swapped
        if self.orientation == "v" and sx == sy:
            sx, sy = -sx, -sy
            
        gc.save_state()
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        gc.set_alpha(self.alpha)

        # Kiva image interpolation note:
        # Kiva's Agg backend uses the interpolation setting of the *source*
        # image to determine the type of interpolation to use when drawing the
        # image.  The mac backend uses the interpolation setting on the
        # destination GC.
        old_interp = self._cached_image.get_image_interpolation()
        if hasattr(gc, "set_interpolation_quality"):
            from enthought.kiva.mac.ABCGI import InterpolationQuality
            interp_quality_dict = {"nearest": InterpolationQuality.none,
                    "bilinear": InterpolationQuality.low,
                    "bicubic": InterpolationQuality.high}
            gc.set_interpolation_quality(interp_quality_dict[self.interpolation])
        elif hasattr(gc, "set_image_interpolation"):
            self._cached_image.set_image_interpolation(self.interpolation)
        x, y, w, h = self._cached_dest_rect
        if self.orientation == "h":        # for horizontal orientation:
            gc.translate_ctm(x+w/2, y+h/2)   # translate back normally
        else:                              # for vertical orientation:
            gc.translate_ctm(y+h/2, x+w/2)   # translate back with dx,dy swap
        gc.scale_ctm(sx, sy)               # flip axes as appropriate
        if self.orientation == "v":        # for vertical orientation:
            gc.scale_ctm(1,-1)               # restore origin to lower left
            gc.rotate_ctm(pi/2)              # rotate 1/4 turn clockwise
        gc.translate_ctm(-x-w/2, -y-h/2)   # translate image center to origin
        gc.draw_image(self._cached_image, self._cached_dest_rect)
        self._cached_image.set_image_interpolation(old_interp)
        gc.restore_state()

    def map_index(self, screen_pt, threshold=0.0, outside_returns_none=True,
                  index_only=False):
        """ Maps a screen space point to an index into the plot's index array(s).
        
        Implements the AbstractPlotRenderer interface. Uses 0.0 for *threshold*,
        regardless of the passed value.
        """
        # For image plots, treat hittesting threshold as 0.0, because it's
        # the only thing that really makes sense.
        return Base2DPlot.map_index(self, screen_pt, 0.0, outside_returns_none,
                                    index_only)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _compute_cached_image(self, data=None):
        """ Computes the correct sub-image coordinates and renders an image 
        into self._cached_image. 
        
        The parameter *data* is for subclasses that might not store an RGB(A)
        image as the value, but need to compute one to display (colormaps, etc.).
        """
        
        if data == None:
            data = self.value.data

        (lpt, upt) = self.index.get_bounds()
        ll_x, ll_y = self.map_screen([lpt])[0]
        ur_x, ur_y = self.map_screen([upt])[0]
        if "right" in self.origin:
            ll_x, ur_x = ur_x, ll_x
        if "top" in self.origin:
            ll_y, ur_y = ur_y, ll_y
        virtual_width = ur_x - ll_x
        virtual_height = ur_y - ll_y
        
        args = self.position \
             + self.bounds \
             + [ll_x, ll_y, virtual_width, virtual_height]
        img_pixels, gc_rect = self._calc_zoom_coords(*args)

        # Grab the appropriate sub-image, if necessary
        if img_pixels is not None:
            i1, j1, i2, j2 = img_pixels
            if "top" in self.origin:
                y_length = self.value.get_array_bounds()[1][1]
                j1 = y_length + 1 - j1
                j2 = y_length + 1 - j2
                # swap so that j1 < j2
                j1, j2 = j2, j1
            if "right" in self.origin:
                x_length = self.value.get_array_bounds()[0][1]
                i1 = x_length + 1 - i1
                i2 = x_length + 1 - i2
                # swap so that i1 < i2
                i1, i2 = i2, i1

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
        """ Calculates the coordinates of a zoomed sub-image.
        
        Because of floating point limitations, it is not advisable to request a
        extreme level of zoom, e.g., idx or idy > 10^10.
        
        Parameters
        ----------
        px : number
            X-coordinate of plot pixel bounds
        py : number
            Y-coordinate of plot pixel bounds
        plot_width : number
            Width of plot pixel bounds
        plot_height : number
            Height of plot pixel bounds
        ix : number
            X-coordinate of image pixel bounds
        iy : number
            Y-coordinate of image pixel bounds
        image_width : number
            Width of image pixel bounds
        image_height : number
            Height of image pixel bounds
            
        Returns
        -------
        ((i1, j1, i2, j2), (x, y, dx, dy))
            Lower left and upper right indices of the sub-image to be extracted,
            and graphics context origin and extents to draw the sub-image into.
        (None, None)
            No image extraction is necessary.
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
        if self.orientation == "h":
            x1 = px - ix
            x2 = (px + plot_width) - ix
            y1 = py - iy
            y2 = (py + plot_height) - iy
        else:
            x1 = px - ix
            x2 = (px + plot_height) - ix
            y1 = py - iy
            y2 = (py + plot_width) - iy


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
