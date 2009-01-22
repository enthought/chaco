""" Defines the PanTool class.
"""
# Enthought library imports
from enthought.enable.api import BaseTool, Pointer
from enthought.traits.api import Bool, Enum, Float, Tuple


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
    
    # Constrain the panning to one direction?
    constrain = Bool(False)
    
    # The direction of constrained draw. A value of None means that the user
    # has initiated the drag and pressed the constrain_key, but hasn't moved
    # the mouse yet; the magnitude of the components of the next mouse_move
    # event will determine the constrain_direction.
    constrain_direction = Enum(None, "x", "y")
    
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
                if (domain_min is not None and newlow < domain_min):
                    delta = newhigh - newlow
                    newlow = domain_min
                    newhigh = domain_min + delta
                if (domain_max is not None and newhigh > domain_max):
                    delta = newhigh - newlow
                    newhigh = domain_max
                    newlow = domain_max - delta

                # Use .set_bounds() so that we don't generate two range_changed
                # events on the DataRange
                range.set_bounds(newlow, newhigh)
               
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
