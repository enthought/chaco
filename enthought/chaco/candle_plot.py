
# Major library imports
from numpy import array, column_stack, compress, concatenate, empty_like

# Enthought library imports
from enthought.enable.api import ColorTrait
from enthought.traits.api import Bool, Int, Instance, List, Property, Trait

# Chaco imports
from abstract_data_source import AbstractDataSource
from scatterplot import ScatterPlot

def Alias(name):
    return Property(lambda obj: getattr(obj, name),
                    lambda obj, val: setattr(obj, name, val))

def broaden(mask):
    """ Takes a 1D boolean mask array and returns a copy with all the non-zero
    runs widened by 1.
    """
    if len(mask) < 2:
        return mask
    # Note: the order in which these operations are performed is important.
    # Modifying newmask in-place with the |= operator only works for if
    # newmask[:-1] is the L-value.
    newmask = concatenate(([False], mask[1:] | mask[:-1]))
    newmask[:-1] |= mask[1:]
    return newmask


class CandlePlot(ScatterPlot):
    """ A plot consisting of a filled bar with an optional centerline and
    stems extending to extrema.  Usually used to represent some statistics
    on bins of data, with the centerline representing the mean, the bar
    extents representing +/- 1 standard dev or 10th/90th percentiles, and
    the stems extents representing the minimum and maximum samples.
    """

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # The minimum values at each index point.  If None, then no stem and no
    # endcap line will be drawn below each bar.
    min_values = Instance(AbstractDataSource)

    # The "lower" extent of the "bar", i.e. the value closest to the
    # corresponding value in min_values at each index.
    bar_min = Instance(AbstractDataSource)

    # Values that appear inside the bar, between bar_min and bar_max.  These
    # Are usually mean or median values, and are rendered with a solid line
    # of a different color than the bar fill color.  This can be None.
    center_values = Instance(AbstractDataSource)
    
    # The "upper" extent of the "bar", i.e. the value closest to the
    # corresponding value in max_values at each index.
    bar_max = Instance(AbstractDataSource)
    
    # The maximum value at each index point.  If None, then no stem and no
    # endcap line will be drawn above each bar.
    max_values = Instance(AbstractDataSource)

    #------------------------------------------------------------------------
    # Appearance traits
    #------------------------------------------------------------------------

    # The fill color of the bar
    bar_color = Alias("color")
    
    # The color of the rectangular box forming the bar.
    bar_line_color = Alias("outline_color")

    # The color of the stems reaching from the bar ends to the min and max
    # values.  Also the color of the endcap line segments at min and max.  If
    # None, this defaults to **bar_line_color**.
    stem_color = Trait(None, None, ColorTrait("black"))

    # The color of the line drawn across the bar at the center values.
    # If None, this defaults to **bar_line_color**.
    center_color = Trait(None, None, ColorTrait("outline_color"))

    # The thickness, in pixels, of the stem lines.  If None, this defaults
    # to **line_width**.
    stem_width = Trait(None, None, Int(1))

    # The thickeness, in pixels, of the line drawn across the bar at the
    # center values.  If None, this defaults to **line_width**.
    center_width = Trait(None, None, Int(1))
    
    # Whether or not to draw bars at the min and max extents of the error bar
    end_cap = Bool(True)

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # Override the base class definition of this because we store a list of
    # arrays and not a single array.
    _cached_data_pts = List()

    def map_data(self, screen_pt, all_values=True):
        """ Maps a screen space point into the "index" space of the plot.
        
        Overrides the BaseXYPlot implementation, and always returns an
        array of (index, value) tuples.
        """
        x, y = screen_pt
        if self.orientation == 'v':
            x, y = y, x
        return array((self.index_mapper.map_data(x),
                      self.value_mapper.map_data(y)))

    def _gather_points(self):
        index = self.index.get_data()
        mask = broaden(self.index_range.mask_data(index))

        if not mask.any():
            self._cached_data_pts = []
            self._cache_valid = True
            return

        data_pts = [compress(mask, index)]
        for v in (self.min_values, self.bar_min, self.center_values, self.bar_max, self.max_values):
            if v is None:
                data_pts.append(None)
            else:
                data_pts.append(compress(mask, v.get_data()))

        self._cached_data_pts = data_pts
        self._cache_valid = True

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        self._gather_points()
        if len(self._cached_data_pts) == 0:
            return
        
        index = self.index_mapper.map_screen(self._cached_data_pts[0])
        vals = []
        for v in self._cached_data_pts[1:]:
            if v is None:
                vals.append(None)
            else:
                vals.append(self.value_mapper.map_screen(v))
        gc.save_state()
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        self._render(gc, index, *vals)
        gc.restore_state() 

    def _render(self, gc, index, min, bar_min, center, bar_max, max):
        if len(index) == 0:
            return
        elif len(index) == 1:
            width = 5.0
        else:
            width = (index[1] - index[0]) / 2.5
        
        stack = column_stack
        gc.save_state()

        left = index - width
        right = index + width
        widths = empty_like(index)
        widths.fill(width * 2.0)

        # Draw the stem lines for min to max.  Draw these first so we can
        # draw the boxes on top.
        # A little tricky: we need to account for cases when either min or max
        # are None.  To do this, just draw to bar_min or from bar_max instead
        # of drawing a single line from min to max.
        if min is not None or max is not None:
            if self.stem_color is None:
                stem_color = self.bar_line_color_
            else:
                stem_color = self.stem_color_
            gc.set_stroke_color(stem_color)

            if self.stem_width is None:
                stem_width = self.line_width
            else:
                stem_width = self.stem_width
            gc.set_line_width(stem_width)
            
            if min is None:
                gc.line_set(stack((index, bar_max)), stack((index, max)))
                if self.end_cap:
                    gc.line_set(stack((left, max)), stack((right, max)))
            elif max is None:
                gc.line_set(stack((index, min)), stack((index, bar_min)))
                if self.end_cap:
                    gc.line_set(stack((left, min)), stack((right, min)))
            else:
                gc.line_set(stack((index, min)), stack((index, max)))
                if self.end_cap:
                    gc.line_set(stack((left, max)), stack((right, max)))
                    gc.line_set(stack((left, min)), stack((right, min)))
            gc.stroke_path()

        # Draw the candlestick boxes
        boxes = stack((left, bar_min, widths, bar_max - bar_min))
        gc.set_antialias(False)
        gc.set_stroke_color(self.outline_color_)
        gc.set_line_width(self.line_width)
        gc.rects(boxes)
        if self.color in ("none", "transparent", "clear"):
            gc.stroke_path()
        else:
            gc.set_fill_color(self.color_)
            gc.draw_path()

        # Draw the center line
        if center is not None:
            if self.center_color is None:
                gc.set_stroke_color(self.bar_line_color_)
            else:
                gc.set_stroke_color(self.center_color_)
            if self.center_width is None:
                gc.set_line_width(self.line_width)
            else:
                gc.set_line_width(self.center_width)
            gc.line_set(stack((left, center)), stack((right, center)))
            gc.stroke_path()

        gc.restore_state()

