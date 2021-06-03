# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# Major library imports
from numpy import array, column_stack

# Enthought library imports
from enable.api import ColorTrait
from traits.api import Bool, Float, Int, List, Property, Trait

# Chaco imports
from .base_xy_plot import BaseXYPlot

# TODO: allow to set the width of the bar


def Alias(name):
    return Property(
        lambda obj: getattr(obj, name),
        lambda obj, val: setattr(obj, name, val),
    )


class BaseCandlePlot(BaseXYPlot):
    """Represents the base class for candle- and bar-type plots that are
    multi-valued at each index point, and optionally have an extent in the
    index dimension.

    Implements the rendering logic and centralizes a lot of the visual
    attributes for these sorts of plots.  The gather and culling and
    clipping of data is up to individual subclasses.
    """

    # ------------------------------------------------------------------------
    # Appearance traits
    # ------------------------------------------------------------------------

    #: The fill color of the marker.
    color = ColorTrait("black")

    #: The fill color of the bar
    bar_color = Alias("color")

    #: The color of the rectangular box forming the bar.
    bar_line_color = Alias("outline_color")

    #: The color of the stems reaching from the bar ends to the min and max
    #: values.  Also the color of the endcap line segments at min and max.  If
    #: None, this defaults to **bar_line_color**.
    stem_color = Trait(None, None, ColorTrait("black"))

    #: The color of the line drawn across the bar at the center values.
    #: If None, this defaults to **bar_line_color**.
    center_color = Trait(None, None, ColorTrait("black"))

    #: The color of the outline to draw around the bar.
    outline_color = ColorTrait("black")

    #: The thickness, in pixels, of the outline to draw around the bar.  If
    #: this is 0, no outline is drawn.
    line_width = Float(1.0)

    #: The thickness, in pixels, of the stem lines.  If None, this defaults
    #: to **line_width**.
    stem_width = Trait(None, None, Int(1))

    #: The thickeness, in pixels, of the line drawn across the bar at the
    #: center values.  If None, this defaults to **line_width**.
    center_width = Trait(None, None, Int(1))

    #: Whether or not to draw bars at the min and max extents of the error bar
    end_cap = Bool(True)

    # ------------------------------------------------------------------------
    # Private traits
    # ------------------------------------------------------------------------

    # Override the base class definition of this because we store a list of
    # arrays and not a single array.
    _cached_data_pts = List()

    # ------------------------------------------------------------------------
    # BaseXYPlot interface
    # ------------------------------------------------------------------------

    def get_screen_points(self):
        # Override the BaseXYPlot implementation so that this is just
        # a pass-through, in case anyone calls it.
        pass

    # ------------------------------------------------------------------------
    # Protected methods (subclasses should be able to use these directly
    # or wrap them)
    # ------------------------------------------------------------------------

    def _render(self, gc, right, left, min, bar_min, center, bar_max, max):
        stack = column_stack

        with gc:
            widths = right - left
            bar_vert_center = left + widths / 2.0

            # Draw the stem lines for min to max.  Draw these first so we can
            # draw the boxes on top.
            # A little tricky: we need to account for cases when either min or max
            # are None.  To do this, just draw to bar_min or from bar_max instead
            # of drawing a single line from min to max.
            if min is not None or max is not None:
                if self.stem_color is None:
                    stem_color = self.outline_color_
                else:
                    stem_color = self.stem_color_
                gc.set_stroke_color(stem_color)

                if self.stem_width is None:
                    stem_width = self.line_width
                else:
                    stem_width = self.stem_width
                gc.set_line_width(stem_width)

                if min is None:
                    gc.line_set(
                        stack((bar_vert_center, bar_max)),
                        stack((bar_vert_center, max)),
                    )
                    if self.end_cap:
                        gc.line_set(stack((left, max)), stack((right, max)))
                elif max is None:
                    gc.line_set(
                        stack((bar_vert_center, min)),
                        stack((bar_vert_center, bar_min)),
                    )
                    if self.end_cap:
                        gc.line_set(stack((left, min)), stack((right, min)))
                else:
                    gc.line_set(
                        stack((bar_vert_center, min)),
                        stack((bar_vert_center, max)),
                    )
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
                    gc.set_stroke_color(self.outline_color_)
                else:
                    gc.set_stroke_color(self.center_color_)
                if self.center_width is None:
                    gc.set_line_width(self.line_width)
                else:
                    gc.set_line_width(self.center_width)
                gc.line_set(stack((left, center)), stack((right, center)))
                gc.stroke_path()

    def _render_icon(self, gc, x, y, width, height):
        min = array([y + 1])
        max = array([y + height - 1])
        bar_min = array([y + height / 3])
        bar_max = array([y + height - (height / 3)])
        center = array([y + (height / 2)])
        self._render(
            gc,
            array([x + width / 4]),
            array([x + 3 * width / 4]),
            min,
            bar_min,
            center,
            bar_max,
            max,
        )
