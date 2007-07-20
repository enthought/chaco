""" Defines the base DragTool class.
"""
# Enthought library imports
from enthought.traits.api import Any, Dict, Enum, false, Float, Instance, Trait, true, Tuple

# Chaco imports
from enthought.chaco2.api import BaseTool


class DragTool(BaseTool):
    """ Base class for tools that are activated by a drag operation.  
    
    This tool insulates the drag operation from double clicks and the like, and
    gracefully manages the transition into and out of drag mode.
    """

    # The mouse button used for this drag operation.
    drag_button = Enum("left", "right")

    # End the drag operation if the mouse leaves the associated component?
    end_drag_on_leave = true
    
    # These keys, if pressed during drag, cause the drag operation to reset.
    cancel_keys = Tuple("Esc")
    
    # The position of the initial mouse click that started the drag.
    # Typically, tools that move things around use this
    # position to do hit-testing to determine what object to "pick up".
    mouse_down_position = Tuple(0.0, 0.0)

    # The modifier key that must be used to activate the tool.
    modifier_key = Enum("none", "shift", "alt", "control")

    #------------------------------------------------------------------------
    # Private traits used by DragTool
    #------------------------------------------------------------------------

    # The possible states of this tool.
    _drag_state = Enum("nondrag", "dragging")
    
    # Records whether a mouse_down event has been received while in
    # "nondrag" state.  This is a safety check to prevent the tool from suddenly
    # getting mouse focus while the mouse button is down (either from
    # window_enter or programmatically) and erroneously
    # initiating a drag.
    _mouse_down_received = false


    #------------------------------------------------------------------------
    # Interface for subclasses
    #------------------------------------------------------------------------

    def is_draggable(self, x, y):
        """ Returns whether the (x,y) position is in a region that is OK to 
        drag.  
        
        Used by the tool to determine when to start a drag.
        """
        return True

    def drag_start(self, event):
        """ Called when the drag operation starts.  
        
        The *event* parameter is the mouse event that established the drag 
        operation; its **x** and **y** attributes correspond to the current
        location of the mouse, and not to the position of the mouse when the 
        initial left_down or right_down event happened.
        """
        pass

    def dragging(self, event):
        """ This method is called for every mouse_move event that the tool 
        receives while the user is dragging the mouse.  
        
        It is recommended that subclasses do most of their work in this method.
        """
        pass

    def drag_cancel(self, event):
        """ Called when the drag is cancelled.
        
        A drag is usually cancelled by receiving a mouse_leave event when 
        end_drag_on_leave is True, or by the user pressing any of the 
        **cancel_keys**.
        """
        pass

    def drag_end(self, event):
        """ Called when a mouse event causes the drag operation to end.
        """
        pass

    #------------------------------------------------------------------------
    # Private methods for handling drag
    #------------------------------------------------------------------------

    def _dispatch_stateful_event(self, event, suffix):
        # We intercept a lot of the basic events and re-map them if
        # necessary.  "consume" indicates whether or not we should pass
        # the event to the subclass's handlers.
        consume = False
        if suffix == self.drag_button + "_down":
            consume = self._drag_button_down(event)
        elif suffix == self.drag_button + "_up":
            consume = self._drag_button_up(event)
        elif suffix == "mouse_move":
            consume = self._drag_mouse_move(event)
        elif suffix == "mouse_leave":
            consume = self._drag_mouse_leave(event)
        elif suffix == "mouse_enter":
            consume = self._drag_mouse_enter(event)
        elif suffix == "key_pressed":
            consume = self._drag_cancel_keypressed(event)
        
        if not consume:
            BaseTool._dispatch_stateful_event(self, event, suffix)
        else:
            event.handled = True
        return

    def _cancel_drag(self, event):
        old_state = self._drag_state
        self._drag_state = "nondrag"
        if old_state == "dragging":
            self.drag_cancel(event)
        self._mouse_down_received = False
        return

    def _drag_cancel_keypressed(self, event):
        if self._drag_state != "nondrag":
            self._cancel_drag(event)
            return True
        else:
            return False

    def _drag_mouse_move(self, event):
        state = self._drag_state
        button_down = getattr(event, self.drag_button + "_down")
        if state == "nondrag":
            if button_down and self._mouse_down_received and \
                   self.is_draggable(*self.mouse_down_position):
                self._drag_state = "dragging"
                self.drag_start(event)
                return self._drag_mouse_move(event)
            return False
        elif state == "dragging":
            if button_down:
                return self.dragging(event)
            else:
                return self._drag_button_up(event)
        
        # If we don't invoke the subclass drag handler, then don't consume the event.
        return False

    def _drag_button_down(self, event):
        if self._drag_state == "nondrag":
            self.mouse_down_position = (event.x, event.y)
            self._mouse_down_received = True
        return False

    def _drag_button_up(self, event):
        self._mouse_down_received = False
        state = self._drag_state
        if state == "dragging":
            self._drag_state = "nondrag"
            return self.drag_end(event)
        
        # If we don't invoke the subclass drag handler, then don't consume the event.
        return False

    def _drag_mouse_leave(self, event):
        state = self._drag_state
        self._mouse_down_received = False
        if state == "nondrag":
            pass
        elif state == "dragging":
            if self.end_drag_on_leave:
                return self.drag_cancel(event)
        return False

    def _drag_mouse_enter(self, event):
        state = self._drag_state
        if state == "nondrag":
            pass
        elif state == "dragging":
            pass
        return False


# EOF
