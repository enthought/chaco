""" Defines the PanTool class.
"""

from numpy import inf

# Enthought library imports
from enable.api import BaseTool, Pointer, KeySpec
from traits.api import Bool, Enum, Float, Tuple, Instance


class PanTool(BaseTool):
    """ A tool that enables the user to pan a plot by clicking a mouse
    button and dragging.
    """

    # The mouse button that initiates the drag operation.
    drag_button = Enum("left", "middle", "right")

    # The cursor to use when panning.
    drag_pointer = Pointer("hand")

    # Scaling factor on the panning "speed".
    speed = Float(1.0)

    # The modifier key that, if depressed when the drag is initiated, constrains
    # the panning to happen in the only direction of largest initial motion.
    # It is possible to permanently restrict this tool to always drag along one
    # direction.  To do so, set constrain=True, constrain_key=None, and
    # constrain_direction to the desired direction.
    constrain_key = Enum(None, "shift", "control", "alt")

    # Keys to Pan via keyboard
    pan_right_key = Instance(KeySpec, args=("Right",))
    pan_left_key = Instance(KeySpec, args=("Left",))
    pan_up_key = Instance(KeySpec, args=("Up",))
    pan_down_key = Instance(KeySpec, args=("Down",))

    # number of pixels the keys should pan
    # disabled if 0.0
    pan_keys_step = Float(0.0)

    # Constrain the panning to one direction?
    constrain = Bool(False)

    # The direction of constrained draw. A value of None means that the user
    # has initiated the drag and pressed the constrain_key, but hasn't moved
    # the mouse yet; the magnitude of the components of the next mouse_move
    # event will determine the constrain_direction.
    constrain_direction = Enum(None, "x", "y")

    # Restrict to the bounds of the plot data
    restrict_to_data = Bool(False)

    # (x,y) of the point where the mouse button was pressed.
    _original_xy = Tuple

    # Data coordinates of **_original_xy**.  This may be either (index,value)
    # or (value,index) depending on the component's orientation.
    _original_data = Tuple

    # Was constrain=True triggered by the **contrain_key**? If False, it was
    # set programmatically.
    _auto_constrain = Bool(False)


    #------------------------------------------------------------------------
    # Inherited BaseTool traits
    #------------------------------------------------------------------------

    # The tool does not have a visual representation (overrides
    # BaseTool).
    draw_mode = "none"

    # The tool is not visible (overrides BaseTool).
    visible = False

    # The possible event states of this tool (overrides enable.Interactor).
    event_state = Enum("normal", "panning")

    def normal_key_pressed(self, event):
        """ Handles a key being pressed when the tool is in the 'normal'
        state.
        """
        if self.pan_keys_step == 0.0:
            return
        src = self.component.bounds[0]/2, self.component.bounds[1]/2
        dest = src
        if self.pan_left_key.match(event):
            dest = (src[0] - self.pan_keys_step,
                    src[1])
        elif self.pan_right_key.match(event):
            dest = (src[0] + self.pan_keys_step,
                    src[1])
        elif self.pan_down_key.match(event):
            dest = (src[0],
                    src[1] - self.pan_keys_step)
        elif self.pan_up_key.match(event):
            dest = (src[0],
                    src[1] + self.pan_keys_step)
        if src != dest:
            self._original_xy = src
            event.x = dest[0]
            event.y = dest[1]
            self.panning_mouse_move(event)
        return

    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed when the tool is in
        the 'normal' state.

        Starts panning if the left mouse button is the drag button.
        """
        if self.drag_button == "left":
            self._start_pan(event)
        return

    def normal_right_down(self, event):
        """ Handles the right mouse button being pressed when the tool is in
        the 'normal' state.

        Starts panning if the right mouse button is the drag button.
        """
        if self.drag_button == "right":
            self._start_pan(event)
        return

    def normal_middle_down(self, event):
        """ Handles the middle mouse button being pressed when the tool is in
        the 'normal' state.

        Starts panning if the middle mouse button is the drag button.
        """
        if self.drag_button == "middle":
            self._start_pan(event)
        return

    def panning_left_up(self, event):
        """ Handles the left mouse button coming up when the tool is in the
        'panning' state.

        Stops panning if the left mouse button is the drag button.
        """
        if self.drag_button == "left":
            self._end_pan(event)
        return

    def panning_right_up(self, event):
        """ Handles the right mouse button coming up when the tool is in the
        'panning' state.

        Stops panning if the right mouse button is the drag button.
        """
        if self.drag_button == "right":
            self._end_pan(event)
        return

    def panning_middle_up(self, event):
        """ Handles the middle mouse button coming up when the tool is in the
        'panning' state.

        Stops panning if the middle mouse button is the drag button.
        """
        if self.drag_button == "middle":
            self._end_pan(event)
        return

    def panning_mouse_move(self, event):
        """ Handles the mouse being moved when the tool is in the 'panning'
        state.
        """
        plot = self.component

        if self._auto_constrain and self.constrain_direction is None:
            # Determine the constraint direction
            x_orig, y_orig = self._original_xy
            if abs(event.x - x_orig) > abs(event.y - y_orig):
                self.constrain_direction = "x"
            else:
                self.constrain_direction = "y"

        direction_info = [("x", "width", 0), ("y", "height", 1)]
        for direction, bound_name, index in direction_info:
            if not self.constrain or self.constrain_direction == direction:
                mapper = getattr(plot, direction + "_mapper")
                domain_min, domain_max = mapper.domain_limits
                eventpos = getattr(event, direction)
                origpos = self._original_xy[index]

                screenlow, screenhigh = mapper.screen_bounds
                screendelta = self.speed * (eventpos - origpos)

                newlow = mapper.map_data(screenlow - screendelta)
                newhigh = mapper.map_data(screenhigh - screendelta)

                # Don't set the range in this dimension if the panning
                # would exceed the domain limits.
                # To do this offset properly, we would need to iteratively
                # solve for a root using map_data on successive trial
                # values.  As a first approximation, we're just going to
                # use a linear approximation, which works perfectly for
                # linear mappers (which is used 99% of the time).
                if domain_min is None:
                    if self.restrict_to_data:
                        domain_min = min([source.get_data().min()
                                          for source in mapper.range.sources])
                    else:
                        domain_min = -inf
                if domain_max is None:
                    if self.restrict_to_data:
                        domain_max = max([source.get_data().max()
                                          for source in mapper.range.sources])
                    else:
                        domain_max = inf

                if (newlow <= domain_min) and (newhigh >= domain_max):
                    # Don't do anything; effectively, freeze the pan
                    continue

                if newlow <= domain_min:
                    newlow = domain_min
                    # Calculate delta in screen space, which is always linear.
                    screen_delta = mapper.map_screen(domain_min) - screenlow
                    newhigh = mapper.map_data(screenhigh + screen_delta)
                elif newhigh >= domain_max:
                    newhigh = domain_max
                    # Calculate delta in screen space, which is always linear.
                    screen_delta = mapper.map_screen(domain_max) - screenhigh
                    newlow = mapper.map_data(screenlow + screen_delta)

                # Use .set_bounds() so that we don't generate two range_changed
                # events on the DataRange
                mapper.range.set_bounds(newlow, newhigh)

        event.handled = True

        self._original_xy = (event.x, event.y)
        plot.request_redraw()
        return

    def panning_mouse_leave(self, event):
        """ Handles the mouse leaving the plot when the tool is in the 'panning'
        state.

        Ends panning.
        """
        return self._end_pan(event)

    def _start_pan(self, event, capture_mouse=True):
        self._original_xy = (event.x, event.y)
        if self.constrain_key is not None:
            if getattr(event, self.constrain_key + "_down"):
                self.constrain = True
                self._auto_constrain = True
                self.constrain_direction = None
        self.event_state = "panning"
        if capture_mouse:
            event.window.set_pointer(self.drag_pointer)
            event.window.set_mouse_owner(self, event.net_transform())
        event.handled = True
        return

    def _end_pan(self, event):
        if self._auto_constrain:
            self.constrain = False
            self.constrain_direction = None
        self.event_state = "normal"
        event.window.set_pointer("arrow")
        if event.window.mouse_owner == self:
            event.window.set_mouse_owner(None)
        event.handled = True
        return

# EOF
