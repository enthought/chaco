""" Defines the DataLabel class and related trait and function.
"""
# Major library imports
from numpy import array, asarray, inf
from numpy.linalg import norm

# Enthought library imports
from enthought.traits.api import Any, Array, Bool, Enum, Float, Int, List, \
     Str, Tuple, Trait
from enthought.enable2.api import ColorTrait

# Local, relative imports
from scatterplot import render_markers
from scatter_markers import marker_trait
from tooltip import ToolTip


# Specifies the position of a label relative to its target.  This can
# be one of the text strings indicated, or a tuple or list of floats representing
# the (x_offset, y_offset) in screen space of the label's lower left corner.
LabelPositionTrait = Trait("top right",
                           Enum("bottom", "left", "right", "top",
                                "top right", "top left", "bottom left", "bottom right"),
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

        unit_vec = (pt2-pt1)
        unit_vec /= norm(unit_vec)

        if unit_vec[0] == 0:
            perp_vec = array((0.3 * arrowhead_size,0))
        elif unit_vec[1] == 0:
            perp_vec = array((0,0.3 * arrowhead_size))
        else:
            slope = unit_vec[1]/unit_vec[0]
            perp_slope = -1/slope
            perp_vec = array((1.0, perp_slope))
            perp_vec *= 0.3 * arrowhead_size / norm(perp_vec)

        pt1 = pt1 + offset1 * unit_vec
        pt2 = pt2 - offset2 * unit_vec

        arrowhead_l = pt2 - (arrowhead_size*unit_vec + perp_vec)
        arrowhead_r = pt2 - (arrowhead_size*unit_vec - perp_vec)
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


class DataLabel(ToolTip):
    """ A label on a point in data space, optionally with an arrow to the point. 
    """

    # The symbol to use if **marker** is set to "custom". This attribute must
    # be a compiled path for the given Kiva context.
    custom_symbol = Any
    
    # The point in data space where this label should anchor itself.
    data_point = Trait(None, None, Tuple, List, Array)

    # The location of the data label relative to the data point.
    label_position = LabelPositionTrait

    # The format string that determines the label's text.  This string is
    # formatted using a dict containing the keys 'x' and 'y', corresponding to
    # data space values.
    label_format = Str("(%(x)f, %(y)f)")

    # Does the label clip itself against the main plot area?  If not, then
    # the label draws into the padding area (where axes typically reside).
    clip_to_plot = Bool(True)

    #----------------------------------------------------------------------
    # Marker traits
    #----------------------------------------------------------------------

    # Mark the point on the data that this label refers to?
    marker_visible = Bool(True)

    # The type of marker to use.  This is a mapped trait using strings as the
    # keys.
    marker = marker_trait
    
    # The pixel size of the marker (doesn't include the thickness of the outline).
    marker_size = Int(4)
    
    # The thickness, in pixels, of the outline to draw around the marker.  If
    # this is 0, no outline will be drawn.
    marker_line_width = Float(1.0)

    # The color of the inside of the marker.
    marker_color = ColorTrait("red")

    # The color out of the border drawn around the marker.
    marker_line_color = ColorTrait("black")

    #----------------------------------------------------------------------
    # Arrow traits
    #----------------------------------------------------------------------
    
    # Draw an arrow from the label to the data point?  Only
    # used if **data_point** is not None.
    arrow_visible = Bool(True)   # FIXME: replace with some sort of ArrowStyle

    # The length of the arrowhead, in screen points (e.g., pixels).
    arrow_size = Float(5)

    # The color of the arrow.
    arrow_color = ColorTrait("black")

    # The position of the base of the arrow on the label.  If this
    # is 'auto', then the label uses **label_position**.  Otherwise, it treats
    # the label as if it were at the label position indicated by this attribute.
    arrow_root = Trait("auto", "auto", "top left", "top right", "bottom left",
                       "bottom right", "center")

    # The minimum length of the arrow before it will be drawn.  By default,
    # the arrow will be drawn regardless of how short it is.
    arrow_min_length = Float(0)

    # The maximum length of the arrow before it will be drawn.  By default,
    # the arrow will be drawn regardless of how long it is.
    arrow_max_length = Float(inf)

    #-------------------------------------------------------------------------
    # Private traits
    #-------------------------------------------------------------------------

    # Tuple (sx, sy) of the mapped screen coordinates of **data_point**.
    _screen_coords = Any

    _cached_arrow = Any

    # When **arrow_root** is 'auto', this determines the location on the data label
    # from which the arrow is drawn, based on the position of the label relative
    # to its data point.
    _position_root_map = {
        "top left": "bottom right",
        "top right": "bottom left",
        "bottom left": "top right",
        "bottom right": "top left",
        }

    _root_positions = {
        "bottom right": ("x2", "y"),
        "bottom left": ("x", "y"),
        "top right": ("x2", "y2"),
        "top left": ("x", "y2"),
        }


    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws the tooltip overlaid on another component.
        
        Overrides ToolTip.
        """
        if self.clip_to_plot:
            gc.save_state()
            c = component
            gc.clip_to_rect(c.x, c.y, c.width, c.height)

        self.do_layout()
        
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
                    ox, oy = self._root_positions.get(
                                 self._position_root_map.get(arrow_root, "DUMMY"),
                                 (self.x+self.width/2, self.y+self.height/2)
                                 )
                    
                if type(ox) == str:
                    ox = getattr(self, ox)
                    oy = getattr(self, oy)
                self._cached_arrow = draw_arrow(gc, (ox, oy), self._screen_coords,
                                                self.arrow_color_,
                                                offset1=3,
                                                offset2=self.marker_size+3,
                                                minlen=self.arrow_min_length,
                                                maxlen=self.arrow_max_length)
            else:
                draw_arrow(gc, None, None, self.arrow_color_, 
                           arrow=self._cached_arrow,
                           minlen=self.arrow_min_length, 
                           maxlen=self.arrow_max_length)

        # layout and render the label itself
        ToolTip.overlay(self, component, gc, view_bounds, mode)

        # draw the marker
        if self.marker_visible:
            render_markers(gc, [self._screen_coords], self.marker, self.marker_size,
                           self.marker_color_, self.marker_line_width,
                           self.marker_line_color_, self.custom_symbol)

        if self.clip_to_plot:
            gc.restore_state()

    def _do_layout(self, size=None):
        """Computes the size and position of the label and arrow.
        
        Overrides ToolTip.
        """
        if not self.component or not hasattr(self.component, "map_screen"):
            return
        ToolTip._do_layout(self)

        self._screen_coords = self.component.map_screen(self.data_point)
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
            if orientation == "center":
                self.x = sx - (self.width/2)
                self.y = sy - (self.height/2)
        else:
            self.x = sx + self.label_position[0]
            self.y = sy + self.label_position[1]

        self._cached_arrow = None
        return

    def _data_point_changed(self, old, new):
        if new is not None:
            self._create_new_labels()

    def _label_format_changed(self, old, new):
        self._create_new_labels()

    def _create_new_labels(self):
        pt = self.data_point
        if pt is not None:
            self.lines = [self.label_format % {"x": pt[0], "y": pt[1]}]

    def _component_changed(self, old, new):
        for comp, attach in ((old, False), (new, True)):
            if comp is not None:
                if hasattr(comp, 'index_mapper'):
                    self._modify_mapper_listeners(comp.index_mapper, attach=attach)
                if hasattr(comp, 'value_mapper'):
                    self._modify_mapper_listeners(comp.value_mapper, attach=attach)
        return

    def _modify_mapper_listeners(self, mapper, attach=True):
        if mapper is not None:
            mapper.on_trait_change(self._handle_mapper, 'updated', remove=not attach)
        return

    def _handle_mapper(self):
        # This gets fired whenever a mapper on our plot fires its 'updated' event.
        self._layout_needed = True

    def _arrow_size_changed(self):
        self._cached_arrow = None
        self._layout_needed = True

    def _arrow_root_changed(self):
        self._cached_arrow = None
        self._layout_needed = True

    def _arrow_min_length_changed(self):
        self._cached_arrow = None
        self._layout_needed = True

    def _arrow_max_length_changed(self):
        self._cached_arrow = None
        self._layout_needed = True

    def _label_position_changed(self):
        self._layout_needed = True

    def _position_changed(self, old, new):
        super(DataLabel, self)._position_changed(old, new)
        self._layout_needed = True

    def _position_items_changed(self, event):
        super(DataLabel, self)._position_items_changed(event)
        self._layout_needed = True

    def _bounds_changed(self, old, new):
        super(DataLabel, self)._bounds_changed(old, new)
        self._layout_needed = True

    def _bounds_items_changed(self, event):
        super(DataLabel, self)._bounds_items_changed(event)
        self._layout_needed = True

