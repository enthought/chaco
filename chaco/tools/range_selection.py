""" Defines the RangeSelection controller class.
"""
# Major library imports
from numpy import array

# Enthought library imports
from traits.api import Any, Array, Bool, Enum, Event, Float, Int, Instance, \
                         List, Property, Str, Trait, Tuple
from enable.api import KeySpec

# Chaco imports
from chaco.api import AbstractController


class RangeSelection(AbstractController):
    """ Selects a range along the index or value axis.

    The user right-click-drags to select a region, which stays selected until
    the user left-clicks to deselect.
    """

    # The axis to which this tool is perpendicular.
    axis = Enum("index", "value")

    # The selected region, expressed as a tuple in data space.  This updates
    # and fires change-events as the user is dragging.
    selection = Property

    selection_mode = Enum("set", "append")

    # This event is fired whenever the user completes the selection, or when a
    # finalized selection gets modified.  The value of the event is the data
    # space range.
    selection_completed = Event

    # The name of the metadata on the datasource that we will write
    # self.selection to
    metadata_name = Str("selections")

    # Either "set" or "append", depending on whether self.append_key was
    # held down
    selection_mode_metadata_name = Str("selection_mode")

    # The name of the metadata on the datasource that we will set to a numpy
    # boolean array for masking the datasource's data
    mask_metadata_name = Str("selection_masks")

    # The possible event states of this selection tool (overrides
    # enable.Interactor).
    #
    # normal:
    #     Nothing has been selected, and the user is not dragging the mouse.
    # selecting:
    #     The user is dragging the mouse and actively changing the
    #     selection region; resizing of an existing selection also
    #     uses this mode.
    # selected:
    #     The user has released the mouse and a selection has been
    #     finalized.  The selection remains until the user left-clicks
    #     or self.deselect() is called.
    # moving:
    #   The user moving (not resizing) the selection range.
    event_state = Enum("normal", "selecting", "selected", "moving")

    #------------------------------------------------------------------------
    # Traits for overriding default object relationships
    #
    # By default, the RangeSelection assumes that self.component is a plot
    # and looks for the mapper and the axis_index on it.  If this is not the
    # case, then any (or all) three of these can be overriden by directly
    # assigning values to them.  To unset them and have them revert to default
    # behavior, assign "None" to them.
    #------------------------------------------------------------------------

    # The plot associated with this tool By default, this is just
    # self.component.
    plot = Property

    # The mapper for associated with this tool. By default, this is the mapper
    # on **plot** that corresponds to **axis**.
    mapper = Property

    # The index to use for **axis**. By default, this is self.plot.orientation,
    # but it can be overriden and set to 0 or 1.
    axis_index = Property

    # List of listeners that listen to selection events.
    listeners = List

    #------------------------------------------------------------------------
    # Configuring interaction control
    #------------------------------------------------------------------------

    # Can the user resize the selection once it has been drawn?
    enable_resize = Bool(True)

    # The pixel distance between the mouse event and a selection endpoint at
    # which the user action will be construed as a resize operation.
    resize_margin = Int(7)

    # Allow the left button begin a selection?
    left_button_selects = Bool(False)

    # Disable all left-mouse button interactions?
    disable_left_mouse = Bool(False)

    # Allow the tool to be put into the deselected state via mouse clicks
    allow_deselection = Bool(True)

    # The minimum span, in pixels, of a selection region.  Any attempt to
    # select a region smaller than this will be treated as a deselection.
    minimum_selection = Int(5)

    # The key which, if held down while the mouse is being dragged, will
    # indicate that the selection should be appended to an existing selection
    # as opposed to overwriting it.
    append_key = Instance(KeySpec, args=(None, "control"))

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # The value of the override plot to use, if any.  If None, then uses
    # self.component.
    _plot = Trait(None, Any)

    # The value of the override mapper to use, if any.  If None, then uses the
    # mapper on self.component.
    _mapper = Trait(None, Any)

    # Shadow trait for the **axis_index** property.
    _axis_index = Trait(None, None, Int)

    # The data space start and end coordinates of the selected region,
    # expressed as a list.
    _selection = Trait(None, None, Tuple, List, Array)

    # The selection in mask form.
    _selection_mask = Array

    # The end of the selection that is being actively modified by the mouse.
    _drag_edge = Enum("high", "low")

    #------------------------------------------------------------------------
    # These record the mouse position when the user is moving (not resizing)
    # the selection
    #------------------------------------------------------------------------

    # The position of the initial user click for moving the selection.
    _down_point = Array  # (x,y)

    # The data space coordinates of **_down_point**.
    _down_data_coord = Float

    # The original selection when the mouse went down to move the selection.
    _original_selection = Any

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def deselect(self, event=None):
        """ Deselects the highlighted region.

        This method essentially resets the tool. It takes the event causing the
        deselection as an optional argument.
        """
        self.selection = None
        self.selection_completed = None
        self.event_state = "normal"
        self.component.request_redraw()
        if event:
            event.window.set_pointer("arrow")
            event.handled = True
        return

    #------------------------------------------------------------------------
    # Event handlers for the "selected" event state
    #------------------------------------------------------------------------

    def selected_left_down(self, event):
        """ Handles the left mouse button being pressed when the tool is in
        the 'selected' state.

        If the user is allowed to resize the selection, and the event occurred
        within the resize margin of an endpoint, then the tool switches to the
        'selecting' state so that the user can resize the selection.

        If the event is within the bounds of the selection region, then the
        tool switches to the 'moving' states.

        Otherwise, the selection becomes deselected.
        """
        if self.disable_left_mouse:
            return

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
            self._down_data_coord = \
                self.mapper.map_data(self._down_point)[self.axis_index]
            self._original_selection = array(self.selection)
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
                #elif self.allow_deselection:
                #    self.deselect(event)
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
        """ Handles the mouse moving when the tool is in the 'selected' srate.

        If the user is allowed to resize the selection, and the event
        occurred within the resize margin of an endpoint, then the cursor
        changes to indicate that the selection could be resized.

        Otherwise, the cursor is set to an arrow.
        """
        if self.enable_resize:
            # Change the mouse cursor when the user moves within the
            # resize margin
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

    def selected_mouse_leave(self, event):
        """ Handles the mouse leaving the plot when the tool is in the
        'selected' state.

        Sets the cursor to an arrow.
        """
        event.window.set_pointer("arrow")
        return

    #------------------------------------------------------------------------
    # Event handlers for the "moving" event state
    #------------------------------------------------------------------------

    def moving_left_up(self, event):
        """ Handles the left mouse button coming up when the tool is in the
        'moving' state.

        Switches the tool to the 'selected' state.
        """
        if self.disable_left_mouse:
            return

        self.event_state = "selected"
        self.selection_completed = self.selection
        self._down_point = []
        event.handled = True
        return

    def moving_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'moving' state.

        Moves the selection range by an amount corresponding to the amount
        that the mouse has moved since its button was pressed. If the new
        selection range overlaps the endpoints of the data, it is truncated to
        that endpoint.
        """
        cur_point = array([event.x, event.y])
        cur_data_point = self.mapper.map_data(cur_point)[self.axis_index]
        original_selection = self._original_selection
        new_selection = original_selection + (cur_data_point -
                                              self._down_data_coord)
        selection_data_width = original_selection[1] - original_selection[0]

        range = self.mapper.range
        if min(new_selection) < range.low:
            new_selection = (range.low, range.low + selection_data_width)
        elif max(new_selection) > range.high:
            new_selection = (range.high - selection_data_width, range.high)

        self.selection = new_selection
        self.selection_completed = new_selection
        self.component.request_redraw()
        event.handled = True
        return

    def moving_mouse_leave(self, event):
        """ Handles the mouse leaving the plot while the tool is in the
        'moving' state.

        If the mouse was within the selection region when it left, the method
        does nothing.

        If the mouse was outside the selection region whe it left, the event is
        treated as moving the selection to the minimum or maximum.
        """
        axis_index = self.axis_index
        low = self.plot.position[axis_index]
        high = low + self.plot.bounds[axis_index] - 1

        pos = self._get_axis_coord(event)
        if pos >= low and pos <= high:
            # the mouse left but was within the mapping range, so don't do
            # anything
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
        """ Handles the left mouse button being pressed when the tool is in
        the 'normal' state.

        If the tool allows the left mouse button to start a selection, then
        it does so.
        """
        if self.left_button_selects:
            return self.normal_right_down(event)

    def normal_right_down(self, event):
        """ Handles the right mouse button being pressed when the tool is in
        the 'normal' state.

        Puts the tool into 'selecting' mode, changes the cursor to show that it
        is selecting, and starts defining the selection.

        """
        pos = self._get_axis_coord(event)
        mapped_pos = self.mapper.map_data(pos)
        self.selection = (mapped_pos, mapped_pos)
        self._set_sizing_cursor(event)
        self._down_point = array([event.x, event.y])
        self.event_state = "selecting"
        if self.append_key is not None and self.append_key.match(event):
            self.selection_mode = "append"
        else:
            self.selection_mode = "set"
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
            event.handled = True
        return

    def selecting_button_up(self, event):
        # Check to see if the selection region is bigger than the minimum
        event.window.set_pointer("arrow")

        end = self._get_axis_coord(event)

        if len(self._down_point) == 0:
            cancel_selection = False
        else:
            start = self._down_point[self.axis_index]
            self._down_point = []
            cancel_selection = self.minimum_selection > abs(start - end)

        if cancel_selection:
            self.deselect(event)
            event.handled = True
        else:
            self.event_state = "selected"

            # Fire the "completed" event
            self.selection_completed = self.selection
            event.handled = True
        return

    def selecting_right_up(self, event):
        """ Handles the right mouse button coming up when the tool is in the
        'selecting' state.

        Switches the tool to the 'selected' state and completes the selection.
        """
        self.selecting_button_up(event)

    def selecting_left_up(self, event):
        """ Handles the left mouse button coming up when the tool is in the
        'selecting' state.

        Switches the tool to the 'selected' state.
        """
        if self.disable_left_mouse:
            return
        self.selecting_button_up(event)

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
            selection_high = self.mapper.map_data(high)
        elif pos <= low:
            selection_low = self.mapper.map_data(low)

        self.selection = (selection_low, selection_high)
        event.window.set_pointer("arrow")
        self.component.request_redraw()
        return

    def selecting_mouse_enter(self, event):
        """ Handles the mouse entering the plot when the tool is in the
        'selecting' state.

        If the mouse does not have the right mouse button down, this event
        is treated as if the right mouse button was released. Otherwise,
        the method sets the cursor to show that it is selecting.
        """
        # If we were in the "selecting" state when the mouse left, and
        # the mouse has entered without a button being down,
        # then treat this like we got a button up event.
        if not (event.right_down or event.left_down):
            return self.selecting_button_up(event)
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
        selection = getattr(self.plot, self.axis).metadata[self.metadata_name]
        return selection

    def _set_selection(self, val):
        oldval = self._selection
        self._selection = val

        datasource = getattr(self.plot, self.axis, None)

        if datasource is not None:

            mdname = self.metadata_name

            # Set the selection range on the datasource
            datasource.metadata[mdname] = val
            datasource.metadata_changed = {mdname: val}

            # Set the selection mask on the datasource
            selection_masks = \
                datasource.metadata.setdefault(self.mask_metadata_name, [])
            for index in range(len(selection_masks)):
                if id(selection_masks[index]) == id(self._selection_mask):
                    del selection_masks[index]
                    break

            # Set the selection mode on the datasource
            datasource.metadata[self.selection_mode_metadata_name] = \
                      self.selection_mode

            if val is not None:
                low, high = val
                data_pts = datasource.get_data()
                new_mask = (data_pts >= low) & (data_pts <= high)
                selection_masks.append(new_mask)
                self._selection_mask = new_mask
            datasource.metadata_changed = {self.mask_metadata_name: val}

        self.trait_property_changed("selection", oldval, val)

        for l in self.listeners:
            if hasattr(l, "set_value_selection"):
                l.set_value_selection(val)

        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _get_selection_screencoords(self):
        """ Returns a tuple of (x1, x2) screen space coordinates of the start
        and end selection points.

        If there is no current selection, then it returns None.
        """
        selection = self.selection
        if selection is not None and len(selection) == 2:
            return self.mapper.map_screen(array(selection))
        else:
            return None

    def _set_sizing_cursor(self, event):
        """ Sets the correct cursor shape on the window of the event, given the
        tool's orientation and axis.
        """
        if self.axis_index == 0:
            # horizontal range selection, so use left/right arrow
            event.window.set_pointer("size left")
        else:
            # vertical range selection, so use up/down arrow
            event.window.set_pointer("size top")
        return

    def _get_axis_coord(self, event, axis="index"):
        """ Returns the coordinate of the event along the axis of interest
        to this tool (or along the orthogonal axis, if axis="value").
        """
        event_pos = (event.x, event.y)
        if axis == "index":
            return event_pos[self.axis_index]
        else:
            return event_pos[1 - self.axis_index]

    def _determine_axis(self):
        """ Determines whether the index of the coordinate along this tool's
        axis of interest is the first or second element of an (x,y) coordinate
        tuple.

        This method is only called if self._axis_index hasn't been set (or is
        None).
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
            self.plot.on_trait_change(self.__mapper_changed,
                                      old + "_mapper", remove=True)
        if new is not None:
            self.plot.on_trait_change(self.__mapper_changed,
                                      old + "_mapper", remove=True)
        return


# EOF
