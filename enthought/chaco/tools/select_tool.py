

# Enthought library imports
from enthought.enable.api import BaseTool, KeySpec
from enthought.traits.api import Enum, Float, Instance


class SelectTool(BaseTool):
    """ Base class for tools that handle some level of click-to-select
    interaction.  Handles the logic of different kinds of selection
    modes.  Subclasses only need to implement a few concrete methods
    to handle actual selection/deselection.
    """

    # The threshold, in pixels, around the cursor location to search for points.
    threshold = Float(5.0)

    # How selections are handled:
    #
    # "toggle"
    #     The user clicks on points (while optionally holding down a modifier
    #     key) to select or deselect them. If the point is already selected,
    #     clicking it again deselects it. The modifier key to use is set by
    #     **multiselect_modifier**. The only way to deselect points is by 
    #     clicking on them; clicking on a screen space outside of the plot does
    #     not deselect points.
    # "multi"
    #     Like **toggle** mode, except that the user can deselect all points
    #     at once by clicking on the plot area away from a point.
    # "single"
    #     The user can only select a single point at a time.  
    # "off"
    #     The user cannot select points via clicking.
    selection_mode = Enum("toggle", "multi", "single", "off")

    # The modifier key to use to multi-select points.  Only used in **toggle**
    # and **multi** selection modes.
    multiselect_modifier = Instance(KeySpec, args=(None, "control"), allow_none=True)


    def _get_selection_state(self, event):
        """ Returns a tuple reflecting the current selection state

        Parameters
        ----------
        event : enable KeyEvent or MouseEvent

        Returns
        -------
        (already_selected, clicked) : tuple of Bool
            clicked is True if the item corresponding to the input event has
            just been clicked.
            already_selected indicates that the item corresponding to the
            input event is already selected.
        
        """
        raise NotImplementedError

    def _get_selection_token(self, event):
        """ Returns a token corresponding to the selection event.  This token
        is passed in to the select and deselect methods.  By default, this
        just returns the event itself.
        """
        return event

    def _select(self, token, append=True):
        """ Selects the given token.
        """
        raise NotImplementedError

    def _deselect(self, token, append=True):
        """ Deselects the given token.
        """
        raise NotImplementedError
 
    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed when the tool is in the
        'normal' state.
        
        If selecting is enabled and the cursor is within **threshold** of a
        data point, the method calls the subclass's _select" or _deselect
        methods to perform the appropriate action, given the current
        selection_mode.
        """
        if self.selection_mode != "off":
            already_selected, clicked = self._get_selection_state(event)
            modifier_down = self.multiselect_modifier.match(event)
            token = self._get_selection_token(event)

            if (self.selection_mode == "single") or\
                    (self.selection_mode == "multi" and not modifier_down):
                if clicked and not already_selected:
                    if self.selection_mode == "single":
                        self._select(token, append=False)
                    else:
                        self._select(token, append=True)
                    event.handled = True
                else:
                    self._deselect(token)

            else:  # multi or toggle
                if clicked:
                    if already_selected:
                        self._deselect(token)
                    else:
                        self._select(token)
                    event.handled = True
            return



