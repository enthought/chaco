
# Enthought library imports
from enthought.enable2.api import Pointer
from enthought.traits.api import Enum, false, Float, Tuple

# Chaco imports
from enthought.chaco2.api import BaseTool

class PanTool(BaseTool):
    """
    Allows the user to pan around a plot my clicking a mouse button and
    dragging.
    """
    
    # Which mouse button initiates the drag
    drag_button = Enum("left", "right")
    
    # The cursor to use when panning
    drag_pointer = Pointer("hand")

    # Scaling factor on the panning "speed"
    speed = Float(1.0)

    # The modifier key which, if depressed when the drag is initiated, constrains
    # the panning to only happen in the direction of largest initial motion.
    # It is possible to permanently restrict this tool to always drag along one
    # direction.  To do so, set constrain=True, constrain_key=None, and
    # constrain_direction to the desired direction.
    constrain_key = Enum(None, "shift", "control", "alt")
    
    # Should the panning be constrained to one direction?
    constrain = false
    
    # The direction of constrained draw.  None means that the user has initiated
    # the drag and depressed the constrain_key, but hasn't moved the mouse yet
    # (and thus the magnitude of the components of the next mouse_move event
    # will determine the constrain_direction).
    constrain_direction = Enum(None, "x", "y")
    
    # (x,y) of the point where the mouse button was depressed
    _original_xy = Tuple
    
    # data coordinates of self._original_xy.  This may be either (index,value)
    # or (value,index) depending on the component's orientation.
    _original_data = Tuple

    # keeps track of whether or not constrain=True was triggered by the contrain_key,
    # or set programmatically
    _auto_constrain = false
    
    
    #------------------------------------------------------------------------
    # Inherited BaseTool traits
    #------------------------------------------------------------------------

    draw_mode = "none"
    visible = False
    event_state = Enum("normal", "panning")


    def normal_left_down(self, event):
        if self.drag_button == "left":
            self._start_pan(event)
        return
    
    def normal_right_down(self, event):
        if self.drag_button == "right":
            self._start_pan(event)
        return

    def panning_left_up(self, event):
        if self.drag_button == "left":
            self._end_pan(event)
        return
    
    def panning_right_up(self, event):
        if self.drag_button == "right":
            self._end_pan(event)
        return

    def panning_mouse_move(self, event):
        plot = self.component
        
        if self._auto_constrain and self.constrain_direction is None:
            # Determine the constraint direction
            if abs(event.x - self._original_xy[0]) > abs(event.y - self._original_xy[1]):
                self.constrain_direction = "x"
            else:
                self.constrain_direction = "y"

        xrange = plot.x_mapper.range
        yrange = plot.y_mapper.range

        if not self.constrain or self.constrain_direction == "x":
            clicked_x = plot.x_mapper.map_data(event.x)
            high = xrange.high
            low = xrange.low
            if high == low:
                high = low + 1.0
            xscale = plot.width / (high - low)
            delta_x = self.speed * (event.x - self._original_xy[0]) / xscale
            if getattr(plot, "x_direction", None) == "flipped":
                delta_x = -delta_x
            xrange.set_bounds(xrange.low - delta_x, xrange.high - delta_x)

        if not self.constrain or self.constrain_direction == "y":
            clicked_y = plot.y_mapper.map_data(event.y)
            high = yrange.high
            low = yrange.low
            if high == low:
                high = low + 1.0
            yscale = plot.height / (high - low)
            delta_y = self.speed * (event.y - self._original_xy[1]) / yscale
            if getattr(plot, "y_direction", None) == "flipped":
                delta_y = -delta_y
            yrange.set_bounds(yrange.low - delta_y, yrange.high - delta_y)
        
        event.handled = True
        
        self._original_xy = (event.x, event.y)
        plot.request_redraw()
        return

    def panning_mouse_leave(self, event):
        return self._end_pan(event)
    
    def _start_pan(self, event):
        self._original_xy = (event.x, event.y)
        if self.constrain_key is not None:
            if getattr(event, self.constrain_key + "_down"):
                self.constrain = True
                self._auto_constrain = True
                self.constrain_direction = None
        self.event_state = "panning"
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
