
from numpy import invert, zeros

# Enthought library imports.
from enthought.traits.api import Any, false, Float, HasTraits, Instance, \
                                 List, Property, Tuple
from enthought.kiva.agg import GraphicsContextArray

# Local relative imports
from image_plot import ImagePlot
from color_mapper import ColorMapper


class CMapImagePlot(ImagePlot):
    """ Colormapped image plot.  Takes a value data object whose elements are
    scalars, and renders them as a colormapped image.
    """

    # TODO: Modify ImageData to explicitly support scalar value arrays

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------
    
    # Maps from scalar data values in self.data.value to color tuples
    value_mapper = Instance("ColorMapper")

    # Convenience property for value_mapper as color_mapper
    color_mapper = Property

    # Convenience property for accessing the data range of the mapper.
    value_range = Property

    # alpha value to use to fade out unselected data points when there is an 
    # active selection
    fade_alpha = Float(0.3)

    #fade_background = Tuple((255,255,255))
    # RGB color to use to fade out unselected points.
    fade_background = Tuple((0,0,0))

    #------------------------------------------------------------------------
    # Private Traits
    #------------------------------------------------------------------------

    # Is the mapped image valid?
    _mapped_image_cache_valid = false

    # Cache of the fully mapped image.
    _cached_mapped_image = Any

    # (dx, dy) in data space
    _cached_image_data_widths = Tuple

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

    def _render_pre(self, gc):
        """ Ensures that the cached image is valid.
        
        Called before _render() is called. Implements the Base2DPlot interface.
        """
        if not self._mapped_image_cache_valid:
            if 'selection_masks' in self.value.metadata:
                self._compute_cached_image(self.value.metadata['selection_masks'])
            else:
                self._compute_cached_image()


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _compute_cached_image(self, selection_masks=None):
        """ Updates the cached image.
        """
        if not self._mapped_image_cache_valid:
            cached_mapped_image = \
                self.value_mapper.map_screen(self.value.data) * 255
            if selection_masks is not None:
                # construct a composite mask
                mask = zeros(cached_mapped_image.shape[:2], dtype=bool)
                for m in selection_masks:
                    mask = mask | m 
                invmask = invert(mask)
                # do a cheap alpha blend with our specified color
                cached_mapped_image[invmask,0:3] = \
                    self.fade_alpha*(cached_mapped_image[invmask,0:3] -
                                     self.fade_background) + self.fade_background
            self._cached_mapped_image = cached_mapped_image
            self._cached_image_data_widths = self._get_index_mapper_data_bounds()
            self._mapped_image_cache_valid = True

        mapped_value = self._cached_mapped_image
        ImagePlot._compute_cached_image(self, mapped_value.astype("UInt8"))

    def _update_value_mapper(self):
        self._mapped_image_cache_valid = False
        self.invalidate_draw() 

    def _update_selections(self):
        self._mapped_image_cache_valid = False
        self.invalidate_draw() 

    def _get_index_mapper_data_bounds(self):
        xmin, ymin = self.index_mapper.range.low
        xmax, ymax = self.index_mapper.range.high
        dx = xmax - xmin
        dy = ymax - ymin
        return (dx, dy)

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

    def _index_mapper_changed_fired(self):
        super(CMapImagePlot, self)._index_mapper_changed_fired()
        bounds = self._get_index_mapper_data_bounds()
        if bounds != self._cached_image_data_widths:
            self._mapped_image_cache_valid = False
        return

