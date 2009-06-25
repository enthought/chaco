""" Defines the ContourPolyPlot class.
"""
# Major library imports
from numpy import array, linspace, meshgrid, transpose

# Enthought library imports
from enthought.enable.api import ColorTrait
from enthought.traits.api import Bool, Dict, Instance, Int, List, Range, Trait

# Local relative imports
from base_2d_plot import Base2DPlot
from color_mapper import ColorMapper
from contour.contour import Cntr


class ContourPolyPlot(Base2DPlot):
    """ Contour image plot.  Takes a value data object whose elements are
    scalars, and renders them as a contour plot.
    """

    # TODO: Modify ImageData to explicitly support scalar value arrays

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # List of levels to contour.
    levels = Trait("auto", Int, List)

    # Mapping of values to colors
    color_mapper = Instance(ColorMapper)

    alpha = Trait(1.0, Range(0.0, 1.0))

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # Are the cached contours valid? If False, new ones need to be computed.
    _poly_cache_valid = Bool(False)

    # Cached collection of traces.
    _cached_polys = Dict

    # Is the cached level data valid?
    _level_cache_valid = Bool(False)
    # Is the cached color data valid?
    _colors_cache_valid = Bool(False)
    
    # List of levels and their associated line properties.
    _levels = List
    # List of colors
    _colors = List

    # Mapped trait used to convert user-suppied color values to AGG-acceptable
    # ones. (Mapped traits in lists are not supported, must be converted one at 
    # a time.)
    _color_map_trait = ColorTrait


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _render(self, gc):
        """ Actually draws the plot. 
        
        Implements the Base2DPlot interface.
        """
        
        if not self._level_cache_valid:
            self._update_levels()
        if not self._poly_cache_valid:
            self._update_polys()
        if not self._colors_cache_valid:
            self._update_colors()

        gc.save_state()
        gc.set_antialias(True)
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        gc.set_line_width(0)
        gc.set_alpha(self.alpha)

        for i in range(len(self._levels)-1):
            gc.set_fill_color(self._colors[i])
            key = (self._levels[i], self._levels[i+1])
            for poly in self._cached_polys[key]:
                if self.orientation == "h":
                    spoly = self.index_mapper.map_screen(poly)
                else:
                    spoly = array(self.index_mapper.map_screen(poly))[:,::-1]
                gc.lines(spoly)
                gc.close_path()
                gc.draw_path()

        gc.restore_state()

    def _update_polys(self):
        """ Updates the contour cache.
        """
        # x and ydata are "fenceposts" so ignore the last value
        # XXX: this truncation is causing errors in Cntr() as of r13735
        if self.orientation == "h":
            xg, yg = meshgrid(self.index._xdata.get_data(), #[:-1],
                              self.index._ydata.get_data()) #[:-1])
            c = Cntr(xg, yg, self.value.raw_value)
        else:
            yg, xg = meshgrid(self.index._ydata.get_data(), #[:-1],
                              self.index._xdata.get_data()) #[:-1])
            c = Cntr(xg, yg, self.value.raw_value.T)
        self._cached_contours = {}
        for i in range(len(self._levels)-1):
            key = (self._levels[i], self._levels[i+1])
            self._cached_polys[key] = []
            polys = c.trace(*key)
            for poly in polys:
                self._cached_polys[key].append(transpose(poly))
        self._poly_cache_valid = True

    def _update_levels(self):
        """ Updates the levels cache.
        """
        low, high = self.value.get_bounds()
        if self.levels == "auto":
            self._levels = list(linspace(low, high, 10))
        elif isinstance(self.levels, int):
            self._levels = list(linspace(low, high, self.levels))
        else:
            self._levels = self.levels
            self._levels.sort()
        self._level_cache_valid = True
        self._poly_cache_valid = False
        self._colors_cache_valid = False

    def _update_colors(self):
        """ Updates the colors cache.
        """
        cmap = self.color_mapper
        self._colors =  []
        mapped_colors = cmap.map_screen(array(self._levels))
        for i in range(len(self._levels)-1):
            self._color_map_trait = tuple(mapped_colors[i])
            self._colors.append(self._color_map_trait_)


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _index_data_changed_fired(self):
        # If the index data has changed, the reset the levels cache (which
        # also triggers all the other caches to reset).
        self._level_cache_valid = False
        self.invalidate_draw()

    def _value_data_changed_fired(self):
        # If the index data has changed, the reset the levels cache (which
        # also triggers all the other caches to reset).
        self._level_cache_valid = False
        self.invalidate_draw()

    def _index_mapper_changed_fired(self):
        # If the index mapper has changed, then we need to redraw
        self.invalidate_draw()

    def _value_mapper_changed_fired(self):
        # If the value mapper has changed, then we need to recompute the
        # levels and cached data associated with that.
        self._level_cache_valid = False
        self.invalidate_draw()

    def _levels_changed(self):
        self._update_levels()
        self.invalidate_draw()
        self.request_redraw()
        
    def _color_mapper_changed(self):
        if self._level_cache_valid: 
            self._update_colors()
            self.invalidate_draw()





