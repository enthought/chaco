from numpy import array, isscalar, issubsctype, linspace, number

# Enthought library imports
from enable.api import ColorTrait
from traits.api import Bool, Instance, Int, List, Property, \
        Range, Str, Trait, Tuple

# Local relative imports
from .base_2d_plot import Base2DPlot
from .color_mapper import ColorMapper


class BaseContourPlot(Base2DPlot):
    """ The base class for contour plots.  Mostly manages configuration and
    change events with colormap and contour parameters.
    """

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # Defines the levels to contour.
    # ``levels`` can be either: a list of floating point numbers that define
    # the value of the function at the contours; a positive integer, in which
    # case the range of the value is divided in the given number of equally
    # spaced levels; or "auto" (default), which divides the range in 10 levels
    levels = Trait("auto", Int, List)

    # The color(s) of the lines.
    # ``colors`` can be given as a color name, in which case all contours have
    # the same color, as a list of colors, or as a colormap. If the list of
    # colors is shorter than the number of levels, the values are repeated
    # from the beginning of the list. Default is black.
    # Colors are associated with levels of increasing value.
    colors = Trait(None, Str, Instance(ColorMapper), List, Tuple)

    # If present, the color mapper for the colorbar to look at.
    color_mapper = Property(Instance(ColorMapper))

    # A global alpha value to apply to all the contours
    alpha = Trait(1.0, Range(0.0, 1.0))

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

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


    def __init__(self, *args, **kwargs):
        super(BaseContourPlot, self).__init__(*args, **kwargs)
        if self.color_mapper:
            self.color_mapper.on_trait_change(self._update_color_mapper, "updated")
        return

    def _update_levels(self):
        """ Updates the levels cache.  """
        low, high = self.value.get_bounds()
        if self.levels == "auto":
            self._levels = list(linspace(low, high, 10))
        elif isinstance(self.levels, int):
            self._levels = list(linspace(low, high, self.levels))
        else:
            self._levels = self.levels
            self._levels.sort()
        self._level_cache_valid = True
        self._colors_cache_valid = False

    def _update_colors(self, numcolors=None):
        """ Update the colors cache using our color mapper and based
        on our number of levels.  The **mode** parameter accounts for fenceposting:
          - If **mode** is "poly", then the number of colors to generate is 1
            less than the number of levels
          - If **mode** is "line", then the number of colors to generate is
            equal to the number of levels
        """
        if numcolors is None:
            numcolors = len(self._levels)

        colors = self.colors
        # If we are given no colors, set a default for all levels
        if colors is None:
            self._color_map_trait = "black"
            self._colors = [self._color_map_trait_] * numcolors

        # If we are given a single color, apply it to all levels
        elif isinstance(colors, str):
            self._color_map_trait = colors
            self._colors = [self._color_map_trait_] * numcolors

        # If we are given a colormap, use it to map all the levels to colors
        elif isinstance(colors, ColorMapper):
            self._colors =  []
            mapped_colors = self.color_mapper.map_screen(array(self._levels))
            for i in range(numcolors):
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
                self._colors = [self._color_map_trait_] * numcolors
            else:
                # if the list of colors is shorter than the list of levels, simply
                # repeat colors from the beginning of the list as needed
                self._colors = []
                for i in range(len(self._levels)):
                    self._color_map_trait = colors[i%len(colors)]
                    self._colors.append(self._color_map_trait_)

        self._colors_cache_valid = True
        return


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _index_data_changed_fired(self):
        # If the index data has changed, the reset the levels cache (which
        # also triggers all the other caches to reset).
        self._level_cache_valid = False
        self.invalidate_and_redraw()

    def _value_data_changed_fired(self):
        # If the index data has changed, the reset the levels cache (which
        # also triggers all the other caches to reset).
        self._level_cache_valid = False
        self.invalidate_and_redraw()

    def _index_mapper_changed_fired(self):
        # If the index mapper has changed, then we need to redraw
        self.invalidate_and_redraw()

    def _update_color_mapper(self):
        # If the color mapper has changed, then we need to recompute the
        # levels and cached data associated with that.
        self._level_cache_valid = False
        self.invalidate_and_redraw()

    def _levels_changed(self):
        self._update_levels()
        self.invalidate_and_redraw()

    def _colors_changed(self):
        if self._level_cache_valid:
            self._update_colors()
            self.invalidate_and_redraw()

    #------------------------------------------------------------------------
    # Trait properties
    #------------------------------------------------------------------------

    def _get_color_mapper(self):
        if isinstance(self.colors, ColorMapper):
            return self.colors
        else:
            return None

    def _set_color_mapper(self, color_mapper):
        # Remove the dynamic event handler from the old color mapper
        if self.colors is not None and isinstance(self.colors, ColorMapper):
            self.colors.on_trait_change(self._update_color_mapper, "updated", remove=True)

            # Check to see if we should copy over the range as well
            if color_mapper is not None:
                if color_mapper.range is None and self.colors.range is not None:
                    color_mapper.range = self.colors.range

        # Attach the dynamic event handler to the new color mapper
        if color_mapper is not None:
            color_mapper.on_trait_change(self._update_color_mapper, "updated")

        self.colors = color_mapper
        self._update_color_mapper()
