""" Defines the PlotAxis class, and associated validator and UI.
"""
# Major library import
from numpy import array, around, absolute, cos, dot, float64, inf, pi, \
                  sqrt, sin, transpose

# Enthought Library imports
from enthought.enable2.api import black_color_trait, transparent_color_trait, \
                                  LineStyle
from enthought.kiva.traits.kiva_font_trait import KivaFont
from enthought.traits.api import Any, Float, Int, Str, Trait, Unicode, \
                                 Bool, Event, List, Array, Instance, Enum, false, \
                                 true, TraitError
from enthought.traits.ui.api import View, HGroup, Group, VGroup, Item, TextEditor

# Local relative imports
from ticks import AbstractTickGenerator, DefaultTickGenerator
from abstract_mapper import AbstractMapper
from abstract_overlay import AbstractOverlay
from label import Label
from log_mapper import LogMapper


def float_or_auto(val):
    """
    Validator function that returns *val* if *val* is either a number or
    the word 'auto'.  This is used as a validator for the text editor
    in the Traits UI for the **tick_interval** trait.
    """
    try:
        return float(val)
    except:
        if isinstance(val, basestring) and val == "auto":
            return val
    raise TraitError, "Tick interval must be a number or 'auto'."


# Traits UI for a PlotAxis.
AxisView = View(VGroup(
                Group(
                    Item("title", label="Title", editor=TextEditor()),
                    #Item("title_font", label="Font"),
                    Item("title_color", label="Color", style="custom"),
                         #editor=EnableRGBAColorEditor()),
                    Item("tick_interval", label="Interval", editor=TextEditor(evaluate=float_or_auto)),
                    label="Main"),
                Group(
                    Item("tick_color", label="Color", style="custom"),
                         #editor=EnableRGBAColorEditor()),
                    Item("tick_weight", label="Thickness"),
                    #Item("tick_label_font", label="Font"),
                    Item("tick_label_color", label="Label color", style="custom"),
                         #editor=EnableRGBAColorEditor()),
                    HGroup(
                        Item("tick_in", label="Tick in"),
                        Item("tick_out", label="Tick out"),
                        ),
                    Item("tick_visible", label="Visible"),
                    label="Ticks"),
                Group(
                    Item("axis_line_color", label="Color", style="custom"),
                         #editor=EnableRGBAColorEditor()),
                    Item("axis_line_weight", label="Thickness"),
                    Item("axis_line_visible", label="Visible"),
                    label="Line"),
                ),
                buttons = ["OK", "Cancel"]
            )



class PlotAxis(AbstractOverlay):
    """
    The PlotAxis is a visual component that can be rendered on its own as
    a standalone component or attached as an overlay to another component.
    (To attach it as an overlay, set its **component** attribute.)

    When it is attached as an overlay, it draws into the padding around
    the component.
    """

    # The mapper that drives this axis.
    mapper = Instance(AbstractMapper)

    # The text of the axis title.
    title = Trait('', Str, Unicode) #May want to add PlotLabel option

    # The font of the title.
    title_font = KivaFont('modern 12')

    # The color of the title.
    title_color = black_color_trait

    # Not used right now.
    markers = Any     # TODO: Implement this

    # The thickness (in pixels) of each tick.
    tick_weight = Float(1.0)

    # The color of the ticks.
    tick_color = black_color_trait

    # The font of the tick labels.
    tick_label_font = KivaFont('modern 10')

    # The color of the tick labels.
    tick_label_color = black_color_trait

    # A callable that is passed the numerical value of each tick label and
    # that returns a string.
    tick_label_formatter = Any

    # The number of pixels by which the ticks extend into the plot area.
    tick_in = Int(5)

    # The number of pixels by which the ticks extend into the label area.
    tick_out = Int(5)

    # Are ticks visible at all?
    tick_visible = true

    # The dataspace interval between ticks.
    tick_interval = Trait('auto', 'auto', Float)

    # A callable that implements the AbstractTickGenerator interface.
    tick_generator = Trait(DefaultTickGenerator(), Instance(AbstractTickGenerator))

    # The location of the axis relative to the plot.  This determines where
    # the axis title is located relative to the axis line.
    orientation = Enum("top", "bottom", "left", "right")

    # Is the axis line visible?
    axis_line_visible = true

    # The color of the axis line.
    axis_line_color = black_color_trait

    # The line thickness (in pixels) of the axis line.
    axis_line_weight = Float(1.0)

    # The dash style of the axis line.
    axis_line_style = LineStyle('solid')

    # A special version of the axis line that is more useful for geophysical
    # plots.
    small_haxis_style = false     # TODO: MOVE THIS OUT OF HERE!

    # Does the axis ensure that its end labels fall within its bounding area?
    ensure_labels_bounded = false

    # Does the axis prevent the ticks from being rendered outside its bounds?
    # This flag is off by default because the standard axis *does* render ticks
    # that encroach on the plot area.
    ensure_ticks_bounded = false

    # Fired when the axis's range bounds change.
    updated = Event

    # Default traits UI view.
    traits_view = AxisView

    #------------------------------------------------------------------------
    # Override default values of inherited traits
    #------------------------------------------------------------------------

    # Background color (overrides AbstractOverlay). Axes usually let the color of
    # the container show through.
    bgcolor = transparent_color_trait

    # Dimensions that the axis is resizable in (overrides PlotComponent). 
    # Typically, axes are resizable in both dimensions.
    resizable = "hv"

    #------------------------------------------------------------------------
    # Private Traits
    #------------------------------------------------------------------------

    # Cached position calculations

    _tick_list = List  # These are caches of their respective positions
    _tick_positions = Any #List
    _tick_label_list = Any
    _tick_label_positions = Any
    _tick_label_bounding_boxes = List
    _major_axis_size = Float
    _minor_axis_size = Float
    _major_axis = Array
    _title_orientation = Array
    _title_angle = Float
    _origin_point = Array
    _inside_vector = Array
    _axis_vector = Array
    _axis_pixel_vector = Array
    _end_axis_point = Array


    ticklabel_cache = List
    _cache_valid = Bool(False)


    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, component=None, **kwargs):
        # Override init so that our component gets set last.  We want the
        # _component_changed() event handler to get run last.
        super(PlotAxis, self).__init__(**kwargs)
        if component is not None:
            self.component = component

    def invalidate(self):
        """ Invalidates the pre-computed layout and scaling data.
        """
        self._reset_cache()
        self.invalidate_draw()
        return

    #------------------------------------------------------------------------
    # PlotComponent and AbstractOverlay interface
    #------------------------------------------------------------------------

    def _do_layout(self, *args, **kw):
        """ Tells this component to do layout at a given size.
        
        Overrides PlotComponent.
        """
        if self.use_draw_order and self.component is not None:
            self._layout_as_overlay(*args, **kw)
        else:
            super(PlotAxis, self)._do_layout(*args, **kw)
        return

    def overlay(self, component, gc, view_bounds=None, mode='normal'):
        """ Draws this component overlaid on another component.
        
        Overrides AbstractOverlay.
        """
        if not self.visible:
            return
        self._draw_component(gc, view_bounds, mode, component)
        return

    def _draw_overlay(self, gc, view_bounds=None, mode='normal'):
        """ Draws the overlay layer of a component.
        
        Overrides PlotComponent.
        """
        self._draw_component(gc, view_bounds, mode)
        return

    def _draw_component(self, gc, view_bounds=None, mode='normal', component=None):
        """ Draws the component.

        This method is preserved for backwards compatibility. Overrides 
        PlotComponent.
        """
        if not self.visible:
            return

        if not self._cache_valid:
            if component is not None:
                self._calculate_geometry(component)
            else:
                self._old_calculate_geometry()
            self._compute_tick_positions(gc, component)
            self._compute_labels(gc)

        try:
            gc.save_state()

            # slight optimization: if we set the font correctly on the
            # base gc before handing it in to our title and tick labels,
            # their set_font() won't have to do any work.
            gc.set_font(self.tick_label_font)

            if self.axis_line_visible:
                self._draw_axis_line(gc, self._origin_point, self._end_axis_point)
            if self.title:
                self._draw_title(gc)

            self._draw_ticks(gc)
            self._draw_labels(gc)
        finally:
            gc.restore_state()

        self._cache_valid = True
        return


    #------------------------------------------------------------------------
    # Private draw routines
    #------------------------------------------------------------------------

    def _layout_as_overlay(self, size=None, force=False):
        """ Lays out the axis as an overlay on another component.
        """
        if self.component is not None:
            if self.orientation in ("left", "right"):
                self.y = self.component.y
                self.height = self.component.height
                if self.orientation == "left":
                    self.width = self.component.padding_left
                    self.x = self.component.outer_x
                elif self.orientation == "right":
                    self.width = self.component.padding_right
                    self.x = self.component.x2 + 1
            else:
                self.x = self.component.x
                self.width = self.component.width
                if self.orientation == "bottom":
                    self.height = self.component.padding_bottom
                    self.y = self.component.outer_y
                elif self.orientation == "top":
                    self.height = self.component.padding_top
                    self.y = self.component.y2 + 1
        return

    def _draw_axis_line(self, gc, startpoint, endpoint):
        """ Draws the line for the axis.
        """
        gc.save_state()
        try:
            gc.set_antialias(0)
            gc.set_line_width(self.axis_line_weight)
            gc.set_stroke_color(self.axis_line_color_)
            gc.set_line_dash(self.axis_line_style_)
            gc.move_to(*around(startpoint))
            gc.line_to(*around(endpoint))
            gc.stroke_path()
        finally:
            gc.restore_state()
        return

    def _draw_title_old(self, gc, label=None, v_offset=20):
        """ Draws the title for the axis.
        """
        #put in rotation code for right side

        if label is None:
            title_label = Label(text=self.title,
                                font=self.title_font,
                                color=self.title_color,
                                rotate_angle=self.title_angle)
        else:
            title_label = label
        tl_bounds = array(title_label.get_width_height(gc), float64)

        if self.title_angle == 0:
            text_center_to_corner = -tl_bounds/2.0
            v_offset = max([l._bounding_box[1] for l in self.ticklabel_cache]) * 1.3
        else:
            v_offset = max([l._bounding_box[0] for l in self.ticklabel_cache]) * 1.3
            corner_vec = transpose(-tl_bounds/2.0)
            rotmatrix = self._rotmatrix(-self.title_angle*pi/180.0)
            text_center_to_corner = transpose(dot(rotmatrix, corner_vec))[0]

        offset = (self._origin_point+self._end_axis_point)/2
        center_dist = self._center_dist(-self._inside_vector, tl_bounds[0], tl_bounds[1], rotation=self.title_angle)
        offset -= self._inside_vector * (center_dist + v_offset)
        offset += text_center_to_corner

        if self.title_angle == 90.0:
            # Horrible hack to adjust for the fact that the generic math above isn't
            # actually putting the label in the right place...
            offset[1] = offset[1] - tl_bounds[0]/2.0

        gc.translate_ctm(*offset)
        title_label.draw(gc)
        gc.translate_ctm(*(-offset))

        return


    def _draw_title(self, gc, label=None, v_offset=None):
        """ Draws the title for the axis.
        """
        #put in rotation code for right side

        if label is None:
            title_label = Label(text=self.title,
                                font=self.title_font,
                                color=self.title_color,
                                rotate_angle=self.title_angle)
        else:
            title_label = label
        tl_bounds = array(title_label.get_width_height(gc), float64)

        calculate_v_offset = v_offset is None
        
        if self.title_angle == 0:
            text_center_to_corner = -tl_bounds/2.0
            if calculate_v_offset:
                if not self.ticklabel_cache:
                    v_offset = 25
                else:
                    v_offset = max([l._bounding_box[1] for l in self.ticklabel_cache]) * 1.3
                           
            offset = (self._origin_point+self._end_axis_point)/2
            center_dist = self._center_dist(-self._inside_vector, tl_bounds[0], tl_bounds[1], rotation=self.title_angle)
            offset -= self._inside_vector * (center_dist + v_offset)
            offset += text_center_to_corner
        
        elif self.title_angle == 90:
            # Center the text vertically
            if calculate_v_offset:
                if not self.ticklabel_cache:
                    v_offset = 25
                else:
                    v_offset = (self._end_axis_point[1] - self._origin_point[1] - tl_bounds[0])/2.0
            h_offset = self.tick_out + tl_bounds[1] + 8
            if len(self.ticklabel_cache) > 0:
                h_offset += max([l._bounding_box[0] for l in self.ticklabel_cache]) 
            offset = array([self._origin_point[0] - h_offset, self._origin_point[1] + v_offset])

        else:
            if calculate_v_offset:
                if not self.ticklabel_cache:
                    v_offset = 25
                else:
                    v_offset = max([l._bounding_box[0] for l in self.ticklabel_cache]) * 1.3
            corner_vec = transpose(-tl_bounds/2.0)
            rotmatrix = self._rotmatrix(-self.title_angle*pi/180.0)
            text_center_to_corner = transpose(dot(rotmatrix, corner_vec))[0]
            offset = (self._origin_point+self._end_axis_point)/2
            center_dist = self._center_dist(-self._inside_vector, tl_bounds[0], tl_bounds[1], rotation=self.title_angle)
            offset -= self._inside_vector * (center_dist + v_offset)
            offset += text_center_to_corner

        gc.translate_ctm(*offset)
        title_label.draw(gc)
        gc.translate_ctm(*(-offset))

        return


    def _draw_ticks(self, gc):
        """ Draws the tick marks for the axis.
        """
        if not self.tick_visible:
            return
        gc.set_stroke_color(self.tick_color_)
        gc.set_line_width(self.tick_weight)
        gc.set_antialias(False)
        gc.begin_path()
        tick_in_vector = self._inside_vector*self.tick_in
        tick_out_vector = self._inside_vector*self.tick_out
        for tick_pos in self._tick_positions:
            gc.move_to(*(tick_pos + tick_in_vector))
            gc.line_to(*(tick_pos - tick_out_vector))
        gc.stroke_path()
        return

    def _draw_labels(self, gc):
        """ Draws the tick labels for the axis.
        """
        for i in range(len(self._tick_label_positions)):
            #We want a more sophisticated scheme than just 2 decimals all the time
            ticklabel = self.ticklabel_cache[i]
            tl_bounds = self._tick_label_bounding_boxes[i]

            #base_position puts the tick label at a point where the vector
            #extending from the tick mark inside 8 units
            #just touches the rectangular bounding box of the tick label.
            #Note: This is not necessarily optimal for non
            #horizontal/vertical axes.  More work could be done on this.

            base_position = (self._center_dist(-self._inside_vector, *tl_bounds)+8) \
                                * -self._inside_vector \
                                - tl_bounds/2.0 + self._tick_label_positions[i]

            if self.ensure_labels_bounded:
                pushdir = 0
                if i == 0:
                    pushdir = 1
                elif i == len(self._tick_label_positions)-1:
                    pushdir = -1
                push_pixel_vector = self._axis_pixel_vector * pushdir
                tlpos = around((self._center_dist(push_pixel_vector,*tl_bounds)+4) \
                                          * push_pixel_vector + base_position)

            else:
                tlpos = around(base_position)

            gc.translate_ctm(*tlpos)
            ticklabel.draw(gc)
            gc.translate_ctm(*(-tlpos))
        return


    #------------------------------------------------------------------------
    # Private methods for computing positions and layout
    #------------------------------------------------------------------------

    def _reset_cache(self):
        """ Clears the cached tick positions, labels, and label positions.
        """
        self._tick_positions = []
        self._tick_label_list = []
        self._tick_label_positions = []
        return

    def _compute_tick_positions(self, gc, overlay_component=None):
        """ Calculates the positions for the tick marks.
        """
        if (self.mapper is None):
            self._reset_cache()
            self._cache_valid = True
            return

        datalow = self.mapper.range.low
        datahigh = self.mapper.range.high
        screenhigh = self.mapper.high_pos
        screenlow = self.mapper.low_pos
        if overlay_component is not None:
            if self.orientation in ("top", "bottom"):
                direction = getattr(overlay_component, 'x_direction', None)
            elif self.orientation in ("left", "right"):
                direction = getattr(overlay_component, 'y_direction', None)

            if direction == "flipped":
                screenlow, screenhigh = screenhigh, screenlow


        if (datalow == datahigh) or (screenlow == screenhigh) or \
           (datalow in [inf, -inf]) or (datahigh in [inf, -inf]):
            self._reset_cache()
            self._cache_valid = True
            return

        if datalow > datahigh:
            raise RuntimeError, "DataRange low is greater than high; unable to compute axis ticks."

        if not self.tick_generator:
            return

        if isinstance(self.mapper, LogMapper):
            scale = 'log'
        else:
            scale = 'linear'

        tick_list = array(self.tick_generator.get_ticks(datalow, datahigh,
                                                        datalow, datahigh,
                                                        self.tick_interval,
                                                        use_endpoints=False,
                                                        scale=scale), float64)

        mapped_tick_positions = (array(self.mapper.map_screen(tick_list))-screenlow) / \
                                            (screenhigh-screenlow)
        self._tick_positions = around(array([self._axis_vector*tickpos + self._origin_point \
                                for tickpos in mapped_tick_positions]))

        if self.small_haxis_style:
            # If we're a small axis, we want the endpoints to be the labels regardless of
            # where the ticks are, as the labels represent the bounds, not where the tick
            # marks are.
            self._tick_label_list = array([datalow, datahigh])
            mapped_label_positions = (array(self.mapper.map_screen(self._tick_label_list))-screenlow) / \
                                     (screenhigh-screenlow)
            self._tick_label_positions = [self._axis_vector*tickpos + self._origin_point \
                                          for tickpos in mapped_label_positions]
        else:
            self._tick_label_list = tick_list
            self._tick_label_positions = self._tick_positions
        return


    def _compute_labels(self, gc):
        """Generates the labels for tick marks.  
        
        Waits for the cache to become invalid.
        """
        self.ticklabel_cache = []
        formatter = self.tick_label_formatter
        for i in range(len(self._tick_label_positions)):
            val = self._tick_label_list[i]
            if formatter is not None:
                tickstring = formatter(val)
            else:
                tickstring = ("%.2f"%val).rstrip("0").rstrip(".")
            ticklabel = Label(text=tickstring,
                              font=self.tick_label_font,
                              color=self.tick_label_color)
            self.ticklabel_cache.append(ticklabel)

        self._tick_label_bounding_boxes = [array(ticklabel.get_bounding_box(gc), float64) for ticklabel in self.ticklabel_cache]
        return


    def _calculate_geometry(self, overlay_component=None):
        if overlay_component is not None:
            if self.orientation == "top":
                new_origin = [overlay_component.x, overlay_component.y2]
                inside_vec = [0.0, -1.0]
            elif self.orientation == "bottom":
                new_origin = [overlay_component.x, overlay_component.y]
                inside_vec = [0.0, 1.0]
            elif self.orientation == "left":
                new_origin = [overlay_component.x, overlay_component.y]
                inside_vec = [1.0, 0.0]
            else:  # self.orientation == "right":
                new_origin = [overlay_component.x2, overlay_component.y]
                inside_vec = [-1.0, 0.0]
            self._origin_point = array(new_origin)
            self._inside_vector = array(inside_vec)
        else:
            overlay_component = self
            new_origin = array(self.position)

        direction = None
        if self.orientation in ('top', 'bottom'):
            self._major_axis_size = overlay_component.bounds[0]
            self._minor_axis_size = overlay_component.bounds[1]
            self._major_axis = array([1., 0.])
            self._title_orientation = array([0.,1.])
            if hasattr(overlay_component, "x_direction"):
                direction = overlay_component.x_direction
            #this could be calculated...
            self.title_angle = 0.0
        elif self.orientation in ('left', 'right'):
            self._major_axis_size = overlay_component.bounds[1]
            self._minor_axis_size = overlay_component.bounds[0]
            self._major_axis = array([0., 1.])
            self._title_orientation = array([-1., 0])
            if hasattr(overlay_component, "y_direction"):
                direction = overlay_component.y_direction
            self.title_angle = 90.0

        if self.ensure_ticks_bounded:
            self._origin_point -= self._inside_vector*self.tick_in

        screenhigh = self.mapper.high_pos
        screenlow = self.mapper.low_pos
        # TODO: should this be here, or not?
        if direction == "flipped":
            screenlow, screenhigh = screenhigh, screenlow
        self._end_axis_point = (screenhigh-screenlow)*self._major_axis + self._origin_point
        self._axis_vector = self._end_axis_point - self._origin_point
        # This is the vector that represents one unit of data space in terms of screen space.
        self._axis_pixel_vector = self._axis_vector/sqrt(dot(self._axis_vector,self._axis_vector))
        return


    def _old_calculate_geometry(self):
        if hasattr(self, 'mapper') and self.mapper is not None:
            screenhigh = self.mapper.high_pos
            screenlow = self.mapper.low_pos
        else:
            # fixme: this should take into account axis orientation
            screenhigh = self.x2
            screenlow = self.x

        if self.orientation in ('top', 'bottom'):
            self._major_axis_size = self.bounds[0]
            self._minor_axis_size = self.bounds[1]
            self._major_axis = array([1., 0.])
            self._title_orientation = array([0.,1.])
            #this could be calculated...
            self.title_angle = 0.0
            if self.orientation == 'top':
                self._origin_point = array(self.position) + self._major_axis * screenlow
                self._inside_vector = array([0.,-1.])
            else: #self.oriention == 'bottom'
                self._origin_point = array(self.position) + array([0., self.bounds[1]]) + self._major_axis*screenlow
                self._inside_vector = array([0., 1.])
        elif self.orientation in ('left', 'right'):
            self._major_axis_size = self.bounds[1]
            self._minor_axis_size = self.bounds[0]
            self._major_axis = array([0., 1.])
            self._title_orientation = array([-1., 0])
            self.title_angle = 90.0
            if self.orientation == 'left':
                self._origin_point = array(self.position) + array([self.bounds[0], 0.]) + self._major_axis*screenlow
                self._inside_vector = array([1., 0.])
            else: #self.orientation == 'right'
                self._origin_point = array(self.position) + self._major_axis*screenlow
                self._inside_vector = array([-1., 0.])

#        if self.mapper.high_pos<self.mapper.low_pos:
#            self._origin_point = self._origin_point + self._axis_

        if self.ensure_ticks_bounded:
            self._origin_point -= self._inside_vector*self.tick_in

        self._end_axis_point = (screenhigh-screenlow)*self._major_axis + self._origin_point
        self._axis_vector = self._end_axis_point - self._origin_point
        # This is the vector that represents one unit of data space in terms of screen space.
        self._axis_pixel_vector = self._axis_vector/sqrt(dot(self._axis_vector,self._axis_vector))
        return


    #------------------------------------------------------------------------
    # Private helper methods
    #------------------------------------------------------------------------

    def _rotmatrix(self, theta):
        """Returns a 2x2 rotation matrix for angle *theta*.
        """
        return array([[cos(theta), sin(theta)], [-sin(theta), cos(theta)]], float64)

    def _center_dist(self, vect, width, height, rotation=0.0):
        """Given a width and height of a rectangle, this method finds the
        distance in units of the vector, in the direction of the vector, from
        the center of the rectangle, to wherever the vector leaves the
        rectangle. This method is useful for determining where to place text so
        it doesn't run into other components. """
        rotvec = transpose(dot(self._rotmatrix(rotation*pi/180.0), transpose(array([vect], float64))))[0]
        absvec = absolute(rotvec)
        if absvec[1] != 0:
            heightdist = (float(height)/2)/float(absvec[1])
        else:
            heightdist = 9999999
        if absvec[0] != 0:
            widthdist = (float(width)/2)/float(absvec[0])
        else:
            widthdist = 99999999

        return min(heightdist, widthdist)


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _bounds_changed(self):
        self._invalidate()
        return

    def _bounds_items_changed(self):
        return self._bounds_changed()

    def _mapper_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self.mapper_updated, "updated", remove=True)
        if new is not None:
            new.on_trait_change(self.mapper_updated, "updated")
        self._invalidate()
        return

    def mapper_updated(self):
        """
        Event handler that is bound to this axis's mapper's **updated** event
        """
        self._invalidate()
        return

    def _position_changed(self):
        self._cache_valid = False
        return

    def _position_items_changed(self):
        return self._position_changed()
    
    def _position_changed_for_component(self):
        self._cache_valid = False

    def _position_items_changed_for_component(self):
        self._cache_valid = False

    def _bounds_changed_for_component(self):
        self._cache_valid = False

    def _bounds_items_changed_for_component(self):
        self._cache_valid = False
    
    def _updated_fired(self):
        """If the axis bounds changed, redraw."""
        self._cache_valid = False
        return

    def _invalidate(self):
        self._cache_valid = False
        self.invalidate_draw()
        if self.component:
            self.component.invalidate_draw()
#            self.component.request_redraw()
#        else:
#            self.request_redraw()
        return

    def _component_changed(self):
        if self.mapper is not None:
            # If there is a mapper set, just leave it be.
            return

        # Try to pick the most appropriate mapper for our orientation 
        # and what information we can glean from our component.
        attrmap = { "left": ("ymapper", "y_mapper", "value_mapper"),
                    "bottom": ("xmapper", "x_mapper", "index_mapper"), }
        attrmap["right"] = attrmap["left"]
        attrmap["top"] = attrmap["bottom"]

        component = self.component
        attr1, attr2, attr3 = attrmap[self.orientation]
        for attr in attrmap[self.orientation]:
            if hasattr(component, attr):
                self.mapper = getattr(component, attr)
                break
        return


    #------------------------------------------------------------------------
    # The following event handlers just invalidate our previously computed
    # Label instances and backbuffer if any of our visual attributes change.
    # TODO: refactor this stuff and the caching of contained objects (e.g. Label)
    #------------------------------------------------------------------------

    def _title_changed(self):
        self.invalidate_draw()
        if self.component:
            self.component.invalidate_draw()
#            self.component.request_redraw()
#        else:
#            self.request_redraw()

    def _title_color_changed(self):
        return self._invalidate()

    def _title_font_changed(self):
        return self._invalidate()

    def _tick_weight_changed(self):
        return self._invalidate()

    def _tick_color_changed(self):
        return self._invalidate()

    def _tick_font_changed(self):
        return self._invalidate()

    def _tick_label_font_changed(self):
        return self._invalidate()

    def _tick_label_color_changed(self):
        return self._invalidate()

    def _tick_in_changed(self):
        return self._invalidate()

    def _tick_out_changed(self):
        return self._invalidate()

    def _tick_visible_changed(self):
        return self._invalidate()

    def _tick_interval_changed(self):
        return self._invalidate()

    def _axis_line_color_changed(self):
        return self._invalidate()

    def _axis_line_weight_changed(self):
        return self._invalidate()

    def _axis_line_style_changed(self):
        return self._invalidate()

    def _orientation_changed(self):
        return self._invalidate()

    #------------------------------------------------------------------------
    # Persistence-related methods
    #------------------------------------------------------------------------

    def __getstate__(self):
        dont_pickle = [
            '_tick_list',
            '_tick_positions',
            '_tick_label_list',
            '_tick_label_positions',
            '_tick_label_bounding_boxes',
            '_major_axis_size',
            '_minor_axis_size',
            '_major_axis',
            '_title_orientation',
            '_title_angle',
            '_origin_point',
            '_inside_vector',
            '_axis_vector',
            '_axis_pixel_vector',
            '_end_axis_point',
            '_ticklabel_cache',
            '_cache_valid'
           ]

        state = super(PlotAxis,self).__getstate__()
        for key in dont_pickle:
            if state.has_key(key):
                del state[key]

        return state

    def __setstate__(self, state):
        super(PlotAxis,self).__setstate__(state)
        self._mapper_changed(None, self.mapper)
        self._reset_cache()
        self._cache_valid = False
        return


# EOF ########################################################################
