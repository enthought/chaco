#
# (C) Copyright 2016 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

""" Defines the GridVertexPlot class. """

# Standard library imports
from math import ceil, floor, pi
from contextlib import contextmanager

import numpy as np

# Enthought library imports.
from traits.api import (Bool, Either, Enum, Float, Instance, Int, List, Range, Trait,
                        Tuple, Property, cached_property)
from kiva.agg import GraphicsContextArray

# Local imports
from chaco.downsample._aggregate import reduce_slices_2d_float
from chaco.abstract_colormap import AbstractColormap
from chaco.base_2d_plot import Base2DPlot
from chaco.image_utils import trim_screen_rect

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


class GridVertexPlot(Base2DPlot):
    """ A colormapped plot at vertex points of a Grid

    This differs from image plots in that:

    * data is aligned to grid vertices rather than cells
    * the grid is not assumed to be uniformly sampled
    """
    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    #: The aggregation method to use.
    aggregate = Enum("fast_mean", "mean", "count", "sum", "max", "min")

    #: The interpolation method to use when rendering an image onto the GC.
    interpolation = Enum("nearest", "bilinear", "bicubic")

    #: Maps from scalar data values in self.data.value to color tuples
    value_mapper = Instance(AbstractColormap)

    #: Convenience property for value_mapper as color_mapper
    color_mapper = Property

    #: Convenience property for accessing the data range of the mapper.
    value_range = Property

    #: The pixel resolution to use (useful for making sparse plots clearer)
    resolution = Tuple(Int(1), Int(1))

    # Overall alpha value of the image. Ranges from 0.0 for transparent to 1.0
    # for full intensity.
    alpha = Trait(1.0, Range(0.0, 1.0))

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

    #------------------------------------------------------------------------
    # Base2DPlot interface
    #------------------------------------------------------------------------

    def _render(self, gc):
        """ Draw the plot to screen.

        Implements the Base2DPlot interface.
        """
        if not self._image_cache_valid:
            self._compute_cached_image()

        x, y, w, h = self._cached_dest_rect
        if w <= 0 or h <= 0:
            return

        # at this point we are guaranteed that we have the data in a gc which
        # is oriented correctly and can be blitted into the destination
        # rectangle
        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            gc.set_alpha(self.alpha)

            if self.resolution[0] != 1 or self.resolution[1] != 1:
                with self._temporary_interp_setting(gc):
                    gc.draw_image(self._cached_image, self._cached_dest_rect)
            else:
                gc.draw_image(self._cached_image, self._cached_dest_rect)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

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
        # get the dataspace coordinates of the pixel edges
        x, y, w, h = self._calc_screen_bbox()
        x_res, y_res = self.resolution
        x_screen_edges = np.arange(x//x_res, (x + w)//x_res + 1) * x_res
        y_screen_edges = np.arange(y//y_res, (y + h)//y_res + 1) * y_res
        x_pixel_edges = self.map_data(np.column_stack([x_screen_edges, [y]*len(x_screen_edges)]))[:, 0]
        y_pixel_edges = self.map_data(np.column_stack([[x]*len(y_screen_edges), y_screen_edges]))[:, 1]

        x = x_screen_edges[0]
        w = x_screen_edges[-1] - x_screen_edges[0]
        y = y_screen_edges[0]
        h = y_screen_edges[-1] - y_screen_edges[0]
        self._cached_dest_rect = (x, y, w, h)

        if w <= 0 or h <= 0:
            return

        # now find the indices of the edges in the grid
        x_grid, y_grid = self.index.get_data()
        x_grid = x_grid.get_data()
        y_grid = y_grid.get_data()
        x_indices = x_grid.searchsorted(x_pixel_edges)
        y_indices = y_grid.searchsorted(y_pixel_edges)
        x_slices = np.column_stack([x_indices[:-1], x_indices[1:]])
        y_slices = np.column_stack([y_indices[:-1], y_indices[1:]])

        if data is None:
            data = self.value.data
        # XXX this may be very expensive, but will do for now!
        data = data.astype(float)
        data = reduce_slices_2d_float(data, y_slices, x_slices, self.aggregate)

        # now orient the data in screen space
        if self.x_axis_is_flipped:
            data = data[:, ::-1]
        if not self.y_axis_is_flipped:
            data = data[::-1, :]

        # XXX we aren't attempting to handle selections at this time
        # arbitrary selections are... complex (eg. how to fade a pixel with
        # points both selected and unselected?)
        data = self.value_mapper.map_uint8(data)

        if len(data.shape) != 3:
            raise RuntimeError("`ImagePlot` requires color images.")

        # Update cached image and rectangle.
        self._cached_image = self._kiva_array_from_numpy_array(data)
        self._image_cache_valid = True

    def _calc_screen_bbox(self):
        """ Return the screen coordinate rectangle that contains the grid

        This will be no bigger than the plot's bounding box, but may be
        smaller.
        """
        # get bounds of component
        x, y = self.position
        w, h = self.bounds

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

        # want min and max to be integer pixel boundaries
        x_min = floor(max(min(x_min, x+w), x))
        y_min = floor(max(min(y_min, y+h), y))
        x_max = ceil(min(max(x_max, x), x + w))
        y_max = ceil(min(max(y_max, y), y + h))

        width = x_max - x_min
        height = y_max - y_min

        return [x_min, y_min, width, height]

    def _cmap_values(self, data, selection_masks=None):
        """ Maps the data to RGB(A) with optional selection masks overlayed

        """
        # get the RGBA values from the color map as uint8
        mapped_image = self.value_mapper.map_uint8(data)
        if selection_masks is not None:
            # construct a composite mask
            if len(selection_masks) > 0:
                mask = zeros(mapped_image.shape[:2], dtype=bool)
                for m in selection_masks:
                    mask = mask | m
            else:
                mask = zeros(self._cached_mapped_image.shape[:2], dtype=bool)
            # Apply the selection fade, from speedups.py
            apply_selection_fade(mapped_image, mask,
                    self.fade_alpha, self.fade_background)
        return mapped_image

    def _kiva_array_from_numpy_array(self, data):
        if data.shape[2] not in KIVA_DEPTH_MAP:
            msg = "Unknown colormap depth value: {}"
            raise RuntimeError(msg.format(data.shape[2]))
        kiva_depth = KIVA_DEPTH_MAP[data.shape[2]]

        # Data presented to the GraphicsContextArray needs to be contiguous.
        data = np.ascontiguousarray(data)
        return GraphicsContextArray(data, pix_format=kiva_depth)

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

    def _update_value_mapper(self):
        self._mapped_image_cache_valid = False
        self._image_cache_valid = False
        self.invalidate_and_redraw()

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

    def _value_mapper_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._update_value_mapper,
                                "updated", remove=True)
        if new is not None:
            new.on_trait_change(self._update_value_mapper, "updated")

        if old and new:
            if new.range is None and old.range is not None:
                new.range = old.range
        self._update_value_mapper()

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
