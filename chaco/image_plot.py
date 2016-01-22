#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

""" Defines the ImagePlot class.
"""

from __future__ import with_statement

# Standard library imports
from math import ceil, floor, pi
from contextlib import contextmanager

import numpy as np

# Enthought library imports.
from traits.api import (Bool, Either, Enum, Instance, List, Range, Trait,
                        Tuple, Property, cached_property)
from kiva.agg import GraphicsContextArray

# Local relative imports
from base_2d_plot import Base2DPlot
from image_utils import trim_screen_rect

try:
    # InterpolationQuality required for Quartz backend only (requires OSX).
    from kiva.quartz.ABCGI import InterpolationQuality
except ImportError:
    pass
else:
    QUARTZ_INTERP_QUALITY = {"nearest": InterpolationQuality.none,
                             "bilinear": InterpolationQuality.low,
                             "bicubic": InterpolationQuality.high}


KIVA_DEPTH_MAP = {3: "rgb24", 4: "rgba32"}


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

    # Bool indicating whether x-axis is flipped.
    x_axis_is_flipped = Property(depends_on=['orientation', 'origin'])

    # Bool indicating whether y-axis is flipped.
    y_axis_is_flipped = Property(depends_on=['orientation', 'origin'])

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

    # Bool indicating whether the origin is top-left or bottom-right.
    # The name "principal diagonal" is borrowed from linear algebra.
    _origin_on_principal_diagonal = Property(depends_on='origin')

    #------------------------------------------------------------------------
    # Properties
    #------------------------------------------------------------------------

    @cached_property
    def _get_x_axis_is_flipped(self):
        return ((self.orientation == 'h' and 'right' in self.origin) or
                (self.orientation == 'v' and 'top' in self.origin))

    @cached_property
    def _get_y_axis_is_flipped(self):
        return ((self.orientation == 'h' and 'top' in self.origin) or
                (self.orientation == 'v' and 'right' in self.origin))

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _index_data_changed_fired(self):
        self._image_cache_valid = False
        self.request_redraw()

    def _index_mapper_changed_fired(self):
        self._image_cache_valid = False
        self.request_redraw()

    def _value_data_changed_fired(self):
        self._image_cache_valid = False
        self.request_redraw()

    #------------------------------------------------------------------------
    # Base2DPlot interface
    #------------------------------------------------------------------------

    def _render(self, gc):
        """ Draw the plot to screen.

        Implements the Base2DPlot interface.
        """
        if not self._image_cache_valid:
            self._compute_cached_image()

        scale_x = -1 if self.x_axis_is_flipped else 1
        scale_y = 1 if self.y_axis_is_flipped else -1

        x, y, w, h = self._cached_dest_rect
        if w <= 0 or h <= 0:
            return

        x_center = x + w / 2
        y_center = y + h / 2
        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            gc.set_alpha(self.alpha)

            # Translate origin to the center of the graphics context.
            if self.orientation == "h":
                gc.translate_ctm(x_center, y_center)
            else:
                gc.translate_ctm(y_center, x_center)

            # Flip axes to move origin to the correct position.
            gc.scale_ctm(scale_x, scale_y)

            if self.orientation == "v":
                self._transpose_about_origin(gc)

            # Translate the origin back to its original position.
            gc.translate_ctm(-x_center, -y_center)

            with self._temporary_interp_setting(gc):
                gc.draw_image(self._cached_image, self._cached_dest_rect)

    def map_index(self, screen_pt, threshold=0.0, outside_returns_none=True,
                  index_only=False):
        """ Maps a screen space point to an index into the plot's index
        array(s).

        Implements the AbstractPlotRenderer interface. Uses 0.0 for
        *threshold*, regardless of the passed value.
        """
        # For image plots, treat hittesting threshold as 0.0, because it's
        # the only thing that really makes sense.
        return Base2DPlot.map_index(self, screen_pt, 0.0, outside_returns_none,
                                    index_only)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    @cached_property
    def _get__origin_on_principal_diagonal(self):
        bottom_right = 'bottom' in self.origin and 'right' in self.origin
        top_left = 'top' in self.origin and 'left' in self.origin
        return bottom_right or top_left

    def _transpose_about_origin(self, gc):
        if self._origin_on_principal_diagonal:
            gc.scale_ctm(-1, 1)
        else:
            gc.scale_ctm(1, -1)
        gc.rotate_ctm(pi/2)

    @contextmanager
    def _temporary_interp_setting(self, gc):
        if hasattr(gc, "set_interpolation_quality"):
            # Quartz uses interpolation setting on the destination GC.
            interp_quality = QUARTZ_INTERP_QUALITY[self.interpolation]
            gc.set_interpolation_quality(interp_quality)
            yield
        elif hasattr(gc, "set_image_interpolation"):
            # Agg backend uses the interpolation setting of the *source*
            # image to determine the type of interpolation to use when
            # drawing. Temporarily change image's interpolation value.
            old_interp = self._cached_image.get_image_interpolation()
            set_interp = self._cached_image.set_image_interpolation
            try:
                set_interp(self.interpolation)
                yield
            finally:
                set_interp(old_interp)
        else:
            yield

    def _calc_virtual_screen_bbox(self):
        """ Return the rectangle describing the image in screen space
        assuming that the entire image could fit on screen.

        Zoomed-in images will have "virtual" sizes larger than the image.
        Note that vertical orientations flip x- and y-axes such that x is
        vertical and y is horizontal.
        """
        # Upper-right values are always larger than lower-left values,
        # regardless of origin or orientation...
        (lower_left, upper_right) = self.index.get_bounds()
        # ... but if the origin is not 'bottom left', the data-to-screen
        # mapping will flip min and max values.
        x_min, y_min = self.map_screen([lower_left])[0]
        x_max, y_max = self.map_screen([upper_right])[0]
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        if y_min > y_max:
            y_min, y_max = y_max, y_min

        virtual_x_size = x_max - x_min
        virtual_y_size = y_max - y_min

        # Convert to the coordinates of the graphics context, which expects
        # origin to be at the center of a pixel.
        x_min += 0.5
        y_min += 0.5
        return [x_min, y_min, virtual_x_size, virtual_y_size]

    def _compute_cached_image(self, data=None, mapper=None):
        """ Computes the correct screen coordinates and renders an image into
        `self._cached_image`.

        Parameters
        ----------
        data : array
            Image data. If None, image is derived from the `value` attribute.
        mapper : function
            Allows subclasses to transform the displayed values for the visible
            region. This may be used to adapt grayscale images to RGB(A)
            images.
        """
        if data is None:
            data = self.value.data

        virtual_rect = self._calc_virtual_screen_bbox()
        index_bounds, screen_rect = self._calc_zoom_coords(virtual_rect)
        col_min, col_max, row_min, row_max = index_bounds

        view_rect = self.position + self.bounds
        sub_array_size = (col_max - col_min, row_max - row_min)
        screen_rect = trim_screen_rect(screen_rect, view_rect, sub_array_size)

        data = data[row_min:row_max, col_min:col_max]

        if mapper is not None:
            data = mapper(data)

        if len(data.shape) != 3:
            raise RuntimeError("`ImagePlot` requires color images.")

        # Update cached image and rectangle.
        self._cached_image = self._kiva_array_from_numpy_array(data)
        self._cached_dest_rect = screen_rect
        self._image_cache_valid = True

    def _kiva_array_from_numpy_array(self, data):
        if data.shape[2] not in KIVA_DEPTH_MAP:
            msg = "Unknown colormap depth value: {}"
            raise RuntimeError(msg.format(data.shape[2]))
        kiva_depth = KIVA_DEPTH_MAP[data.shape[2]]

        # Data presented to the GraphicsContextArray needs to be contiguous.
        data = np.ascontiguousarray(data)
        return GraphicsContextArray(data, pix_format=kiva_depth)

    def _calc_zoom_coords(self, image_rect):
        """ Calculates the coordinates of a zoomed sub-image.

        Because of floating point limitations, it is not advisable to request a
        extreme level of zoom, e.g., idx or idy > 10^10.

        Parameters
        ----------
        image_rect : 4-tuple
            (x, y, width, height) rectangle describing the pixels bounds of the
            full, **rendered** image. This will be larger than the canvas when
            zoomed in since the full image may not fit on the canvas.

        Returns
        -------
        index_bounds : 4-tuple
            The column and row indices (col_min, col_max, row_min, row_max) of
            the sub-image to be extracted and drawn into `screen_rect`.
        screen_rect : 4-tuple
            (x, y, width, height) rectangle describing the pixels bounds where
            the image will be rendered in the plot.
        """
        ix, iy, image_width, image_height = image_rect
        if 0 in (image_width, image_height) or 0 in self.bounds:
            return (None, None)

        array_bounds = self._array_bounds_from_screen_rect(image_rect)
        col_min, col_max, row_min, row_max = array_bounds
        # Convert array indices back into screen coordinates after its been
        # clipped to fit within the bounds.
        array_width = self.value.get_width()
        array_height = self.value.get_height()
        x_min = float(col_min) / array_width * image_width + ix
        x_max = float(col_max) / array_width * image_width + ix
        y_min = float(row_min) / array_height * image_height + iy
        y_max = float(row_max) / array_height * image_height + iy

        # Flip indexes **after** calculating screen coordinates.
        # The screen coordinates will get flipped in the renderer.
        if self.y_axis_is_flipped:
            row_min = array_height - row_min
            row_max = array_height - row_max
            row_min, row_max = row_max, row_min
        if self.x_axis_is_flipped:
            col_min = array_width - col_min
            col_max = array_width - col_max
            col_min, col_max = col_max, col_min

        index_bounds = map(int, [col_min, col_max, row_min, row_max])
        screen_rect = [x_min, y_min, x_max - x_min, y_max - y_min]
        return index_bounds, screen_rect

    def _array_bounds_from_screen_rect(self, image_rect):
        """ Transform virtual-image rectangle into array indices.

        The virtual-image rectangle is in screen coordinates and can be outside
        the plot bounds. This method converts the rectangle into array indices
        and clips to the plot bounds.
        """
        # Plot dimensions are independent of orientation and origin, but data
        # dimensions vary with orientation. Flip plot dimensions to match data
        # since outputs will be in data space.
        if self.orientation == "h":
            x_min, y_min = self.position
            plot_width, plot_height = self.bounds
        else:
            y_min, x_min = self.position
            plot_height, plot_width = self.bounds

        ix, iy, image_width, image_height = image_rect
        # Screen coordinates of virtual-image that fit into plot window.
        x_min -= ix
        y_min -= iy
        x_max = x_min + plot_width
        y_max = y_min + plot_height

        array_width = self.value.get_width()
        array_height = self.value.get_height()
        # Convert screen coordinates to array indexes
        col_min = floor(float(x_min) / image_width * array_width)
        col_max = ceil(float(x_max) / image_width * array_width)
        row_min = floor(float(y_min) / image_height * array_height)
        row_max = ceil(float(y_max) / image_height * array_height)

        # Clip index bounds to the array bounds.
        col_min = max(col_min, 0)
        col_max = min(col_max, array_width)
        row_min = max(row_min, 0)
        row_max = min(row_max, array_height)

        return col_min, col_max, row_min, row_max
