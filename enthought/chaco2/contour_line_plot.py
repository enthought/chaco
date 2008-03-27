""" Defines the ContourLinePlot class.
"""
# Major library imports
from numpy import array, isscalar, issubsctype, linspace, meshgrid, number, transpose

# Enthought library imports
from enthought.enable2.api import ColorTrait, LineStyle
from enthought.traits.api import Dict, false, Float, Instance, \
        Int, List, Property, Range, Str, Trait, Tuple

# Local relative imports
from base_2d_plot import Base2DPlot
from color_mapper import ColorMapper
from contour.contour import Cntr


class ContourLinePlot(Base2DPlot):
    """ Takes a value data object whose elements are scalars, and renders them
    as a contour plot.
    """

    # TODO: Modify ImageData to explicitly support scalar value arrays

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # List of levels to contour.
    levels = Trait("auto", "auto", Int, List)

    # The thickness(es) of the contour lines.
    widths = Trait(1.0, Float, List)
    
    # The line dash style(s).
    styles = Trait("signed", Str, List)   

    # Line style for positive levels.
    positive_style = LineStyle("solid")
    # Line style for negative levels.
    negative_style = LineStyle("dash")

    # The color(s) of the lines.
    colors = Trait(None, Str, Instance("ColorMapper"), List, Tuple)

    # Overall alpha value of the plot. Ranges from 0.0 for transparent to 1.0
    # for full intensity.
    alpha = Trait(1.0, Range(0.0, 1.0))

    # If present, the color mapper for the colorbar to look at.
    color_mapper = Property(Instance("ColorMapper"))

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # Are the cached contours valid? If False, new ones need to be computed.
    _contour_cache_valid = false

    # Cached collection of traces.
    _cached_contours = Dict

    # Is the cached level data valid?
    _level_cache_valid = false
    # Is the cached width data valid?
    _widths_cache_valid = false
    # Is the cached style data valid?
    _styles_cache_valid = false
    # Is the cached color data valid
    _colors_cache_valid = false
    
    # Cached list of levels and their associated line properties
    _levels = List
    # Cached list of line widths
    _widths = List
    # Cached list of line styles
    _styles = List
    # Cached list of line colors
    _colors = List

    # Mapped trait used to convert user-suppied color values to AGG-acceptable
    # ones. (Mapped traits in lists are not supported, must be converted one at 
    # a time.)
    _color_map_trait = ColorTrait
    # Mapped trait used to convert user-suppied line style values to 
    # AGG-acceptable ones. (Mapped traits in lists are not supported, must be
    # converted one at a time.)
    _style_map_trait = LineStyle

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _render(self, gc):
        """ Actually draws the plot. 
        
        Implements the Base2DPlot interface.
        """
        if not self._level_cache_valid:
            self._update_levels()
        if not self._contour_cache_valid:
            self._update_contours()
        if not self._widths_cache_valid:
            self._update_widths()
        if not self._styles_cache_valid:
            self._update_styles()
        if not self._colors_cache_valid:
            self._update_colors()

        gc.save_state()
        gc.set_antialias(True)
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        gc.set_alpha(self.alpha)
        
        for i in range(len(self._levels)):
            gc.set_stroke_color(self._colors[i])
            gc.set_line_width(self._widths[i])
            gc.set_line_dash(self._styles[i])
            for trace in self._cached_contours[self._levels[i]]:
                if self.orientation == "h":
                    strace = self.index_mapper.map_screen(trace)
                else:
                    strace = array(self.index_mapper.map_screen(trace))[:,::-1]
                gc.begin_path()
                gc.lines(strace)
                gc.stroke_path()

        gc.restore_state()

    def _update_contours(self):
        """ Updates the contour cache.
        """
        # x and ydata are "fenceposts" so ignore the last value        
        # XXX: this truncaton is causing errors in Cntr() as of r13735
        if self.orientation == "h":
            xg, yg = meshgrid(self.index._xdata.get_data(), #[:-1],
                              self.index._ydata.get_data()) #[:-1])
            c = Cntr(xg, yg, self.value.raw_value)
        else:
            yg, xg = meshgrid(self.index._ydata.get_data(), #[:-1],
                              self.index._xdata.get_data()) #[:-1])
            c = Cntr(xg, yg, self.value.raw_value.T)
        self._cached_contours = {}
        for level in self._levels:
            self._cached_contours[level] = []
            traces = c.trace(level)
            for trace in traces:
                self._cached_contours[level].append(transpose(trace))
        self._contour_cache_valid = True

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
        self._level_cache_valid = True
        self._contour_cache_valid = False
        self._widths_cache_valid = False
        self._styles_cache_valid = False
        self._colors_cache_valid = False

    def _update_widths(self):
        """ Updates the widths cache.
        """
        # If we are given a single width, apply it to all levels
        if isinstance(self.widths, float):
            self._widths = [self.widths] * len(self._levels)

        # If the list of widths is shorter than the list of levels, 
        # simply repeat widths from the beginning of the list as needed
        else:
            self._widths = []
            for i in range(len(self._levels)):
                self._widths.append(self.widths[i%len(self.widths)])

        self._widths_cache_valid = True

    def _update_styles(self):
        """ Updates the styles cache.
        """
        # If the style type is "signed" then assign styles to levels based
        # on their sign 
        if self.styles == "signed":
            self._styles = []
            for level in self._levels:
                if level < 0:
                    self._styles.append(self.negative_style_)
                else:
                    self._styles.append(self.positive_style_)

        # If we not given a list, apply the one style to all levels
        elif not isinstance(self.styles, list):
            self._style_map_trait = self.styles
            self._styles = [self._style_map_trait_] * len(self._levels)

        # If the list of styles is shorter than the list of levels, 
        # simply repeat styles from the beginning of the list as needed
        else:
            self._styles = []
            for i in range(len(self._levels)):
                self._style_map_trait = self.styles[i%len(self.styles)]      
                self._styles.append(self._style_map_trait_)

        self._styles_cache_valid = True

    def _update_colors(self):
        """ Updates the colors cache.
        """
        colors = self.colors
        # If we are given no colors, set a default for all levels
        if colors is None: 
            self._color_map_trait = "black"
            self._colors = [self._color_map_trait_] * len(self._levels)

        # If we are given a single color, apply it to all levels 
        elif isinstance(colors, basestring):
            self._color_map_trait = colors
            self._colors = [self._color_map_trait_] * len(self._levels)

        # If we are given a colormap, use it to map all the levels to colors 
        elif isinstance(colors, ColorMapper):
            cmap = colors
            self._colors =  []
            mapped_colors = cmap.map_screen(array(self._levels))
            for i in range(len(self._levels)):
                self._color_map_trait = tuple(mapped_colors[i])
                self._colors.append(self._color_map_trait_)

        # A list or tuple
        # This could be a length 3 or 4 sequence of scalars, which indicates
        # a color; otherwise, this is interpreted as a list of items to
        # be converted via self._color_map_trait.
        else:
            if len(colors) in (3,4) and \
                    (isscalar(colors[0]) and issubsctype(type(colors[0]), number)):
                self._color_map_trait = colors
                self._colors = [self._color_map_trait_] * len(self._levels)
            else:
                # if the list of colors is shorter than the list of levels, simply
                # repeat colors from the beginning of the list as needed
                self._colors = []
                for i in range(len(self._levels)):
                    self._color_map_trait = colors[i%len(colors)]    
                    self._colors.append(self._color_map_trait_)

        self._colors_cache_valid = True


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _index_data_changed_fired(self):
        self._level_cache_valid = False
        self.invalidate_draw()

    def _index_mapper_changed_fired(self):
        self._level_cache_valid = False

    def _value_data_changed_fired(self):
        self._level_cache_valid = False
        self.invalidate_draw()

    def _levels_changed(self):
        self._update_levels()
        self.invalidate_draw()
        #self.request_redraw()
        
    def _widths_changed(self):
        if self._level_cache_valid: 
            self._update_widths()
            self.invalidate_draw()

    def _styles_changed(self):
        if self._level_cache_valid: 
            self._update_styles()
            self.invalidate_draw()

    def _negative_style_changed(self):
        if self._level_cache_valid: 
            self._update_styles()
            self.invalidate_draw()

    def _positive_style_changed(self):
        if self._level_cache_valid: 
            self._update_styles()
            self.invalidate_draw()

    def _colors_changed(self):
        if self._level_cache_valid: 
            self._update_colors()
            self.invalidate_draw()

    #------------------------------------------------------------------------
    # Trait properties
    #------------------------------------------------------------------------

    def _get_color_mapper(self):
        if isinstance(self.colors, ColorMapper):
            return self.colors
        else:
            return None
