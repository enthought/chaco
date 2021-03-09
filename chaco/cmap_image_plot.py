#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from numpy import zeros

# Enthought library imports.
from traits.api import Any, Bool, Float, Instance, Property, Tuple

# Local relative imports
from .image_plot import ImagePlot
from .abstract_colormap import AbstractColormap
from .speedups import apply_selection_fade


class CMapImagePlot(ImagePlot):
    """ Colormapped image plot.  Takes a value data object whose elements are
    scalars, and renders them as a colormapped image.
    """

    # TODO: Modify ImageData to explicitly support scalar value arrays

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    #: Maps from scalar data values in self.data.value to color tuples
    value_mapper = Instance(AbstractColormap)

    #: Convenience property for value_mapper as color_mapper
    color_mapper = Property

    #: Convenience property for accessing the data range of the mapper.
    value_range = Property

    #: alpha value to use to fade out unselected data points when there is an
    #: active selection
    fade_alpha = Float(0.3)

    #: RGB color to use to fade out unselected points.
    fade_background = Tuple((0,0,0))
    
    #: whether to pre-compute the full colormapped RGB(A) image
    cache_full_map = Bool(True)

    #------------------------------------------------------------------------
    # Private Traits
    #------------------------------------------------------------------------

    # Is the mapped image valid?
    _mapped_image_cache_valid = Bool(False)

    # Cache of the fully mapped RGB(A) image.
    _cached_mapped_image = Any

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, **kwargs):
        super(CMapImagePlot, self).__init__(**kwargs)
        if self.value_mapper:
            self.value_mapper.on_trait_change(self._update_value_mapper,
                                              "updated")
        if self.value:
            self.value.on_trait_change(self._update_selections,
                                       "metadata_changed")

    def set_value_selection(self, val):
        """ Sets a range of values in the value data source as selected.
        """
        if val is not None:
            low, high = val
            data = self.value.get_data()
            new_mask = (data>=low) & (data<=high)
            self.value.metadata["selection_masks"] = [new_mask]
        else:
            del self.value.metadata["selection_masks"]

        self._update_selections()

    #------------------------------------------------------------------------
    # Base2DPlot interface
    #------------------------------------------------------------------------

    def _render(self, gc):
        """ Ensures that the cached image is valid.

        Called before _render() is called. Implements the Base2DPlot interface.
        """
        if not self._mapped_image_cache_valid:
            if 'selection_masks' in self.value.metadata:
                self._compute_cached_image(self.value.metadata['selection_masks'])
            else:
                self._compute_cached_image()
        ImagePlot._render(self, gc)


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------
    
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
        
    def _compute_cached_image(self, selection_masks=None):
        """ Updates the cached image.
        """
        if self.cache_full_map:
            if not self._mapped_image_cache_valid:
                self._cached_mapped_image = self._cmap_values(self.value.data,
                    selection_masks)
                self._mapped_image_cache_valid = True

            mapped_value = self._cached_mapped_image
            ImagePlot._compute_cached_image(self, mapped_value)
        else:
            self._mapped_image_cache_valid = True
            ImagePlot._compute_cached_image(self, self.value.data, mapper=lambda data:
                self._cmap_values(data))
            
    def _update_value_mapper(self):
        self._mapped_image_cache_valid = False
        self._image_cache_valid = False
        self.invalidate_and_redraw()

    def _update_selections(self):
        self._mapped_image_cache_valid = False
        self._image_cache_valid = False
        self.invalidate_and_redraw()

    #------------------------------------------------------------------------
    # Properties
    #------------------------------------------------------------------------

    def _get_value_range(self):
        return self.value_mapper.range

    def _set_value_range(self, val):
        self.value_mapper.range = val

    def _get_color_mapper(self):
        return self.value_mapper

    def _set_color_mapper(self, val):
        self.value_mapper = val

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

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
    
    def _value_data_changed_fired(self):
        super(CMapImagePlot, self)._value_data_changed_fired()
        self._mapped_image_cache_valid = False
        return

    def _index_data_changed_fired(self):
        super(CMapImagePlot, self)._index_data_changed_fired()
        self._mapped_image_cache_valid = False
        return
    
    def _cache_full_map_changed(self):
        self._mapped_image_cache_valid = False
        

