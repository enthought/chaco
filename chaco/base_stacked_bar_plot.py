
from __future__ import with_statement
import warnings

# Major library imports
from numpy import array, column_stack, zeros_like

# Enthought library imports
from enable.api import ColorTrait
from traits.api import Any, Bool, Float, Int, List, Property, Trait

# Chaco imports
from base_xy_plot import BaseXYPlot

def Alias(name):
    return Property(lambda obj: getattr(obj, name),
                    lambda obj, val: setattr(obj, name, val))

class BaseStackedBarPlot(BaseXYPlot):
    """ Represents the base class for candle- and bar-type plots that are
    multi-valued at each index point, and optionally have an extent in the
    index dimension.

    Implements the rendering logic and centralizes a lot of the visual
    attributes for these sorts of plots.  The gather and culling and
    clipping of data is up to individual subclasses.
    """

    #------------------------------------------------------------------------
    # Appearance traits
    #------------------------------------------------------------------------

    # The fill color of the marker.
    # TODO: this is a hack...need to see how to handle auto colors correctly
    color = List(Any)

    # The fill color of the bar
    fill_color = Alias("color")

    # The color of the rectangular box forming the bar.
    outline_color = ColorTrait("black")

    # The thickness, in pixels, of the outline to draw around the bar.  If
    # this is 0, no outline is drawn.
    line_width = Float(1.0)


    # List of colors to cycle through when auto-coloring is requested. Picked
    # and ordered to be red-green color-blind friendly, though should not
    # be an issue for blue-yellow.
    auto_colors = List(["green", "lightgreen", "blue", "lightblue", "red",
                        "pink", "darkgray", "silver"])


    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # currently used color -- basically using ColorTrait magic for color
    # designations.
    _current_color = ColorTrait("lightgray")

    # Override the base class definition of this because we store a list of
    # arrays and not a single array.
    _cached_data_pts = List()

    #------------------------------------------------------------------------
    # BaseXYPlot interface
    #------------------------------------------------------------------------

    def get_screen_points(self):
        # Override the BaseXYPlot implementation so that this is just
        # a pass-through, in case anyone calls it.
        pass

    #------------------------------------------------------------------------
    # Protected methods (subclasses should be able to use these directly
    # or wrap them)
    #------------------------------------------------------------------------

    def _render(self, gc, left, right, bar_maxes):
        stack = column_stack

        bottom = zeros_like(left)
        bottom = self.value_mapper.map_screen(bottom)

        with gc:
            widths = right - left

            if len(self.color)<len(bar_maxes):

                warnings.warn("Color count does not match data series count.")
                for i in range(len(bar_maxes)):
                    self.color.append(self.color[-1])
                
            idx = 0

            for bar_max in bar_maxes:

                top = bar_max

                if self.color[0] == "auto":
                    self.color = self.auto_colors[:len(left)]

                self._current_color = self.color[idx]

                # Draw the bars
                bars = stack((left, bottom, widths, top - bottom))

                gc.set_antialias(False)
                gc.set_stroke_color(self.outline_color_)
                gc.set_line_width(self.line_width)
                gc.rects(bars)
                if self.color in ("none", "transparent", "clear"):
                    gc.stroke_path()
                else:
                    gc.set_fill_color(self._current_color_)
                    gc.draw_path()
                bottom = top

                idx += 1


    def _render_icon(self, gc, x, y, width, height):
        min = array([y + 1])
        max = array([y + height - 1])
        bar_min = array([y + height / 3])
        bar_max = array([y + height - (height / 3)])
        center = array([y + (height / 2)])
        self._render(gc, array([x+width/4]), array([x+3*width/4]), bar_maxes)




