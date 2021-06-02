""" Defines the DataLabel class and related trait and function.
"""
# Major library imports
from math import sqrt
from numpy import array, asarray, inf
from numpy.linalg import norm

# Enthought library imports
from traits.api import Any, ArrayOrNone, Bool, Enum, Float, Int, List, \
     Str, Tuple, Trait, observe, Property
from enable.api import ColorTrait, MarkerTrait

# Local, relative imports
from .plots.scatterplot import render_markers
from .tooltip import ToolTip


# Specifies the position of a label relative to its target.  This can
# be one of the text strings indicated, or a tuple or list of floats
# representing the (x_offset, y_offset) in screen space of the label's
# lower left corner.
LabelPositionTrait = Trait("top right",
                           Enum("bottom", "left", "right", "top",
                                "top right", "top left",
                                "bottom left", "bottom right"),
                           Tuple, List)


def draw_arrow(gc, pt1, pt2, color, arrowhead_size=10.0, offset1=0,
               offset2=0, arrow=None, minlen=0, maxlen=inf):
    """ Renders an arrow from *pt1* to *pt2*.  If gc is None, then just returns
    the arrow object.

    Parameters
    ==========
    gc : graphics context
        where to render the arrow
    pt1 : point
        the origin of the arrow
    pt2 : point
        where the arrow is pointing
    color : a 3- or 4-tuple of color value
        the color to use for the arrow stem and head
    arrowhead_size : number
        screen units corresponding to the length of the arrowhead
    offset1 : number
        the amount of space from the start of the arrow to pt1
    offset2 : number
        the amount of space from the tip of the arrow to pt2
    arrow : object
        an opaque object returned by previous calls to draw_arrow.  If this
        argument is provided, all other arguments (except gc) are ignored
    minlen: number or None
        the minimum length of the arrow; if the arrow is shorter than this,
        it will not be drawn
    maxlen: number or None
        the maximum length of the arrow; if the arrow is longer than this, it
        will not be drawn

    Returns
    =======
    An 'arrow' (opaque object) which can be passed in to subsequent
    calls to this method to short-circuit some of the computation.
    Even if an arrow is not drawn (due to minlen/maxlen restrictions),
    an arrow will be returned.
    """

    if arrow is None:
        pt1 = asarray(pt1)
        pt2 = asarray(pt2)

        unit_vec = pt2 - pt1
        unit_vec /= norm(unit_vec)

        if unit_vec[0] == 0:
            perp_vec = array((0.3 * arrowhead_size, 0))
        elif unit_vec[1] == 0:
            perp_vec = array((0, 0.3 * arrowhead_size))
        else:
            slope = unit_vec[1] / unit_vec[0]
            perp_slope = -1 / slope
            perp_vec = array((1.0, perp_slope))
            perp_vec *= 0.3 * arrowhead_size / norm(perp_vec)

        pt1 = pt1 + offset1 * unit_vec
        pt2 = pt2 - offset2 * unit_vec

        arrowhead_l = pt2 - (arrowhead_size * unit_vec + perp_vec)
        arrowhead_r = pt2 - (arrowhead_size * unit_vec - perp_vec)
        arrow = (pt1, pt2, arrowhead_l, arrowhead_r)
    else:
        pt1, pt2, arrowhead_l, arrowhead_r = arrow

    arrowlen = norm(pt2 - pt1)
    if arrowlen < minlen or arrowlen > maxlen:
        # This is the easiest way to circumvent the actual drawing
        gc = None

    if gc is not None:
        gc.set_stroke_color(color)
        gc.set_fill_color(color)
        gc.begin_path()
        gc.move_to(*pt1)
        gc.line_to(*pt2)
        gc.stroke_path()
        gc.move_to(*pt2)
        gc.line_to(*arrowhead_l)
        gc.line_to(*arrowhead_r)
        gc.fill_path()
    return arrow


def find_region(px, py, x, y, x2, y2):
    """Classify the location of the point (px, py) relative to a rectangle.

    (x, y) and (x2, y2) are the lower-left and upper-right corners of the
    rectangle, respectively.  (px, py) is classified as "left", "right",
    "top", "bottom" or "inside", according to the following diagram:

            \     top      /
             \            /
              +----------+
         left |  inside  | right
              +----------+
             /            \ 
            /    bottom    \ 

    """
    if px < x:
        dx = x - px
        if py > y2 + dx:
            region = 'top'
        elif py < y - dx:
            region = 'bottom'
        else:
            region = 'left'
    elif px > x2:
        dx = px - x2
        if py > y2 + dx:
            region = 'top'
        elif py < y - dx:
            region = 'bottom'
        else:
            region = 'right'
    else:  # x <= px <= x2
        if py > y2:
            region = 'top'
        elif py < y:
            region = 'bottom'
        else:
            region = 'inside'
    return region


class DataLabel(ToolTip):
    """ A label on a point in data space.

    Optionally, an arrow is drawn to the point.
    """

    #: The symbol to use if **marker** is set to "custom". This attribute must
    #: be a compiled path for the given Kiva context.
    custom_symbol = Any

    #: The point in data space where this label should anchor itself.
    data_point = ArrayOrNone()

    #: The location of the data label relative to the data point.
    label_position = LabelPositionTrait

    #: The format string that determines the label's text.  This string is
    #: formatted using a dict containing the keys 'x' and 'y', corresponding to
    #: data space values.
    label_format = Str("(%(x)f, %(y)f)")

    #: The text to show on the label, or above the coordinates for the label, if
    #: show_label_coords is True
    label_text = Str

    #: Flag whether to show coordinates with the label or not.
    show_label_coords = Bool(True)

    #: Does the label clip itself against the main plot area?  If not, then
    #: the label draws into the padding area (where axes typically reside).
    clip_to_plot = Bool(True)

    #: The center x position (average of x and x2)
    xmid = Property(Float, observe=['x', 'x2'])

    #: The center y position (average of y and y2)
    ymid = Property(Float, observe=['y', 'y2'])

    #: 'box' is a simple rectangular box, with an arrow that is a single line
    #: with an arrowhead at the data point.
    #: 'bubble' can be given rounded corners (by setting `corner_radius`), and
    #: the 'arrow' is a thin triangular wedge with its point at the data point.
    #: When label_style is 'bubble', the following traits are ignored:
    #: arrow_size, arrow_color, arrow_root, and arrow_max_length.
    label_style = Enum('box', 'bubble')

    #----------------------------------------------------------------------
    # Marker traits
    #----------------------------------------------------------------------

    #: Mark the point on the data that this label refers to?
    marker_visible = Bool(True)

    #: The type of marker to use.  This is a mapped trait using strings as the
    #: keys.
    marker = MarkerTrait

    #: The pixel size of the marker (doesn't include the thickness of the
    #: outline).
    marker_size = Int(4)

    #: The thickness, in pixels, of the outline to draw around the marker.
    #: If this is 0, no outline will be drawn.
    marker_line_width = Float(1.0)

    #: The color of the inside of the marker.
    marker_color = ColorTrait("red")

    #: The color out of the border drawn around the marker.
    marker_line_color = ColorTrait("black")

    #----------------------------------------------------------------------
    # Arrow traits
    #----------------------------------------------------------------------

    #: Draw an arrow from the label to the data point?  Only
    #: used if **data_point** is not None.
    arrow_visible = Bool(True)   # FIXME: replace with some sort of ArrowStyle

    #: The length of the arrowhead, in screen points (e.g., pixels).
    arrow_size = Float(10)

    #: The color of the arrow.
    arrow_color = ColorTrait("black")

    #: The position of the base of the arrow on the label.  If this
    #: is 'auto', then the label uses **label_position**.  Otherwise, it
    #: treats the label as if it were at the label position indicated by
    #: this attribute.
    arrow_root = Trait("auto", "auto", "top left", "top right", "bottom left",
                       "bottom right", "top center", "bottom center",
                       "left center", "right center")

    #: The minimum length of the arrow before it will be drawn.  By default,
    #: the arrow will be drawn regardless of how short it is.
    arrow_min_length = Float(0)

    #: The maximum length of the arrow before it will be drawn.  By default,
    #: the arrow will be drawn regardless of how long it is.
    arrow_max_length = Float(inf)

    #----------------------------------------------------------------------
    # Bubble traits
    #----------------------------------------------------------------------

    #: The radius (in screen coordinates) of the curved corners of the "bubble".
    corner_radius = Float(10)

    #-------------------------------------------------------------------------
    # Private traits
    #-------------------------------------------------------------------------

    # Tuple (sx, sy) of the mapped screen coordinates of **data_point**.
    _screen_coords = Any

    _cached_arrow = Any

    # When **arrow_root** is 'auto', this determines the location on the data
    # label from which the arrow is drawn, based on the position of the label
    # relative to its data point.
    _position_root_map = {
        "top left": "bottom right",
        "top right": "bottom left",
        "bottom left": "top right",
        "bottom right": "top left",
        "top center": "bottom center",
        "bottom center": "top center",
        "left center": "right center",
        "right center": "left center"
        }

    _root_positions = {
        "bottom right": ("x2", "y"),
        "bottom left": ("x", "y"),
        "top right": ("x2", "y2"),
        "top left": ("x", "y2"),
        "top center": ("xmid", "y2"),
        "bottom center": ("xmid", "y"),
        "left center": ("x", "ymid"),
        "right center": ("x2", "ymid"),
        }

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws the tooltip overlaid on another component.

        Overrides and extends ToolTip.overlay()
        """
        if self.clip_to_plot:
            gc.save_state()
            c = component
            gc.clip_to_rect(c.x, c.y, c.width, c.height)

        self.do_layout()

        if self.label_style == 'box':
            self._render_box(component, gc, view_bounds=view_bounds,
                             mode=mode)
        else:
            self._render_bubble(component, gc, view_bounds=view_bounds,
                                mode=mode)

        # draw the marker
        if self.marker_visible:
            render_markers(gc, [self._screen_coords],
                           self.marker, self.marker_size,
                           self.marker_color_, self.marker_line_width,
                           self.marker_line_color_, self.custom_symbol)

        if self.clip_to_plot:
            gc.restore_state()

    def _render_box(self, component, gc, view_bounds=None, mode='normal'):
        # draw the arrow if necessary
        if self.arrow_visible:
            if self._cached_arrow is None:
                if self.arrow_root in self._root_positions:
                    ox, oy = self._root_positions[self.arrow_root]
                else:
                    if self.arrow_root == "auto":
                        arrow_root = self.label_position
                    else:
                        arrow_root = self.arrow_root
                    pos = self._position_root_map.get(arrow_root, "DUMMY")
                    ox, oy = self._root_positions.get(pos,
                                        (self.x + self.width / 2,
                                         self.y + self.height / 2))

                if type(ox) == str:
                    ox = getattr(self, ox)
                    oy = getattr(self, oy)
                self._cached_arrow = draw_arrow(gc, (ox, oy),
                                            self._screen_coords,
                                            self.arrow_color_,
                                            arrowhead_size=self.arrow_size,
                                            offset1=3,
                                            offset2=self.marker_size + 3,
                                            minlen=self.arrow_min_length,
                                            maxlen=self.arrow_max_length)
            else:
                draw_arrow(gc, None, None, self.arrow_color_,
                           arrow=self._cached_arrow,
                           minlen=self.arrow_min_length,
                           maxlen=self.arrow_max_length)

        # layout and render the label itself
        ToolTip.overlay(self, component, gc, view_bounds, mode)

    def _render_bubble(self, component, gc, view_bounds=None, mode='normal'):
        """ Render the bubble label in the graphics context. """
        # (px, py) is the data point in screen space.
        px, py = self._screen_coords

        # (x, y) is the lower left corner of the label.
        x = self.x
        y = self.y
        # (x2, y2) is the upper right corner of the label.
        x2 = self.x2
        y2 = self.y2
        # r is the corner radius.
        r = self.corner_radius

        if self.arrow_visible:
            # FIXME: Make 'gap_width' a configurable trait (and give it a
            #        better name).
            max_gap_width = 10
            gap_width = min(max_gap_width,
                            abs(x2 - x - 2 * r),
                            abs(y2 - y - 2 * r))
            region = find_region(px, py, x, y, x2, y2)

            # Figure out where the "arrow" connects to the "bubble".
            if region == 'left' or region == 'right':
                gap_start = py - gap_width / 2
                if gap_start < y + r:
                    gap_start = y + r
                elif gap_start > y2 - r - gap_width:
                    gap_start = y2 - r - gap_width
                by = gap_start + 0.5 * gap_width
                if region == 'left':
                    bx = x
                else:
                    bx = x2
            else:
                gap_start = px - gap_width / 2
                if gap_start < x + r:
                    gap_start = x + r
                elif gap_start > x2 - r - gap_width:
                    gap_start = x2 - r - gap_width
                bx = gap_start + 0.5 * gap_width
                if region == 'top':
                    by = y2
                else:
                    by = y
            arrow_len = sqrt((px - bx)**2 + (py - by)**2)

        arrow_visible = (self.arrow_visible and
                         (arrow_len >= self.arrow_min_length))

        with gc:
            if self.border_visible:
                gc.set_line_width(self.border_width)
                gc.set_stroke_color(self.border_color_)
            else:
                gc.set_line_width(0)
                gc.set_stroke_color((0, 0, 0, 0))
            gc.set_fill_color(self.bgcolor_)

            # Start at the lower left, on the left edge where the curved
            # part of the box ends.
            gc.move_to(x, y + r)

            # Draw the left side and the upper left curved corner.
            if arrow_visible and region == 'left':
                gc.line_to(x, gap_start)
                gc.line_to(px, py)
                gc.line_to(x, gap_start + gap_width)
            gc.arc_to(x, y2, x + r, y2, r)

            # Draw the top and the upper right curved corner.
            if arrow_visible and region == 'top':
                gc.line_to(gap_start, y2)
                gc.line_to(px, py)
                gc.line_to(gap_start + gap_width, y2)
            gc.arc_to(x2, y2, x2, y2 - r, r)

            # Draw the right side and the lower right curved corner.
            if arrow_visible and region == 'right':
                gc.line_to(x2, gap_start + gap_width)
                gc.line_to(px, py)
                gc.line_to(x2, gap_start)
            gc.arc_to(x2, y, x2 - r, y, r)

            # Draw the bottom and the lower left curved corner.
            if arrow_visible and region == 'bottom':
                gc.line_to(gap_start + gap_width, y)
                gc.line_to(px, py)
                gc.line_to(gap_start, y)
            gc.arc_to(x, y, x, y + r, r)

            # Finish the "bubble".
            gc.draw_path()

            self._draw_overlay(gc)

    def _do_layout(self, size=None):
        """Computes the size and position of the label and arrow.

        Overrides and extends ToolTip._do_layout()
        """
        if not self.component or not hasattr(self.component, "map_screen"):
            return

        # Call the parent class layout.  This computes all the label
        ToolTip._do_layout(self)

        self._screen_coords = self.component.map_screen([self.data_point])[0]
        sx, sy = self._screen_coords

        if isinstance(self.label_position, str):
            orientation = self.label_position
            if ("left" in orientation) or ("right" in orientation):
                if " " not in orientation:
                    self.y = sy - self.height / 2
                if "left" in orientation:
                    self.outer_x = sx - self.outer_width - 1
                elif "right" in orientation:
                    self.outer_x = sx
            if ("top" in orientation) or ("bottom" in orientation):
                if " " not in orientation:
                    self.x = sx - self.width / 2
                if "bottom" in orientation:
                    self.outer_y = sy - self.outer_height - 1
                elif "top" in orientation:
                    self.outer_y = sy
            if "center" in orientation:
                if " " not in orientation:
                    self.x = sx - (self.width / 2)
                    self.y = sy - (self.height / 2)
                else:
                    self.x = sx - (self.outer_width / 2) - 1
                    self.y = sy - (self.outer_height / 2) - 1
        else:
            self.x = sx + self.label_position[0]
            self.y = sy + self.label_position[1]

        self._cached_arrow = None

    def _data_point_changed(self, old, new):
        if new is not None:
            self._create_new_labels()

    def _label_format_changed(self, old, new):
        self._create_new_labels()

    def _label_text_changed(self, old, new):
        self._create_new_labels()

    def _show_label_coords_changed(self, old, new):
        self._create_new_labels()

    def _create_new_labels(self):
        pt = self.data_point
        if pt is not None:
            if self.show_label_coords:
                self.lines = [self.label_text,
                              self.label_format % {"x": pt[0], "y": pt[1]}]
            else:
                self.lines = [self.label_text]

    def _component_changed(self, old, new):
        for comp, attach in ((old, False), (new, True)):
            if comp is not None:
                if hasattr(comp, 'index_mapper'):
                    self._modify_mapper_listeners(comp.index_mapper,
                                                  attach=attach)
                if hasattr(comp, 'value_mapper'):
                    self._modify_mapper_listeners(comp.value_mapper,
                                                  attach=attach)

    def _modify_mapper_listeners(self, mapper, attach=True):
        if mapper is not None:
            mapper.observe(self._handle_mapper, 'updated', remove=not attach)

    def _handle_mapper(self, event):
        # This gets fired whenever a mapper on our plot fires its
        # 'updated' event.
        self._layout_needed = True

    @observe("arrow_size,arrow_root,arrow_min_length,arrow_max_length")
    def _invalidate_arrow(self, event):
        self._cached_arrow = None
        self._layout_needed = True

    @observe("label_position,position.items,bounds.items")
    def _invalidate_layout(self, event):
        self._layout_needed = True

    def _get_xmid(self):
        return 0.5 * (self.x + self.x2)

    def _get_ymid(self):
        return 0.5 * (self.y + self.y2)
