
# Major library imports
from numpy import array

# Enthought library imports
from enthought.enable2.api import ColorTrait
from enthought.traits.api import Any, Array, Enum, Event, false, Float, Int, List, \
                             Property, Str, Trait, true, Tuple

# Chaco imports
from enthought.chaco2.api import AbstractController


class RangeSelection(AbstractController):
    """
    Selects a range along the index or value axis.  The user right-click-drags
    to select a region, which stays selected until the user left-clicks to
    deselect.
    """
    
    # The axis to which this tool is perpendicular
    axis = Enum("index", "value")

    # The selected region, expressed as a tuple in data space.  This updates
    # and fires change events as the user is dragging.
    selection = Property
    
    # This event is fired when the user completes the selection.  The value of
    # the event is the dataspace 
    selection_completed = Event

    # The meanings of the states:
    #   normal: nothing has been selected, the user is not dragging the mouse
    #   selecting: the user is dragging the mouse and actively changing the 
    #              selection region; resizing of an existing selection also
    #              uses this mode
    #   selected: the user has released the mouse and a selection has been
    #             finalized.  the selection will remain until the user left-clicks
    #             or self.deselect() is called.
    event_state = Enum("normal", "selecting", "selected", "moving")

    #------------------------------------------------------------------------
    # Traits for overriding default object relationships
    #
    # By default, the RangeSelection assumes that self.component is a plot
    # and looks for the mapper and the axis_index on it.  If this is not the
    # case, then any (or all) three of these can be overriden by directly assigning
    # values to them.  To unset them and have them revert to default behavior,
    # assign "None" to them.
    #------------------------------------------------------------------------
    
    # By default plot is just self.component.
    plot = Property
    
    # By default, we use the mapper on self.plot that corresponds to self.axis
    mapper = Property
    
    # By default, we use self.plot.orientation, but this can be overriden and
    # set to 0 or 1.
    axis_index = Property

    listeners = List


    #------------------------------------------------------------------------
    # Configuring interaction control
    #------------------------------------------------------------------------
    
    # Controls if the user can resize the selection once it has been drawn.
    enable_resize = true
    
    # The pixel distance between the mouse event and a selection endpoint at
    # which the user action will be construed as a resize operation
    resize_margin = Int(7)
    
    # Should we allow the left button begin a selection?
    left_button_selects = false
    
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # The value of the override plot to use, if any.  If None, then uses
    # self.component.
    _plot = Trait(None, Any)

    # The value of the override mapper to use, if any.  If None, then uses the
    # mapper on self.component.
    _mapper = Trait(None, Any)
    
    # Shadow trait for the 'axis_index' property
    _axis_index = Trait(None, None, Int)

    # The data space start and end coordinates of the selected region, expressed
    # as a list
    _selection = Trait(None, None, Tuple, List, Array)
    
    # The selection in mask form
    _selection_mask = Array
    
    # Is the low or the high end of the selection being actively modified
    # by the mouse?
    _drag_edge = Enum("high", "low")
    
    #------------------------------------------------------------------------
    # These record the mouse position when the user is moving (not resizing)
    # the selection
    #------------------------------------------------------------------------
    
    # The position of the initial user click
    _down_point = Array  # (x,y)
    
    # the data space coords of _down_point
    _down_data_coord = Float
    
    # the original selection when the mouse went down
    _original_selection = Any


    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def deselect(self, event=None):
        """
        Deselects the highlighted region; essentially performs a reset on the
        tool.  Takes the event causing the deselect as an optional argument.
        """
        self.selection = None
        self.event_state = "normal"
        self.component.request_redraw()
        if event:
            event.window.set_pointer("arrow")
        return
    
    #------------------------------------------------------------------------
    # Event handlers for the "selected" event state
    #------------------------------------------------------------------------
    
    def selected_left_down(self, event):
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
            self._down_point = array([event.x, event.y])
            self._down_data_coord = self.mapper.map_data(self._down_point)[self.axis_index]
            self._original_selection = array(self.selection)
        else:
            self.deselect(event)
        return

    def selected_right_down(self, event):
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
                else:
                    self.deselect(event)
        else:
            # Treat this as a combination deselect + right down
            self.deselect(event)
            self.normal_right_down(event)
        return
    
    def selected_mouse_move(self, event):
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
        return
    
    def selected_mouse_leave(self, event):
        event.window.set_pointer("arrow")
        return

    #------------------------------------------------------------------------
    # Event handlers for the "moving" event state
    #------------------------------------------------------------------------
    
    def moving_left_up(self, event):
        self.event_state = "selected"
        return
    
    def moving_mouse_move(self, event):
        cur_point = array([event.x, event.y])
        cur_data_point = self.mapper.map_data(cur_point)[self.axis_index]
        original_selection = self._original_selection
        new_selection = original_selection + (cur_data_point - self._down_data_coord)
        selection_data_width = original_selection[1] - original_selection[0]
        
        range = self.mapper.range
        if min(new_selection) < range.low:
            new_selection = (range.low, range.low + selection_data_width)
        elif max(new_selection) > range.high:
            new_selection = (range.high - selection_data_width, range.high)
            
        self.selection = new_selection
        self.component.request_redraw()
        return

    def moving_mouse_leave(self, event):
        axis_index = self.axis_index
        low = self.plot.position[axis_index]
        high = low + self.plot.bounds[axis_index] - 1
        
        pos = self._get_axis_coord(event)
        if pos >= low and pos <= high:
            # the mouse left but was within the mapping range, so don't do anything
            return
        else:
            # the mouse left and exceeds the mapping range, so we need to slam
            # the selection all the way to the minimum or the maximum
            self.moving_mouse_move(event)
        return

    def moving_mouse_enter(self, event):
        if not event.left_down:
            return self.moving_left_up(event)
        return

    #------------------------------------------------------------------------
    # Event handlers for the "normal" event state
    #------------------------------------------------------------------------
    
    def normal_left_down(self, event):
        if self.left_button_selects:
            return self.normal_right_down(event)
    
    def normal_right_down(self, event):
        pos = self._get_axis_coord(event)
        mapped_pos = self.mapper.map_data(pos)
        self.selection = (mapped_pos, mapped_pos)
        self._set_sizing_cursor(event)
        self.event_state = "selecting"
        self.selecting_mouse_move(event)
        return

    #------------------------------------------------------------------------
    # Event handlers for the "selecting" event state
    #------------------------------------------------------------------------

    def selecting_mouse_move(self, event):
        if self.selection is not None:
            axis_index = self.axis_index
            low = self.plot.position[axis_index]
            high = low + self.plot.bounds[axis_index] - 1
            tmp = self._get_axis_coord(event)
            if tmp >= low and tmp <= high:
                new_edge = self.mapper.map_data(self._get_axis_coord(event))
                #new_edge = self._map_data(self._get_axis_coord(event))
                if self._drag_edge == "high":
                    low_val = self.selection[0]
                    if new_edge >= low_val:
                        self.selection = (low_val, new_edge)
                    else:
                        self.selection = (new_edge, low_val)
                        self._drag_edge = "low"
                else:
                    high_val = self.selection[1]
                    if new_edge <= high_val:
                        self.selection = (new_edge, high_val)
                    else:
                        self.selection = (high_val, new_edge)
                        self._drag_edge = "high"

                self.component.request_redraw()
        return
    
    def selecting_right_up(self, event):
        self.event_state = "selected"
        
        # Fire the "completed" event
        self.selection_completed = self.selection
        return
    
    def selecting_left_up(self, event):
        self.event_state = "selected"
        return
    
    def selecting_mouse_leave(self, event):
        # Determine if the event's position is outside our component's bounds;
        # if so, then clip the selection.
        axis_index = self.axis_index
        low = self.plot.position[axis_index]
        high = low + self.plot.bounds[axis_index] - 1
        
        old_selection = self.selection
        selection_low = old_selection[0]
        selection_high = old_selection[1]
        
        pos = self._get_axis_coord(event)
        if pos >= high:
            selection_high = self.mapper.map_data(high)
        elif pos <= low:
            selection_low = self.mapper.map_data(low)
        
        self.selection = (selection_low, selection_high)
        event.window.set_pointer("arrow")
        self.component.request_redraw()
        return

    def selecting_mouse_enter(self, event):
        if not event.right_down:
            # If we were in the "selecting" state when the mouse left, and
            # the mouse has entered withou the right button being down,
            # then treat this like we got a selecting_right_up event.
            return self.selecting_right_up(event)
        else:
            self._set_sizing_cursor(event)
        return
    

    #------------------------------------------------------------------------
    # Property getter/setters
    #------------------------------------------------------------------------
    
    def _get_plot(self):
        if self._plot is not None:
            return self._plot
        else:
            return self.component
    
    def _set_plot(self, val):
        self._plot = val
        return
    
    def _get_mapper(self):
        if self._mapper is not None:
            return self._mapper
        else:
            return getattr(self.plot, self.axis + "_mapper")
        
    def _set_mapper(self, new_mapper):
        self._mapper = new_mapper
        return
    
    def _get_axis_index(self):
        if self._axis_index is None:
            return self._determine_axis()
        else:
            return self._axis_index

    def _set_axis_index(self, val):
        self._axis_index = val
        return

    def _get_selection(self):
        selection = getattr(self.plot, self.axis).metadata["selections"]
        return selection
    
    def _set_selection(self, val):
        oldval = self._selection
        self._selection = val
        
        datasource = getattr(self.plot, self.axis, None)

        if datasource is not None:
        
            # Set the selection range on the datasource
            datasource.metadata["selections"] = val
            datasource.metadata_changed = {"selections": val}
            
            # Set the selection mask on the datasource
            selection_masks = \
                datasource.metadata.setdefault("selection_masks", [])
            for index in range(len(selection_masks)):
                if id(selection_masks[index]) == id(self._selection_mask):
                    del selection_masks[index]
                    break

            if val is not None:
                low, high = val
                data_pts = datasource.get_data()
                new_mask = (data_pts>=low) & (data_pts<=high)
                selection_masks.append(new_mask)
                self._selection_mask = new_mask
            datasource.metadata_changed = {"selection_masks": val}
            
        self.trait_property_changed("selection", oldval, val)

        for l in self.listeners:
            if hasattr(l, "set_value_selection"):
                l.set_value_selection(val)
        
        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------
    
    def _get_selection_screencoords(self):
        """
        Returns a tuple of (x1, x2) screen space coordinates of the start
        and end selection points.  If there is no current selection, then
        returns None.
        """
        selection = self.selection
        if selection is not None and len(selection) == 2:
            mapper = self.mapper
            return self.mapper.map_screen(array(selection))
        else:
            return None
    
    def _set_sizing_cursor(self, event):
        """
        Sets the correct cursor shape on the window of the event, given our
        orientation and axis.
        """
        if self.axis_index == 0:
            # horizontal range selection, so use left/right arrow
            event.window.set_pointer("size left")
        else:
            # vertical range selection, so use up/down arrow
            event.window.set_pointer("size top")
        return
    
    def _get_axis_coord(self, event, axis="index"):
        """
        Returns the coordinate of the event along the axis of interest
        to us (or along the orthogonal axis, if axis="value").
        """
        event_pos = (event.x, event.y)
        if axis == "index":
            return event_pos[ self.axis_index ]
        else:
            return event_pos[ 1 - self.axis_index ]

    def _determine_axis(self):
        """
        Determines whether the index of the coordinate along our axis of
        interest is the first or second element of an (x,y) coordinate tuple.
        This method is only called if self._axis_index hasn't been set (or is None).
        """
        if self.axis == "index":
            if self.plot.orientation == "h":
                return 0
            else:
                return 1
        else:   # self.axis == "value"
            if self.plot.orientation == "h":
                return 1
            else:
                return 0

    def __mapper_changed(self):
        self.deselect()
        return

    def _axis_changed(self, old, new):
        if old is not None:
            self.plot.on_trait_change(self.__mapper_changed, old + "_mapper", remove=True)
        if new is not None:
            self.plot.on_trait_change(self.__mapper_changed, old + "_mapper", remove=True)
        return


# EOF
