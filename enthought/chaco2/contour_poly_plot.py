""" Defines the ContourPolyPlot class.
"""
# Major library imports
from numpy import array, linspace, meshgrid, transpose

# Enthought library imports
from enthought.enable2.api import black_color_trait, ColorTrait, LineStyle
from enthought.kiva.agg import GraphicsContextArray
from enthought.traits.api import Any, Dict, false, Float, HasTraits, Instance, \
                                 Int, List, Property, Str, Trait

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
    color_mapper = Instance("ColorMapper")


    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # Are the cached contours valid? If False, new ones need to be computed.
    _poly_cache_valid = false

    # Cached collection of traces.
    _cached_polys = Dict

    # Is the cached level data valid?
    _level_cache_valid = false
    # Is the cached color data valid?
    _colors_cache_valid = false
    
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
        
        for i in range(len(self._levels)-1):
            gc.set_fill_color(self._colors[i])
            key = (self._levels[i], self._levels[i+1])
            for poly in self._cached_polys[key]:
                spoly = self.index_mapper.map_screen(poly)
                gc.lines(spoly)
                gc.close_path()
                gc.draw_path()

        gc.restore_state()

    def _update_polys(self):
        """ Updates the contour cache.
        """
        xg, yg = meshgrid(self.index._xdata.get_data(),
                          self.index._ydata.get_data()[::-1])
        c = Cntr(xg, yg, self.value.raw_value)
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
        cmap.range.low, cmap.range.high = self._levels[0], self._levels[-1]
        self._colors =  []
        mapped_colors = cmap.map_screen(array(self._levels))
        for i in range(len(self._levels)-1):
            self._color_map_trait = tuple(mapped_colors[i])
            self._colors.append(self._color_map_trait_)


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _index_data_changed_fired(self):
        self._level_cache_valid = False
        self.invalidate_draw()

    def _index_mapper_changed_fired(self):
        self.invalidate_draw()

    def _value_data_changed_fired(self):
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





