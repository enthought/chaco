# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the PlotGrid class, and associated TraitsUI View and validator
function.
"""


from numpy import (
    around,
    array,
    asarray,
    column_stack,
    float64,
    inf,
    zeros,
    zeros_like,
)

# Enthought library imports
from enable.api import black_color_trait, LineStyle
from traits.api import (
    Any,
    Bool,
    Callable,
    Enum,
    Float,
    Instance,
    CInt,
    Trait,
    Property,
    TraitError,
    Tuple,
    observe,
)
from traitsui.api import HGroup, Item, VGroup, View, TextEditor

# Local, relative imports
from .abstract_overlay import AbstractOverlay
from .abstract_mapper import AbstractMapper
from .log_mapper import LogMapper
from .ticks import AbstractTickGenerator, DefaultTickGenerator


def float_or_auto(val):
    """
    Validator function that returns *val* if *val* is either a number or
    the word 'auto'.  This is used as a validator for the text editor
    in the traits UI for the tick_interval trait.
    """
    try:
        return float(val)
    except:
        if isinstance(val, str) and val == "auto":
            return val
    raise TraitError("Tick interval must be a number or 'auto'.")


# View for setting grid properties.
GridView = View(
    VGroup(
        HGroup(
            Item(
                "grid_interval",
                label="Interval",
                editor=TextEditor(evaluate=float_or_auto),
            ),
            Item("visible", label="Visible"),
        ),
        Item("line_color", label="Color", style="custom"),
        Item("line_style", label="Dash style"),
        Item("line_width", label="Thickness"),
    ),
    buttons=["OK", "Cancel"],
)


def Alias(name):
    return Property(
        lambda obj: getattr(obj, name),
        lambda obj, val: setattr(obj, name, val),
    )


class PlotGrid(AbstractOverlay):
    """An overlay that represents a grid.

    A grid is a set of parallel lines, horizontal or vertical. You can use
    multiple grids with different settings for the horizontal and vertical
    lines in a plot.
    """

    # ------------------------------------------------------------------------
    # Data-related traits
    # ------------------------------------------------------------------------

    #: The mapper (and associated range) that drive this PlotGrid.
    mapper = Instance(AbstractMapper)

    #: The dataspace interval between grid lines.
    grid_interval = Trait("auto", "auto", Float)

    #: The dataspace value at which to start this grid.  If None, then
    #: uses the mapper.range.low.
    data_min = Trait(None, None, Float)

    #: The dataspace value at which to end this grid.  If None, then uses
    #: the mapper.range.high.
    data_max = Trait(None, None, Float)

    #: A callable that implements the AbstractTickGenerator Interface.
    tick_generator = Instance(AbstractTickGenerator)

    # ------------------------------------------------------------------------
    # Layout traits
    # ------------------------------------------------------------------------

    #: The orientation of the grid lines.  "horizontal" means that the grid
    #: lines are parallel to the X axis and the ticker and grid interval
    #: refer to the Y axis.
    orientation = Enum("horizontal", "vertical")

    #: Draw the ticks starting at the end of the mapper range? If False, the
    #: ticks are drawn starting at 0. This setting can be useful to keep the
    #: grid from from "flashing" as the user resizes the plot area.
    flip_axis = Bool(False)

    #: Optional specification of the grid bounds in the dimension transverse
    #: to the ticking/gridding dimension, i.e. along the direction specified
    #: by self.orientation.  If this is specified but transverse_mapper is
    #: not specified, then there is no effect.
    #:
    #:   None : use self.bounds or self.component.bounds (if overlay)
    #:   Tuple : (low, high) extents, used for every grid line
    #:   Callable : Function that takes an array of dataspace grid ticks
    #:              and returns either an array of shape (N,2) of (starts,ends)
    #:              for each grid point or a single tuple (low, high)
    transverse_bounds = Trait(None, Tuple, Callable)

    #: Mapper in the direction corresponding to self.orientation, i.e. transverse
    #: to the direction of self.mapper.  This is used to compute the screen
    #: position of transverse_bounds.  If this is not specified, then
    #: transverse_bounds has no effect, and vice versa.
    transverse_mapper = Instance(AbstractMapper)

    #: Dimensions that the grid is resizable in (overrides PlotComponent).
    resizable = "hv"

    # ------------------------------------------------------------------------
    # Appearance traits
    # ------------------------------------------------------------------------

    #: The color of the grid lines.
    line_color = black_color_trait

    #: The style (i.e., dash pattern) of the grid lines.
    line_style = LineStyle("solid")

    #: The thickness, in pixels, of the grid lines.
    line_width = CInt(1)
    line_weight = Alias("line_width")

    #: Default TraitsUI View for modifying grid attributes.
    traits_view = GridView

    # ------------------------------------------------------------------------
    # Private traits; mostly cached information
    # ------------------------------------------------------------------------

    _cache_valid = Bool(False, transient=True)
    _tick_list = Any(transient=True)
    _tick_positions = Any(transient=True)

    # An array (N,2) of start,end positions in the transverse direction
    # i.e. the direction corresponding to self.orientation
    _tick_extents = Any(transient=True)

    # _length = Float(0.0)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def __init__(self, **traits):
        # TODO: change this back to a factory in the instance trait some day
        self.tick_generator = DefaultTickGenerator()
        super().__init__(**traits)
        self.bgcolor = "none"  # make sure we're transparent

    @observe("bounds.items,position.items")
    def invalidate(self, event=None):
        """Invalidate cached information about the grid."""
        self._reset_cache()

    # ------------------------------------------------------------------------
    # PlotComponent and AbstractOverlay interface
    # ------------------------------------------------------------------------

    def do_layout(self, *args, **kw):
        """Tells this component to do layout at a given size.

        Overrides PlotComponent.
        """
        if self.component is not None:
            self._layout_as_overlay(*args, **kw)
        else:
            super().do_layout(*args, **kw)

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _do_layout(self):
        """Performs a layout.

        Overrides PlotComponent.
        """

    def _layout_as_overlay(self, size=None, force=False):
        """Lays out the axis as an overlay on another component."""
        if self.component is not None:
            self.position = self.component.position
            self.bounds = self.component.bounds

    def _reset_cache(self):
        """Clears the cached tick positions."""
        self._tick_positions = array([], dtype=float)
        self._tick_extents = array([], dtype=float)
        self._cache_valid = False

    def _compute_ticks(self, component=None):
        """Calculates the positions for the grid lines."""
        if self.mapper is None:
            self._reset_cache()
            self._cache_valid = True
            return

        if self.data_min is None:
            datalow = self.mapper.range.low
        else:
            datalow = self.data_min
        if self.data_max is None:
            datahigh = self.mapper.range.high
        else:
            datahigh = self.data_max

        # Map the low and high data points
        screenhigh = self.mapper.map_screen(datalow)
        screenlow = self.mapper.map_screen(datahigh)

        if (
            (datalow == datahigh)
            or (screenlow == screenhigh)
            or (datalow in [inf, -inf])
            or (datahigh in [inf, -inf])
        ):
            self._reset_cache()
            self._cache_valid = True
            return

        if component is None:
            component = self.component

        if component is not None:
            bounds = component.bounds
            position = component.position
        else:
            bounds = self.bounds
            position = self.position

        if isinstance(self.mapper, LogMapper):
            scale = "log"
        else:
            scale = "linear"

        ticks = self.tick_generator.get_ticks(
            datalow,
            datahigh,
            datalow,
            datahigh,
            self.grid_interval,
            use_endpoints=False,
            scale=scale,
        )
        tick_positions = self.mapper.map_screen(array(ticks, float64))

        if self.orientation == "horizontal":
            self._tick_positions = around(
                column_stack(
                    (zeros_like(tick_positions) + position[0], tick_positions)
                )
            )
        elif self.orientation == "vertical":
            self._tick_positions = around(
                column_stack(
                    (tick_positions, zeros_like(tick_positions) + position[1])
                )
            )
        else:
            raise self.NotImplementedError

        # Compute the transverse direction extents
        self._tick_extents = zeros((len(ticks), 2), dtype=float)
        if self.transverse_bounds is None or self.transverse_mapper is None:
            # No mapping needed, just use the extents
            if self.orientation == "horizontal":
                extents = (position[0], position[0] + bounds[0])
            elif self.orientation == "vertical":
                extents = (position[1], position[1] + bounds[1])
            self._tick_extents[:] = extents
        elif callable(self.transverse_bounds):
            data_extents = self.transverse_bounds(ticks)
            tmapper = self.transverse_mapper
            if isinstance(data_extents, tuple):
                self._tick_extents[:] = tmapper.map_screen(
                    asarray(data_extents)
                )
            else:
                extents = array(
                    [
                        tmapper.map_screen(data_extents[:, 0]),
                        tmapper.map_screen(data_extents[:, 1]),
                    ]
                ).T
                self._tick_extents = extents
        else:
            # Already a tuple
            self._tick_extents[:] = self.transverse_mapper.map_screen(
                asarray(self.transverse_bounds)
            )

        self._cache_valid = True

    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        """Draws the overlay layer of a component.

        Overrides PlotComponent.
        """
        # What we're really trying to do with a grid is plot contour lines in
        # the space of the plot.  In a rectangular plot, these will always be
        # straight lines.
        if not self.visible:
            return

        if not self._cache_valid:
            self._compute_ticks()

        if len(self._tick_positions) == 0:
            return

        with gc:
            gc.set_line_width(self.line_weight)
            gc.set_line_dash(self.line_style_)
            gc.set_stroke_color(self.line_color_)
            gc.set_antialias(False)

            if self.component is not None:
                gc.clip_to_rect(
                    *(self.component.position + self.component.bounds)
                )
            else:
                gc.clip_to_rect(*(self.position + self.bounds))

            gc.begin_path()
            if self.orientation == "horizontal":
                starts = self._tick_positions.copy()
                starts[:, 0] = self._tick_extents[:, 0]
                ends = self._tick_positions.copy()
                ends[:, 0] = self._tick_extents[:, 1]
            else:
                starts = self._tick_positions.copy()
                starts[:, 1] = self._tick_extents[:, 0]
                ends = self._tick_positions.copy()
                ends[:, 1] = self._tick_extents[:, 1]
            if self.flip_axis:
                starts, ends = ends, starts
            gc.line_set(starts, ends)
            gc.stroke_path()

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        """Draws this component overlaid on another component.

        Overrides AbstractOverlay.
        """
        # What we're really trying to do with a grid is plot contour lines in
        # the space of the plot.  In a rectangular plot, these will always be
        # straight lines.
        if not self.visible:
            return
        self._compute_ticks(other_component)
        
        if not self._cache_valid:
            self._compute_ticks()

        if len(self._tick_positions) == 0:
            return

        with gc:
            gc.set_line_width(self.line_weight)
            gc.set_line_dash(self.line_style_)
            gc.set_stroke_color(self.line_color_)
            gc.set_antialias(False)

            if self.component is not None:
                gc.clip_to_rect(
                    *(self.component.position + self.component.bounds)
                )
            else:
                gc.clip_to_rect(*(self.position + self.bounds))

            gc.begin_path()
            if self.orientation == "horizontal":
                starts = self._tick_positions.copy()
                starts[:, 0] = self._tick_extents[:, 0]
                ends = self._tick_positions.copy()
                ends[:, 0] = self._tick_extents[:, 1]
            else:
                starts = self._tick_positions.copy()
                starts[:, 1] = self._tick_extents[:, 0]
                ends = self._tick_positions.copy()
                ends[:, 1] = self._tick_extents[:, 1]
            if self.flip_axis:
                starts, ends = ends, starts
            gc.line_set(starts, ends)
            gc.stroke_path()

        self._cache_valid = False

    def _mapper_changed(self, old, new):
        if old is not None:
            old.observe(self.mapper_updated, "updated", remove=True)
        if new is not None:
            new.observe(self.mapper_updated, "updated")
        self.invalidate()

    def mapper_updated(self, event=None):
        """
        Event handler that is bound to this mapper's **updated** event.
        """
        self.invalidate()

    def _position_changed_for_component(self):
        self.invalidate()

    def _position_items_changed_for_component(self):
        self.invalidate()

    def _bounds_changed_for_component(self):
        self.invalidate()

    def _bounds_items_changed_for_component(self):
        self.invalidate()

    # ------------------------------------------------------------------------
    # Event handlers for visual attributes.  These mostly just call request_redraw()
    # ------------------------------------------------------------------------

    @observe("visible,line_color,line_style,line_weight")
    def visual_attr_changed(self, event=None):
        """Called when an attribute that affects the appearance of the grid
        is changed.
        """
        if self.component:
            self.component.invalidate_draw()
            self.component.request_redraw()
        else:
            self.invalidate_draw()
            self.request_redraw()

    def _grid_interval_changed(self):
        self.invalidate()
        self.visual_attr_changed()

    def _orientation_changed(self):
        self.invalidate()
        self.visual_attr_changed()

    ### Persistence ###########################################################

    def _post_load(self):
        super()._post_load()
        self._mapper_changed(None, self.mapper)
        self._reset_cache()
        self._cache_valid = False
