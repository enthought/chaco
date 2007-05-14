
from enthought.traits.api import Any, HasTraits, Instance, Int, List

from enthought.chaco2.api import KeySpec


class ToolHistoryMixin(HasTraits):
    """
    Mixin for tools that wish to go to maintain a tool state history and move
    forwards and backwards through that history stack.
    
    This mixin listens for keypressed events; if the subclass also needs to
    handle keypresses, it should call self._history_handle_key(event) to
    have this mixin properly process the event.
    """

    # Goes to the original/start state in the history
    reset_state_key = Instance(KeySpec, args=("Esc",))
    
    # Goes to the previous state in the history
    prev_state_key = Instance(KeySpec, args=("Left", "control"))
    
    # Goes to the next state in the history
    next_state_key = Instance(KeySpec, args=("Right", "control"))

    # The state stack
    _history = List
    
    # The index into _history that we are currently looking at
    _history_index = Int
    
    #------------------------------------------------------------------------
    # Abstract methods that subclasses must implement to handle keypresses
    #------------------------------------------------------------------------
    
    def _next_state_pressed(self):
        """
        Called when the tool needs to advance to the next state in the stack.
        self._history_index will have already been set to the index corresponding
        to the next state.
        """
        pass
        
    def _prev_state_pressed(self):
        """
        Called when the tool needs to advance to the prev state in the stack.
        self._history_index will have already been set to the index corresponding
        to the prev state.
        """
        pass
    
    def _reset_state_pressed(self):
        """
        Called when the tool needs to reset its history.  The history index will
        have already been set to 0.
        """
        pass


    #------------------------------------------------------------------------
    # Protected methods for subclasses to use
    #------------------------------------------------------------------------

    def _current_state(self):
        return self._history[self._history_index]

    def _reset_state(self, state):
        """
        Clears the history stack and sets the first/original state in the history
        """
        self._history = [state]
        self._history_index = 0
        return

    def _append_state(self, state, set_index=True):
        """
        Clears the history after the current history_index, and appends the given
        state to the history.
        """
        new_history = self._history[:self._history_index+1] + [state]
        self._history = new_history
        if set_index:
            self._history_index = len(self._history) - 1
        return

    def _pop_state(self):
        """
        Pops the most last state off the history stack.  If the current
        history index points to the end of the stack, then it is adjusted;
        otherwise, it is unaffected.  If the stack is empty, raises an
        IndexError.

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
