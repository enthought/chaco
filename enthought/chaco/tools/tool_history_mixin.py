""" Defines the ToolHistoryMixin class.
""" 
from enthought.traits.api import HasTraits, Instance, Int, List
from enthought.enable.api import KeySpec


class ToolHistoryMixin(HasTraits):
    """ A mix-in class for tools to maintain a tool state history and to move
    backwards and forwards through that history stack.
    
    This mix-in listens for keypressed events; to handle keypresses in a 
    subclass, call self._history_handle_key(event) to have this mix-in properly
    process the event.
    """

    # Key to go to the original or start state in the history.
    reset_state_key = Instance(KeySpec, args=("Esc",))
    
    # Key to go to the previous state in the history.
    prev_state_key = Instance(KeySpec, args=("Left", "control"))
    
    # Key to go to the next state in the history.
    next_state_key = Instance(KeySpec, args=("Right", "control"))

    # The state stack.
    _history = List
    
    # The current index into _history 
    _history_index = Int
    
    #------------------------------------------------------------------------
    # Abstract methods that subclasses must implement to handle keypresses
    #------------------------------------------------------------------------
    
    def _next_state_pressed(self):
        """ Called when the tool needs to advance to the next state in the 
        stack.
        
        The **_history_index** will have already been set to the index 
        corresponding to the next state.
        """
        pass
        
    def _prev_state_pressed(self):
        """ Called when the tool needs to advance to the previous state in the
        stack.
        
        The **_history_index** will have already been set to the index
        corresponding to the previous state.
        """
        pass
    
    def _reset_state_pressed(self):
        """ Called when the tool needs to reset its history.  
        
        The history index will have already been set to 0.
        """
        pass


    #------------------------------------------------------------------------
    # Protected methods for subclasses to use
    #------------------------------------------------------------------------

    def _current_state(self):
        """ Returns the current history state.
        """
        return self._history[self._history_index]

    def _reset_state(self, state):
        """ Clears the history stack and sets the first or original state in 
        the history to *state*.
        """
        self._history = [state]
        self._history_index = 0
        return

    def _append_state(self, state, set_index=True):
        """ Clears the history after the current **_history_index**, and 
        appends the given state to the history.
        
        If *set_index* is True, the method sets the **_history_index** to
        match the new, truncated history. If it is False, the history index
        is unchanged.
        """
        new_history = self._history[:self._history_index+1] + [state]
        self._history = new_history
        if set_index:
            self._history_index = len(self._history) - 1
        return

    def _pop_state(self):
        """ Pops the most last state off the history stack.  
        
        If the history index points to the end of the stack, then it is 
        adjusted; otherwise, the index is unaffected. If the stack is empty,
        the method raises an IndexError.

        Returns the popped state.
        """
        if len(self._history) == 0:
            raise IndexError("Unable to pop empty history stack.")

        if self._history_index == len(self._history) - 1:
            self._history_index -= 1

        return self._history.pop()

    #------------------------------------------------------------------------
    # Private methods / event handlers
    #------------------------------------------------------------------------

    def normal_key_pressed(self, event):
        """ Handles a key being pressed, and takes appropriate action if it is
        one of the history keys defined for this class.
        """
        self._history_handle_key(event)
        return
    
    def _history_handle_key(self, event):
        if self.reset_state_key.match(event):
            self._history_index = 0
            self._reset_state_pressed()
            event.handled = True
        elif self.prev_state_key.match(event):
            if self._history_index > 0:
                self._history_index -= 1
                self._prev_state_pressed()
            event.handled = True
        elif self.next_state_key.match(event):
            if self._history_index <= len(self._history) - 2:
                self._history_index += 1
                self._next_state_pressed()
            event.handled = True
        else:
            return




# EOF
