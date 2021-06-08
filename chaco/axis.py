# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the PlotAxis class, and associated validator and UI.
"""
# Major library import
from numpy import (
    array,
    around,
    absolute,
    cos,
    dot,
    float64,
    inf,
    pi,
    sqrt,
    sin,
    transpose,
)

# Enthought Library imports
from enable.api import ColorTrait, LineStyle
from kiva.trait_defs.kiva_font_trait import KivaFont
from traits.api import (
    Any,
    Float,
    Int,
    Str,
    Trait,
    Unicode,
    Bool,
    Event,
    List,
    Array,
    Instance,
    Enum,
    Callable,
    ArrayOrNone,
    observe
)

# Local relative imports
from .ticks import (
    AbstractTickGenerator,
    DefaultTickGenerator,
    MinorTickGenerator,
)
from .abstract_mapper import AbstractMapper
from .abstract_overlay import AbstractOverlay
from .label import Label
from .log_mapper import LogMapper


def DEFAULT_TICK_FORMATTER(val):
    return ("%f" % val).rstrip("0").rstrip(".")


class PlotAxis(AbstractOverlay):
    """
    The PlotAxis is a visual component that can be rendered on its own as
    a standalone component or attached as an overlay to another component.
    (To attach it as an overlay, set its **component** attribute.)

    When it is attached as an overlay, it draws into the padding around
    the component.
    """

    #: The mapper that drives this axis.
    mapper = Instance(AbstractMapper)

    #: Keep an origin for plots that aren't attached to a component
    origin = Enum("bottom left", "top left", "bottom right", "top right")

    #: The text of the axis title.
    title = Trait("", Str, Unicode)  # May want to add PlotLabel option

    #: The font of the title.
    title_font = KivaFont("modern 12")

    #: The spacing between the axis line and the title
    title_spacing = Trait("auto", "auto", Float)

    #: The color of the title.
    title_color = ColorTrait("black")

    #: The angle of the title, in degrees, from horizontal line
    title_angle = Float(0.0)

    #: The thickness (in pixels) of each tick.
    tick_weight = Float(1.0)

    #: The color of the ticks.
    tick_color = ColorTrait("black")

    #: The font of the tick labels.
    tick_label_font = KivaFont("modern 10")

    #: The color of the tick labels.
    tick_label_color = ColorTrait("black")

    #: The rotation of the tick labels.
    tick_label_rotate_angle = Float(0)

    #: Whether to align to corners or edges (corner is better for 45 degree rotation)
    tick_label_alignment = Enum("edge", "corner")

    #: The margin around the tick labels.
    tick_label_margin = Int(2)

    #: The distance of the tick label from the axis.
    tick_label_offset = Float(8.0)

    #: Whether the tick labels appear to the inside or the outside of the plot area
    tick_label_position = Enum("outside", "inside")

    #: A callable that is passed the numerical value of each tick label and
    #: that returns a string.
    tick_label_formatter = Callable(DEFAULT_TICK_FORMATTER)

    #: The number of pixels by which the ticks extend into the plot area.
    tick_in = Int(5)

    #: The number of pixels by which the ticks extend into the label area.
    tick_out = Int(5)

    #: Are ticks visible at all?
    tick_visible = Bool(True)

    #: The dataspace interval between ticks.
    tick_interval = Trait("auto", "auto", Float)

    #: A callable that implements the AbstractTickGenerator interface.
    tick_generator = Instance(AbstractTickGenerator)

    #: The location of the axis relative to the plot.  This determines where
    #: the axis title is located relative to the axis line.
    orientation = Enum("top", "bottom", "left", "right")

    #: Is the axis line visible?
    axis_line_visible = Bool(True)

    #: The color of the axis line.
    axis_line_color = ColorTrait("black")

    #: The line thickness (in pixels) of the axis line.
    axis_line_weight = Float(1.0)

    #: The dash style of the axis line.
    axis_line_style = LineStyle("solid")

    #: A special version of the axis line that is more useful for geophysical
    #: plots.
    small_haxis_style = Bool(False)

    #: Does the axis ensure that its end labels fall within its bounding area?
    ensure_labels_bounded = Bool(False)

    #: Does the axis prevent the ticks from being rendered outside its bounds?
    #: This flag is off by default because the standard axis *does* render ticks
    #: that encroach on the plot area.
    ensure_ticks_bounded = Bool(False)

    #: Fired when the axis's range bounds change.
    updated = Event

    # ------------------------------------------------------------------------
    # Override default values of inherited traits
    # ------------------------------------------------------------------------

    #: Background color (overrides AbstractOverlay). Axes usually let the color of
    #: the container show through.
    bgcolor = ColorTrait("transparent")

    #: Dimensions that the axis is resizable in (overrides PlotComponent).
    #: Typically, axes are resizable in both dimensions.
    resizable = "hv"

    # ------------------------------------------------------------------------
    # Private Traits
    # ------------------------------------------------------------------------

    # Cached position calculations

    _tick_list = List(transient=True)  # These are caches of their respective positions
    _tick_positions = ArrayOrNone(transient=True)
    _tick_label_list = ArrayOrNone(transient=True)
    _tick_label_positions = ArrayOrNone(transient=True)
    _tick_label_bounding_boxes = List(transient=True)
    _major_axis_size = Float(transient=True)
    _minor_axis_size = Float(transient=True)
    _major_axis = Array(transient=True)
    _title_orientation = Array(transient=True)
    _title_angle = Float(transient=True)
    _origin_point = Array(transient=True)
    _inside_vector = Array(transient=True)
    _axis_vector = Array(transient=True)
    _axis_pixel_vector = Array(transient=True)
    _end_axis_point = Array(transient=True)

    ticklabel_cache = List(transient=True)
    _cache_valid = Bool(False, transient=True)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def __init__(self, component=None, **kwargs):
        # TODO: change this back to a factory in the instance trait some day
        self.tick_generator = DefaultTickGenerator()
        # Override init so that our component gets set last.  We want the
        # _component_changed() event handler to get run last.
        super().__init__(**kwargs)
        if component is not None:
            self.component = component

    def invalidate(self):
        """Invalidates the pre-computed layout and scaling data."""
        self._reset_cache()
        self.invalidate_draw()

    def traits_view(self):
        """Returns a View instance for use with TraitsUI.  This method is
        called automatically be the Traits framework when .edit_traits() is
        invoked.
        """
        from .axis_view import AxisView

        return AxisView

    # ------------------------------------------------------------------------
    # PlotComponent and AbstractOverlay interface
    # ------------------------------------------------------------------------

    def _do_layout(self, *args, **kw):
        """Tells this component to do layout at a given size.

        Overrides Component.
        """
        if self.component is not None:
            self._layout_as_overlay(*args, **kw)
        else:
            super()._do_layout(*args, **kw)

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """Draws this component overlaid on another component.

        Overrides AbstractOverlay.
        """
        if not self.visible:
            return

        if not self._cache_valid:
            if component is not None:
                self._calculate_geometry_overlay(component)
            else:
                self._calculate_geometry()
            self._compute_tick_positions(gc, component)
            self._compute_labels(gc)

        with gc:
            # slight optimization: if we set the font correctly on the
            # base gc before handing it in to our title and tick labels,
            # their set_font() won't have to do any work.
            gc.set_font(self.tick_label_font)

            if self.axis_line_visible:
                self._draw_axis_line(
                    gc, self._origin_point, self._end_axis_point
                )
            if self.title:
                self._draw_title(gc)

            self._draw_ticks(gc)
            self._draw_labels(gc)

        self._cache_valid = True

    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        """Draws the overlay layer of a component.

        Overrides PlotComponent.
        """
        if not self.visible:
            return

        if not self._cache_valid:
            self._calculate_geometry()
            self._compute_tick_positions(gc, component)
            self._compute_labels(gc)

        with gc:
            # slight optimization: if we set the font correctly on the
            # base gc before handing it in to our title and tick labels,
            # their set_font() won't have to do any work.
            gc.set_font(self.tick_label_font)

            if self.axis_line_visible:
                self._draw_axis_line(
                    gc, self._origin_point, self._end_axis_point
                )
            if self.title:
                self._draw_title(gc)

            self._draw_ticks(gc)
            self._draw_labels(gc)

        self._cache_valid = True

    # ------------------------------------------------------------------------
    # Private draw routines
    # ------------------------------------------------------------------------

    def _layout_as_overlay(self, size=None, force=False):
        """Lays out the axis as an overlay on another component."""
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

    def _draw_axis_line(self, gc, startpoint, endpoint):
        """Draws the line for the axis."""
        with gc:
            gc.set_antialias(0)
            gc.set_line_width(self.axis_line_weight)
            gc.set_stroke_color(self.axis_line_color_)
            gc.set_line_dash(self.axis_line_style_)
            gc.move_to(*around(startpoint))
            gc.line_to(*around(endpoint))
            gc.stroke_path()

    def _draw_title(self, gc, label=None, axis_offset=None):
        """Draws the title for the axis."""
        if label is None:
            title_label = Label(
                text=self.title,
                font=self.title_font,
                color=self.title_color,
                rotate_angle=self.title_angle,
            )
        else:
            title_label = label

        # get the _rotated_ bounding box of the label
        tl_bounds = array(title_label.get_bounding_box(gc), float64)
        text_center_to_corner = -tl_bounds / 2.0
        # which axis are we moving away from the axis line along?
        axis_index = self._major_axis.argmin()

        if self.title_spacing != "auto":
            axis_offset = self.title_spacing

        if (self.title_spacing) and (axis_offset is None):
            if not self.ticklabel_cache:
                axis_offset = 25
            else:
                axis_offset = (
                    max(
                        [
                            l._bounding_box[axis_index]
                            for l in self.ticklabel_cache
                        ]
                    )
                    * 1.3
                )

        offset = (self._origin_point + self._end_axis_point) / 2
        axis_dist = self.tick_out + tl_bounds[axis_index] / 2.0 + axis_offset
        offset -= self._inside_vector * axis_dist
        offset += text_center_to_corner

        gc.translate_ctm(*offset)
        title_label.draw(gc)
        gc.translate_ctm(*(-offset))

    def _draw_ticks(self, gc):
        """Draws the tick marks for the axis."""
        if not self.tick_visible:
            return
        gc.set_stroke_color(self.tick_color_)
        gc.set_line_width(self.tick_weight)
        gc.set_antialias(False)
        gc.begin_path()
        tick_in_vector = self._inside_vector * self.tick_in
        tick_out_vector = self._inside_vector * self.tick_out
        for tick_pos in self._tick_positions:
            gc.move_to(*(tick_pos + tick_in_vector))
            gc.line_to(*(tick_pos - tick_out_vector))
        gc.stroke_path()

    def _draw_labels(self, gc):
        """Draws the tick labels for the axis."""
        # which axis are we moving away from the axis line along?
        axis_index = self._major_axis.argmin()

        inside_vector = self._inside_vector
        if self.tick_label_position == "inside":
            inside_vector = -inside_vector

        for i in range(len(self._tick_label_positions)):
            # We want a more sophisticated scheme than just 2 decimals all the time
            ticklabel = self.ticklabel_cache[i]
            tl_bounds = self._tick_label_bounding_boxes[i]

            # base_position puts the tick label at a point where the vector
            # extending from the tick mark inside 8 units
            # just touches the rectangular bounding box of the tick label.
            # Note: This is not necessarily optimal for non
            # horizontal/vertical axes.  More work could be done on this.

            base_position = self._tick_label_positions[i].copy()
            axis_dist = self.tick_label_offset + tl_bounds[axis_index] / 2.0
            base_position -= inside_vector * axis_dist
            base_position -= tl_bounds / 2.0

            if self.tick_label_alignment == "corner":
                if self.orientation in ("top", "bottom"):
                    base_position[0] += tl_bounds[0] / 2.0
                elif self.orientation == "left":
                    base_position[1] -= tl_bounds[1] / 2.0
                elif self.orientation == "right":
                    base_position[1] += tl_bounds[1] / 2.0

            if self.ensure_labels_bounded:
                bound_idx = self._major_axis.argmax()
                if i == 0:
                    base_position[bound_idx] = max(
                        base_position[bound_idx], self._origin_point[bound_idx]
                    )
                elif i == len(self._tick_label_positions) - 1:
                    base_position[bound_idx] = min(
                        base_position[bound_idx],
                        self._end_axis_point[bound_idx] - tl_bounds[bound_idx],
                    )

            tlpos = around(base_position)
            gc.translate_ctm(*tlpos)
            ticklabel.draw(gc)
            gc.translate_ctm(*(-tlpos))

    # ------------------------------------------------------------------------
    # Private methods for computing positions and layout
    # ------------------------------------------------------------------------

    def _reset_cache(self):
        """Clears the cached tick positions, labels, and label positions."""
        self._tick_positions = []
        self._tick_label_list = []
        self._tick_label_positions = []

    def _compute_tick_positions(self, gc, overlay_component=None):
        """Calculates the positions for the tick marks."""
        if self.mapper is None:
            self._reset_cache()
            self._cache_valid = True
            return

        datalow = self.mapper.range.low
        datahigh = self.mapper.range.high
        screenhigh = self.mapper.high_pos
        screenlow = self.mapper.low_pos
        if overlay_component is not None:
            origin = getattr(overlay_component, "origin", "bottom left")
        else:
            origin = self.origin
        if self.orientation in ("top", "bottom"):
            if "right" in origin:
                flip_from_gc = True
            else:
                flip_from_gc = False
        elif self.orientation in ("left", "right"):
            if "top" in origin:
                flip_from_gc = True
            else:
                flip_from_gc = False
        if flip_from_gc:
            screenlow, screenhigh = screenhigh, screenlow

        if (
            (datalow == datahigh)
            or (screenlow == screenhigh)
            or (datalow in [inf, -inf])
            or (datahigh in [inf, -inf])
        ):
            self._reset_cache()
            self._cache_valid = True
            return

        if datalow > datahigh:
            raise RuntimeError(
                "DataRange low is greater than high; unable to compute axis ticks."
            )

        if not self.tick_generator:
            return

        if hasattr(self.tick_generator, "get_ticks_and_labels"):
            # generate ticks and labels simultaneously
            tmp = self.tick_generator.get_ticks_and_labels(
                datalow, datahigh, screenlow, screenhigh
            )
            if len(tmp) == 0:
                tick_list = []
                labels = []
            else:
                tick_list, labels = tmp
            # compute the labels here
            self.ticklabel_cache = [
                Label(
                    text=lab,
                    font=self.tick_label_font,
                    color=self.tick_label_color,
                )
                for lab in labels
            ]
            self._tick_label_bounding_boxes = [
                array(ticklabel.get_bounding_box(gc), float64)
                for ticklabel in self.ticklabel_cache
            ]
        else:
            scale = "log" if isinstance(self.mapper, LogMapper) else "linear"
            if self.small_haxis_style:
                tick_list = array([datalow, datahigh])
            else:
                tick_list = array(
                    self.tick_generator.get_ticks(
                        datalow,
                        datahigh,
                        datalow,
                        datahigh,
                        self.tick_interval,
                        use_endpoints=False,
                        scale=scale,
                    ),
                    float64,
                )

        mapped_tick_positions = (
            array(self.mapper.map_screen(tick_list)) - screenlow
        ) / (screenhigh - screenlow)
        self._tick_positions = around(
            array(
                [
                    self._axis_vector * tickpos + self._origin_point
                    for tickpos in mapped_tick_positions
                ]
            )
        )
        self._tick_label_list = tick_list
        self._tick_label_positions = self._tick_positions

    def _compute_labels(self, gc):
        """Generates the labels for tick marks.

        Waits for the cache to become invalid.
        """
        # tick labels are already computed
        if hasattr(self.tick_generator, "get_ticks_and_labels"):
            return

        formatter = self.tick_label_formatter

        def build_label(val):
            tickstring = formatter(val) if formatter is not None else str(val)
            return Label(
                text=tickstring,
                font=self.tick_label_font,
                color=self.tick_label_color,
                rotate_angle=self.tick_label_rotate_angle,
                margin=self.tick_label_margin,
            )

        self.ticklabel_cache = [
            build_label(val) for val in self._tick_label_list
        ]
        self._tick_label_bounding_boxes = [
            array(ticklabel.get_bounding_box(gc), float)
            for ticklabel in self.ticklabel_cache
        ]

    def _calculate_geometry(self):
        origin = self.origin
        screenhigh = self.mapper.high_pos
        screenlow = self.mapper.low_pos

        if self.orientation in ("top", "bottom"):
            self._major_axis_size = self.bounds[0]
            self._minor_axis_size = self.bounds[1]
            self._major_axis = array([1.0, 0.0])
            self._title_orientation = array([0.0, 1.0])
            if self.orientation == "top":
                self._origin_point = array(self.position)
                self._inside_vector = array([0.0, -1.0])
            else:  # self.oriention == 'bottom'
                self._origin_point = array(self.position) + array(
                    [0.0, self.bounds[1]]
                )
                self._inside_vector = array([0.0, 1.0])
            if "right" in origin:
                screenlow, screenhigh = screenhigh, screenlow

        elif self.orientation in ("left", "right"):
            self._major_axis_size = self.bounds[1]
            self._minor_axis_size = self.bounds[0]
            self._major_axis = array([0.0, 1.0])
            self._title_orientation = array([-1.0, 0])
            if self.orientation == "left":
                self._origin_point = array(self.position) + array(
                    [self.bounds[0], 0.0]
                )
                self._inside_vector = array([1.0, 0.0])
            else:  # self.orientation == 'right'
                self._origin_point = array(self.position)
                self._inside_vector = array([-1.0, 0.0])
            if "top" in origin:
                screenlow, screenhigh = screenhigh, screenlow

        if self.ensure_ticks_bounded:
            self._origin_point -= self._inside_vector * self.tick_in

        self._end_axis_point = (
            abs(screenhigh - screenlow) * self._major_axis + self._origin_point
        )
        self._axis_vector = self._end_axis_point - self._origin_point
        # This is the vector that represents one unit of data space in terms of screen space.
        self._axis_pixel_vector = self._axis_vector / sqrt(
            dot(self._axis_vector, self._axis_vector)
        )

    def _calculate_geometry_overlay(self, overlay_component=None):
        if overlay_component is None:
            overlay_component = self
        component_origin = getattr(overlay_component, "origin", "bottom left")

        screenhigh = self.mapper.high_pos
        screenlow = self.mapper.low_pos

        if self.orientation in ("top", "bottom"):
            self._major_axis_size = overlay_component.bounds[0]
            self._minor_axis_size = overlay_component.bounds[1]
            self._major_axis = array([1.0, 0.0])
            self._title_orientation = array([0.0, 1.0])
            if self.orientation == "top":
                self._origin_point = array(
                    [overlay_component.x, overlay_component.y2]
                )
                self._inside_vector = array([0.0, -1.0])
            else:
                self._origin_point = array(
                    [overlay_component.x, overlay_component.y]
                )
                self._inside_vector = array([0.0, 1.0])
            if "right" in component_origin:
                screenlow, screenhigh = screenhigh, screenlow

        elif self.orientation in ("left", "right"):
            self._major_axis_size = overlay_component.bounds[1]
            self._minor_axis_size = overlay_component.bounds[0]
            self._major_axis = array([0.0, 1.0])
            self._title_orientation = array([-1.0, 0])
            if self.orientation == "left":
                self._origin_point = array(
                    [overlay_component.x, overlay_component.y]
                )
                self._inside_vector = array([1.0, 0.0])
            else:
                self._origin_point = array(
                    [overlay_component.x2, overlay_component.y]
                )
                self._inside_vector = array([-1.0, 0.0])
            if "top" in component_origin:
                screenlow, screenhigh = screenhigh, screenlow

        if self.ensure_ticks_bounded:
            self._origin_point -= self._inside_vector * self.tick_in

        self._end_axis_point = (
            abs(screenhigh - screenlow) * self._major_axis + self._origin_point
        )
        self._axis_vector = self._end_axis_point - self._origin_point
        # This is the vector that represents one unit of data space in terms of screen space.
        self._axis_pixel_vector = self._axis_vector / sqrt(
            dot(self._axis_vector, self._axis_vector)
        )

    # ------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------

    def _bounds_changed(self, old, new):
        super()._bounds_changed(old, new)
        self._layout_needed = True
        self._invalidate()

    def _bounds_items_changed(self, event):
        super()._bounds_items_changed(event)
        self._layout_needed = True
        self._invalidate()

    def _mapper_changed(self, old, new):
        if old is not None:
            old.observe(self.mapper_updated, "updated", remove=True)
        if new is not None:
            new.observe(self.mapper_updated, "updated")
        self._invalidate()

    def mapper_updated(self, event=None):
        """
        Event handler that is bound to this axis's mapper's **updated** event
        """
        self._invalidate()

    def _position_changed(self, old, new):
        super()._position_changed(old, new)
        self._cache_valid = False

    def _position_items_changed(self, event):
        super()._position_items_changed(event)
        self._cache_valid = False

    def _position_changed_for_component(self):
        self._cache_valid = False

    def _position_items_changed_for_component(self):
        self._cache_valid = False

    def _bounds_changed_for_component(self):
        self._cache_valid = False
        self._layout_needed = True

    def _bounds_items_changed_for_component(self):
        self._cache_valid = False
        self._layout_needed = True

    def _origin_changed_for_component(self):
        self._invalidate()

    def _updated_fired(self):
        """If the axis bounds changed, redraw."""
        self._cache_valid = False

    def _invalidate(self):
        self._cache_valid = False
        self.invalidate_draw()
        if self.component:
            self.component.invalidate_draw()

    def _component_changed(self):
        if self.mapper is not None:
            # If there is a mapper set, just leave it be.
            return

        # Try to pick the most appropriate mapper for our orientation
        # and what information we can glean from our component.
        attrmap = {
            "left": ("ymapper", "y_mapper", "value_mapper"),
            "bottom": ("xmapper", "x_mapper", "index_mapper"),
        }
        attrmap["right"] = attrmap["left"]
        attrmap["top"] = attrmap["bottom"]

        component = self.component
        attr1, attr2, attr3 = attrmap[self.orientation]
        for attr in attrmap[self.orientation]:
            if hasattr(component, attr):
                self.mapper = getattr(component, attr)
                break

        # Keep our origin in sync with the component
        self.origin = getattr(component, "origin", "bottom left")

    # ------------------------------------------------------------------------
    # The following event handlers just invalidate our previously computed
    # Label instances and backbuffer if any of our visual attributes change.
    # TODO: refactor this stuff and the caching of contained objects (e.g. Label)
    # ------------------------------------------------------------------------

    def _title_changed(self):
        self.invalidate_draw()
        if self.component:
            self.component.invalidate_draw()

    @observe([
        "title_font",
        "title_spacing",
        "title_color",
        "title_angle",
        "tick_weight",
        "tick_color",
        "tick_label_font",
        "tick_label_color",
        "tick_label_rotate_angle",
        "tick_label_alignment",
        "tick_label_margin",
        "tick_label_offset",
        "tick_label_position",
        "tick_label_formatter",
        "tick_in",
        "tick_out",
        "tick_visible",
        "tick_interval",
        "tick_generator",
        "orientation",
        "origin",
        "axis_line_visible",
        "axis_line_color",
        "axis_line_weight",
        "axis_line_style",
        "small_haxis_style",
        "ensure_labels_bounded",
        "ensure_ticks_bounded",
    ])
    def _invalidate_on_changed_visual_attr(self, event):
        self._invalidate()

    # ------------------------------------------------------------------------
    # Initialization-related methods
    # ------------------------------------------------------------------------

    def _title_angle_default(self):
        if self.orientation == "left":
            return 90.0
        if self.orientation == "right":
            return 270.0
        # Then self.orientation in {'top', 'bottom'}
        return 0.0

    # ------------------------------------------------------------------------
    # Persistence-related methods
    # ------------------------------------------------------------------------

    def __setstate__(self, state):
        super().__setstate__(state)
        self._mapper_changed(None, self.mapper)
        self._reset_cache()
        self._cache_valid = False


class MinorPlotAxis(PlotAxis):
    """
    The MinorPlotAxis is a PlotAxis which draws ticks with a smaller interval,
    smaller tick sizes, and no tick labels.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "tick_generator" not in kwargs:
            self.tick_generator = MinorTickGenerator()
        if "tick_label_formatter" not in kwargs:
            self.tick_label_formatter = lambda x: ""
        if "tick_in" not in kwargs:
            self.tick_in = 2
        if "tick_out" not in kwargs:
            self.tick_out = 2
        if "axis_line_visible" not in kwargs:
            self.axis_line_visible = False
