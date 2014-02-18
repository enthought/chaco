""" Defines the RectangleSelectionTool class.
"""
# Major library imports
import numpy

# Enthought library imports
from traits.api import Bool, Enum, Trait, Int, Float, Tuple, Array
from enable.api import BaseTool, ColorTrait, KeySpec
from chaco.abstract_overlay import AbstractOverlay


class RectangleSelectionTool(AbstractOverlay, BaseTool):
    """ Selection tool which allows the user to draw a box which defines a
    selected region and draw an overlay for the selected region.
    """

    #: Is the tool always "on"? If True, left-clicking always initiates a
    #: selection operation; if False, the user must press a key to enter
    #: selection mode.
    always_on = Bool(False)

    #: Defines a meta-key, that works with always_on to set the selection mode.
    #: This is useful when the selection tool is used in conjunction with the
    #: pan tool.
    always_on_modifier = Enum('control', 'shift', 'control', 'alt')

    #: The minimum amount of screen space the user must select in order for
    #: the tool to actually take effect.
    minimum_screen_delta = Int(10)

    #: Bounding box of selected region: (xmin, xmax, ymin, ymax)
    #TODO: Rename to `selection`?
    selected_box = Tuple()

    #: Key press to clear selected box
    clear_selected_key = KeySpec('Esc')

    #-------------------------------------------------------------------------
    # Appearance properties (for Box mode)
    #-------------------------------------------------------------------------

    #: The pointer to use when drawing a selection box.
    pointer = "magnifier"

    #: The color of the selection box.
    color = ColorTrait("lightskyblue")

    #: The alpha value to apply to **color** when filling in the selection
    #: region.  Because it is almost certainly useless to have an opaque
    #: selection rectangle, but it's also extremely useful to be able to use
    #: the normal named colors from Enable, this attribute allows the
    #: specification of a separate alpha value that replaces the alpha value
    #: of **color** at draw time.
    alpha = Trait(0.4, None, Float)

    #: The color of the outside selection rectangle.
    border_color = ColorTrait("dodgerblue")

    #: The thickness of selection rectangle border.
    border_size = Int(1)

    #: The possible event states of this selection tool.
    event_state = Enum("normal", "selecting", "moving")

    #: The (x,y) screen point where the mouse went down.
    _screen_start = Trait(None, None, Tuple)

    #: The (x,,y) screen point of the last seen mouse move event.
    _screen_end = Trait(None, None, Tuple)

    #: If **always_on** is False, this attribute indicates whether the tool
    #: is currently enabled.
    _enabled = Bool(False)

    #------------------------------------------------------------------------
    # Moving (not resizing) state
    #------------------------------------------------------------------------

    #: The position of the initial user click for moving the selection.
    _move_start = Array  # (x,y)

    #: Move distance during moving state.
    _move_offset = Array(value=(0, 0))  # (x,y)

    def __init__(self, component=None, *args, **kw):
        # Since this class uses multiple inheritance (eek!), lets be
        # explicit about the order of the parent class constructors
        AbstractOverlay.__init__(self, component, *args, **kw)
        BaseTool.__init__(self, component, *args, **kw)

    def reset(self, event=None):
        """ Resets the tool to normal state.
        """
        self.event_state = "normal"

    def clear_selected_box(self):
        self._screen_start = self._screen_end = None
        self.selected_box = ()

    #--------------------------------------------------------------------------
    #  BaseTool interface
    #--------------------------------------------------------------------------

    def normal_key_pressed(self, event):
        """ Handles a key being pressed when the tool is in the 'normal'
        state.
        """
        if self.clear_selected_key.match(event) and not self._enabled:
            self.clear_selected_box()
            self.request_redraw()
            event.handled = True

    def normal_mouse_move(self, event):
        self.position = (event.x, event.y)
        event.handled = True

    def normal_mouse_enter(self, event):
        """ Try to set the focus to the window when the mouse enters, otherwise
            the keypress events will not be triggered.
        """
        if self.component._window is not None:
            self.component._window._set_focus()

    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed while the tool is in
        the 'normal' state.

        If the tool is enabled or always on, it starts selecting.
        """
        if self.component.active_tool in (None, self):
            self.component.active_tool = self
        else:
            self._enabled = False

        if self._within_selected_box(event):
            self._start_move(event)
        else:
            self._start_select(event)

        event.handled = True

    def selecting_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'selecting' state.

        The selection is extended to the current mouse position.
        """
        self._screen_end = (event.x, event.y)
        self.component.request_redraw()
        event.handled = True

    def selecting_left_up(self, event):
        """ Handles the left mouse button being released when the tool is in
        the 'selecting' state.

        Finishes selecting and does the selection.
        """
        self._end_select(event)

    def moving_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'moving' state.

        Moves the overlay by an amount corresponding to the amount that the
        mouse has moved since its button was pressed. If the new selection
        range overlaps the endpoints of the data, it is truncated to that
        endpoint.
        """
        self._move_offset = (event.x, event.y) - self._move_start
        self.component.request_redraw()
        event.handled = True

    def moving_left_up(self, event):
        """ Handles the left mouse button coming up when the tool is in the
        'moving' state.

        Switches the tool to the 'selected' state.
        """
        #TODO: Why are _screen_start and _screen_end tuples not arrays?
        self._screen_start = tuple(self._screen_start + self._move_offset)
        self._screen_end = tuple(self._screen_end + self._move_offset)

        self._update_selected_box()
        # Clear move
        self._move_offset = (0, 0)

        self.event_state = "normal"
        event.handled = True

    #--------------------------------------------------------------------------
    #  AbstractOverlay interface
    #--------------------------------------------------------------------------

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.

        Overrides AbstractOverlay.
        """
        self._overlay_box(component, gc)

    #--------------------------------------------------------------------------
    #  private interface
    #--------------------------------------------------------------------------

    def _start_select(self, event):
        """ Starts selecting the selection region
        """
        self.event_state = "selecting"
        self._screen_start = (event.x, event.y)
        self._screen_end = None
        event.window.set_pointer(self.pointer)
        event.window.set_mouse_owner(self, event.net_transform())
        self.selecting_mouse_move(event)

    def _end_select(self, event):
        """ Ends selection of the selection region, adds the new selection
        range to the selection stack, and does the selection.
        """
        self._screen_end = (event.x, event.y)
        self._update_selected_box()
        self._end_selecting(event)
        event.handled = True

    def _end_selecting(self, event=None):
        """ Ends selection of selection region, without selectioning.
        """
        self.reset()
        self._enabled = False
        if self.component.active_tool == self:
            self.component.active_tool = None
        if event and event.window:
            event.window.set_pointer("arrow")

        self.component.request_redraw()
        if event and event.window.mouse_owner == self:
            event.window.set_mouse_owner(None)

    def _update_selected_box(self):
        start = numpy.array(self._screen_start)
        end = numpy.array(self._screen_end)

        # If selection is below minimum, clear selected box.
        if sum(abs(end - start)) < self.minimum_screen_delta:
            self.clear_selected_box()
        else:
            # Selected box in screen coordinates
            self._selected_box_screen = (sorted([start[0], end[0]]) +
                                         sorted([start[1], end[1]]))
            # Selected box in data coordinates
            low, high = self._map_coordinate_box(self._screen_start,
                                                 self._screen_end)
            self.selected_box = (low[0], high[0], low[1], high[1])

    def _start_move(self, event):
        self.event_state = "moving"
        self._move_start = (event.x, event.y)
        self.moving_mouse_move(event)

    def _overlay_box(self, component, gc):
        """ Draws the overlay as a box.
        """
        if self._screen_start and self._screen_end:
            with gc:
                gc.set_antialias(0)
                gc.set_line_width(self.border_size)
                gc.set_stroke_color(self.border_color_)
                gc.clip_to_rect(component.x, component.y,
                                component.width, component.height)
                x, y = self._screen_start + self._move_offset
                x2, y2 = self._screen_end + self._move_offset
                rect = (x, y, x2 - x + 1, y2 - y + 1)
                if self.color != "transparent":
                    if self.alpha:
                        color = list(self.color_)
                        if len(color) == 4:
                            color[3] = self.alpha
                        else:
                            color += [self.alpha]
                    else:
                        color = self.color_
                    gc.set_fill_color(color)
                    gc.draw_rect(rect)
                else:
                    gc.rect(*rect)
                    gc.stroke_path()

    def _map_coordinate_box(self, start, end):
        """ Given start and end points in screen space, returns corresponding
        low and high points in data space.
        """
        low = [0, 0]
        high = [0, 0]
        for axis_index, mapper in [(0, self.component.x_mapper),
                                   (1, self.component.y_mapper)]:
            # Ignore missing axis mappers (ColorBar instances only have one).
            if not mapper:
                continue
            low_val, high_val = sorted(mapper.map_data(point[axis_index])
                                       for point in (start, end))
            low[axis_index] = low_val
            high[axis_index] = high_val
        return low, high

    def _within_selected_box(self, event):
        if not self.selected_box:
            return False

        xmin, xmax, ymin, ymax = self._selected_box_screen
        if xmin < event.x < xmax and ymin < event.y < ymax:
            return True
        else:
            return False
