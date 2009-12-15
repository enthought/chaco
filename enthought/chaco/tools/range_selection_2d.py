""" Defines the RangeSelection controller class.
"""
# Major library imports
import numpy

# Enthought library imports
from enthought.traits.api import Any, Array, Bool, Enum, Event, Float, Int, List, \
                             Property, Trait, Tuple

# Chaco imports
from range_selection import RangeSelection


class RangeSelection2D(RangeSelection):
    """ Selects a range along the index or value axis for plots on 2D data,
        such as image plots
    
    The user right-click-drags to select a region, which stays selected until
    the user left-clicks to deselect.
    """


    #------------------------------------------------------------------------
    # Event handlers for the "selected" event state
    #------------------------------------------------------------------------
    
    def selected_left_down(self, event):
        """ Handles the left mouse button being pressed when the tool is in
        the 'selected' state.
        
        If the user is allowed to resize the selection, and the event occurred
        within the resize margin of an endpoint, then the tool switches to the
        'selecting' state so that the user can resize the selection.
        
        If the event is within the bounds of the selection region, then the tool
        switches to the 'moving' states.
        
        Otherwise, the selection becomes deselected.
        """
        screen_bounds = self._get_selection_screencoords()
        if screen_bounds is None:
            self.deselect(event)
            return
        low = min(screen_bounds)
        high = max(screen_bounds)
        tmp = (event.x, event.y)
        ndx = self._determine_axis()
        mouse_coord = tmp[ndx]
        
        if self.enable_resize:
            if (abs(mouse_coord - high) <= self.resize_margin) or \
                            (abs(mouse_coord - low) <= self.resize_margin):
                return self.selected_right_down(event)
        
        if tmp[self.axis_index] >= low and tmp[self.axis_index] <= high:
            self.event_state = "moving"
            self._down_point = numpy.array([event.x, event.y])
            self._down_data_coord = self._map_data([self._down_point])[0][self.axis_index]
            
            self._original_selection = numpy.array(self.selection)
        elif self.allow_deselection:
            self.deselect(event)
        else:
            # Treat this as a combination deselect + left down
            self.deselect(event)
            self.normal_left_down(event)
        event.handled = True
        return

    def selected_right_down(self, event):
        """ Handles the right mouse button being pressed when the tool is in
        the 'selected' state.
        
        If the user is allowed to resize the selection, and the event occurred
        within the resize margin of an endpoint, then the tool switches to the
        'selecting' state so that the user can resize the selection.
        
        Otherwise, the selection becomes deselected, and a new selection is
        started..
        """
        if self.enable_resize:
            coords = self._get_selection_screencoords()
            if coords is not None:
                start, end = coords
                tmp = (event.x, event.y)
                ndx = self._determine_axis()
                mouse_coord = tmp[ndx]
                # We have to do a little swapping; the "end" point
                # is always what gets updated, so if the user
                # clicked on the starting point, we have to reverse
                # the sense of the selection.
                if abs(mouse_coord - end) <= self.resize_margin:
                    self.event_state = "selecting"
                    self._drag_edge = "high"
                    self.selecting_mouse_move(event)
                elif abs(mouse_coord - start) <= self.resize_margin:
                    self.event_state = "selecting"
                    self._drag_edge = "low"
                    self.selecting_mouse_move(event)
                elif self.allow_deselection:
                    self.deselect(event)
                else:
                    # Treat this as a combination deselect + right down
                    self.deselect(event)
                    self.normal_right_down(event)
        else:
            # Treat this as a combination deselect + right down
            self.deselect(event)
            self.normal_right_down(event)
        event.handled = True
        return
    
    def selected_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'selected' state.
        
        If the user is allowed to resize the selection, and the event
        occurred within the resize margin of an endpoint, then the cursor
        changes to indicate that the selection could be resized.
        
        Otherwise, the cursor is set to an arrow.
        """
        if self.enable_resize:
            # Change the mouse cursor when the user moves within the resize margin
            coords = self._get_selection_screencoords()
            if coords is not None:
                start, end = coords
                tmp = (event.x, event.y)
                ndx = self._determine_axis()
                mouse_coord = tmp[ndx]
                if abs(mouse_coord - end) <= self.resize_margin or \
                                    abs(mouse_coord - start) <= self.resize_margin:
                    self._set_sizing_cursor(event)
                    return
        event.window.set_pointer("arrow")
        event.handled = True
        return
    
    #------------------------------------------------------------------------
    # Event handlers for the "moving" event state
    #------------------------------------------------------------------------
        
    def moving_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'moving' state.
        
        Moves the selection range by an amount corresponding to the amount
        that the mouse has moved since its button was pressed. If the new
        selection range overlaps the endpoints of the data, it is truncated to
        that endpoint.
        """
        cur_point = numpy.array([event.x, event.y])
        cur_data_point = self._map_data([cur_point])[0]
        original_selection = self._original_selection
        new_selection = original_selection + (cur_data_point[self.axis_index] \
                                              - self._down_data_coord)
        selection_data_width = original_selection[1] - original_selection[0]

        range = self.mapper.range
        range_low = range.low[self.axis_index]
        range_high = range.high[self.axis_index]
        if min(new_selection) < range_low:
            new_selection = (range_low, range_low + selection_data_width)
        elif max(new_selection) > range_high:
            new_selection = (range_high - selection_data_width, range_high)
                
        self.selection = new_selection
        self.selection_completed = new_selection
        self.component.request_redraw()
        event.handled = True
        return
    
    #------------------------------------------------------------------------
    # Event handlers for the "normal" event state
    #------------------------------------------------------------------------
        
    def normal_right_down(self, event):
        """ Handles the right mouse button being pressed when the tool is in 
        the 'normal' state.
        
        Puts the tool into 'selecting' mode, changes the cursor to show that it
        is selecting, and starts defining the selection.
        
        """
        x_pos = self._get_axis_coord(event, "index")
        y_pos = self._get_axis_coord(event, "value")
        mapped_pos = self._map_data([(x_pos,y_pos)])[0][self.axis_index]
        
        self.selection = (mapped_pos, mapped_pos)
            
        self._set_sizing_cursor(event)
        self.event_state = "selecting"
        self.selecting_mouse_move(event)
        return

    #------------------------------------------------------------------------
    # Event handlers for the "selecting" event state
    #------------------------------------------------------------------------

    def selecting_mouse_move(self, event):
        """ Handles the mouse being moved when the tool is in the 'selecting'
        state.
        
        Expands the selection range at the appropriate end, based on the new
        mouse position.
        """
        if self.selection is not None:
            axis_index = self.axis_index
            low = self.plot.position[axis_index]
            high = low + self.plot.bounds[axis_index] - 1
            tmp = self._get_axis_coord(event)
            if tmp >= low and tmp <= high:
                x_pos = self._get_axis_coord(event, "index")
                y_pos = self._get_axis_coord(event, "value")
                new_edge = self._map_data([(x_pos,y_pos)])[0][self.axis_index]
                                    
                if self._drag_edge == "high":
                    low_val = self.selection[0]
                    
                    # the selection should be a range consisting of 2 points, 
                    # if it appears that only 1 point is selected, move one 
                    # edge over a pixel
                    if new_edge == low_val:
                        new_edge = self._map_data([(x_pos+1,y_pos+1)])[0][self.axis_index]
                        
                    if new_edge > low_val:
                        self.selection = (low_val, new_edge)
                    else:
                        self.selection = (new_edge, low_val)
                        self._drag_edge = "low"
                else:
                    high_val = self.selection[1]
                    
                    # the selection should be a range consisting of 2 points, 
                    # if it appears that only 1 point is selected, move one 
                    # edge over a pixel
                    if new_edge == high_val:
                        new_edge = self._map_data([(x_pos-1,y_pos-1)])[0][self.axis_index]
                        
                    if new_edge < high_val:
                        self.selection = (new_edge, high_val)
                    else:
                        self.selection = (high_val, new_edge)
                        self._drag_edge = "high"
                        
                self.component.request_redraw()
            event.handled = True
        return

    def selecting_mouse_leave(self, event):
        """ Handles the mouse leaving the plot when the tool is in the 
        'selecting' state.
        
        Determines whether the event's position is outside the component's
        bounds, and if so, clips the selection. Sets the cursor to an arrow.
        """
        axis_index = self.axis_index
        low = self.plot.position[axis_index]
        high = low + self.plot.bounds[axis_index] - 1
        
        old_selection = self.selection
        selection_low = old_selection[0]
        selection_high = old_selection[1]
        
        pos = self._get_axis_coord(event)
        if pos >= high:
            if self.axis == 'index':
                selection_high = self._map_data([(high, 0)])[0][self.axis_index]
            else:
                selection_high = self._map_data([(0, high)])[0][self.axis_index]                    
        elif pos <= low:
            if self.axis == 'index':
                selection_low = self._map_data([(low, 0)])[0][self.axis_index]
            else:
                selection_low = self._map_data([(0, low)])[0][self.axis_index]

        self.selection = (selection_low, selection_high)
        event.window.set_pointer("arrow")
        self.component.request_redraw()
        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------
    
    def _map_data(self, screen_pts):
        return self.mapper.map_data(screen_pts)
        
    def _map_screen(self, data_pts):
        return self.mapper.map_screen(data_pts)
    
    def _get_selection_screencoords(self):
        """ Returns a tuple of (x1, x2) screen space coordinates of the start
        and end selection points.  
        
        If there is no current selection, then it returns None.
        """
        selection = self.selection
        if selection is not None and len(selection) == 2:
            if self.axis == 'index':
                return [x for x,y in self._map_screen([(x,0) for x in self.selection])]
            else:
                return [y for x,y in self._map_screen([(0,y) for y in self.selection])]
                
        else:
            return None
