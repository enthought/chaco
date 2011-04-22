
from numpy import inf

from enable.api import Pointer
from enable.tools.drag_tool import DragTool
from traits.api import Bool, Enum, Float, Tuple


class PanTool(DragTool):
    """ An implementation of a pan tool based on the DragTool instead of
    a bare BaseTool
    """

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
    #event_state = Enum("normal", "panning")


    def drag_start(self, event):
        """ Called when the drag operation starts """
        self._start_pan(event)

    def dragging(self, event):
        plot = self.component

        if self._auto_constrain and self.constrain_direction is None:
            # Determine the constraint direction
            if abs(event.x - self._original_xy[0]) > abs(event.y - self._original_xy[1]):
                self.constrain_direction = "x"
            else:
                self.constrain_direction = "y"

        for direction, bound_name, ndx in [("x","width",0), ("y","height",1)]:
            if not self.constrain or self.constrain_direction == direction:
                mapper = getattr(plot, direction + "_mapper")
                range = mapper.range
                domain_min, domain_max = mapper.domain_limits
                eventpos = getattr(event, direction)
                origpos = self._original_xy[ndx]

                screenlow, screenhigh = mapper.screen_bounds
                screendelta = self.speed * (eventpos - origpos)
                #if getattr(plot, direction + "_direction", None) == "flipped":
                #    screendelta = -screendelta

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
                        domain_min = min([source.get_data().min() for source in range.sources])
                    else:
                        domain_min = -inf
                if domain_max is None:
                    if self.restrict_to_data:
                        domain_max = max([source.get_data().max() for source in range.sources])
                    else:
                        domain_max = inf
                if (newlow <= domain_min) and (newhigh >= domain_max):
                    # Don't do anything; effectively, freeze the pan
                    continue
                if newlow <= domain_min:
                    delta = newhigh - newlow
                    newlow = domain_min
                    # Don't let the adjusted newhigh exceed domain_max; this
                    # can happen with a nonlinear mapper.
                    newhigh = min(domain_max, domain_min + delta)
                elif newhigh >= domain_max:
                    delta = newhigh - newlow
                    newhigh = domain_max
                    # Don't let the adjusted newlow go below domain_min; this
                    # can happen with a nonlinear mapper.
                    newlow = max(domain_min, domain_max - delta)

                # Use .set_bounds() so that we don't generate two range_changed
                # events on the DataRange
                range.set_bounds(newlow, newhigh)

        event.handled = True

        self._original_xy = (event.x, event.y)
        plot.request_redraw()
        return

    def drag_cancel(self, event):
        # We don't do anything for "cancelling" of the drag event because its
        # transient states during the drag are generally valid and useful
        # terminal states unto themselves.
        pass

    def drag_end(self, event):
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


