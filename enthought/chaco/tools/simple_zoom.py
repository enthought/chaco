""" Defines the SimpleZoom class.
"""
from numpy import array

# Enthought library imports
from enthought.enable.api import ColorTrait, KeySpec
from enthought.traits.api \
    import Bool, Enum, Float, Instance, Int, Str, Trait, Tuple

# Chaco imports
from enthought.chaco.api import AbstractOverlay
from base_zoom_tool import BaseZoomTool
from tool_history_mixin import ToolHistoryMixin

class SimpleZoom(AbstractOverlay, ToolHistoryMixin, BaseZoomTool):
    """ Selects a range along the index or value axis.
    
    The user left-click-drags to select a region to zoom in. 
    Certain keyboard keys are mapped to performing zoom actions as well.
    
    Implements a basic "zoom stack" so the user move go backwards and forwards
    through previous zoom regions.
    """
    
    # The selection mode:
    #
    # range:
    #   Select a range across a single index or value axis.
    # box:
    #   Perform a "box" selection on two axes.
    tool_mode = Enum("box", "range")
    
    # Is the tool always "on"? If True, left-clicking always initiates
    # a zoom operation; if False, the user must press a key to enter zoom mode.
    always_on = Bool(False)
    
    #-------------------------------------------------------------------------
    # Zoom control
    #-------------------------------------------------------------------------
    
    # The axis to which the selection made by this tool is perpendicular. This
    # only applies in 'range' mode.
    axis = Enum("index", "value")
    
    #-------------------------------------------------------------------------
    # Interaction control
    #-------------------------------------------------------------------------
    
    # Enable the mousewheel for zooming?
    enable_wheel = Bool(True)
    
    # The mouse button that initiates the drag.  If "None", then the tool
    # will not respond to drag.  (It can still respond to mousewheel events.)
    drag_button = Enum("left", "right", None)
    
    # Conversion ratio from wheel steps to zoom factors.
    wheel_zoom_step = Float(1.0)
    
    # The key press to enter zoom mode, if **always_on** is False.  Has no effect
    # if **always_on** is True.
    enter_zoom_key = Instance(KeySpec, args=("z",))
    
    # The key press to leave zoom mode, if **always_on** is False.  Has no effect
    # if **always_on** is True.
    exit_zoom_key = Instance(KeySpec, args=("z",))
    
    # Disable the tool after the zoom is completed?
    disable_on_complete = Bool(True)
    
    # The minimum amount of screen space the user must select in order for
    # the tool to actually take effect.
    minimum_screen_delta = Int(10)
    
    #-------------------------------------------------------------------------
    # Appearance properties (for Box mode)
    #-------------------------------------------------------------------------
    
    # The pointer to use when drawing a zoom box.
    pointer = "magnifier"
    
    # The color of the selection box.
    color = ColorTrait("lightskyblue")
    
    # The alpha value to apply to **color** when filling in the selection
    # region.  Because it is almost certainly useless to have an opaque zoom
    # rectangle, but it's also extremely useful to be able to use the normal
    # named colors from Enable, this attribute allows the specification of a
    # separate alpha value that replaces the alpha value of **color** at draw
    # time.
    alpha = Trait(0.4, None, Float)
    
    # The color of the outside selection rectangle.
    border_color = ColorTrait("dodgerblue")
    
    # The thickness of selection rectangle border.
    border_size = Int(1)
    
    # The possible event states of this zoom tool.
    event_state = Enum("normal", "selecting")
       
    #------------------------------------------------------------------------
    # Key mappings
    #------------------------------------------------------------------------
    
    # The key that cancels the zoom and resets the view to the original defaults.
    cancel_zoom_key = Instance(KeySpec, args=("Esc",))

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # If **always_on** is False, this attribute indicates whether the tool
    # is currently enabled.
    _enabled = Bool(False)

    # the original numerical screen ranges
    _orig_low_setting = Trait(None, Tuple, Float, Str)
    _orig_high_setting = Trait(None, Tuple, Float, Str)

    # The (x,y) screen point where the mouse went down.
    _screen_start = Trait(None, None, Tuple)

    # The (x,,y) screen point of the last seen mouse move event.
    _screen_end = Trait(None, None, Tuple)

    def __init__(self, component=None, *args, **kw):
        # Support AbstractController-style constructors so that this can be
        # handed in the component it will be overlaying in the constructor
        # without using kwargs.
        self.component = component
        super(SimpleZoom, self).__init__(*args, **kw)
        self._reset_state_to_current()
        if self.tool_mode == "range":
            mapper = self._get_mapper()
            self._orig_low_setting = mapper.range.low_setting
            self._orig_high_setting = mapper.range.high_setting
        else:
            x_range = self.component.x_mapper.range
            y_range = self.component.y_mapper.range
            self._orig_low_setting = (x_range.low_setting, y_range.low_setting)
            self._orig_high_setting = \
                (x_range.high_setting, y_range.high_setting)
        component.on_trait_change(self._reset_state_to_current,
                                  "index_data_changed")
        return

    def enable(self, event=None):
        """ Provides a programmatic way to enable this tool, if
        **always_on** is False. 
        
        Calling this method has the same effect as if the user pressed the
        **enter_zoom_key**.
        """
        if self.component.active_tool != self:
            self.component.active_tool = self
        self._enabled = True
        if event and event.window:
            event.window.set_pointer(self.pointer)
        return

    def disable(self, event=None):
        """ Provides a programmatic way to enable this tool, if **always_on**
        is False. 
        
        Calling this method has the same effect as if the user pressed the
        **exit_zoom_key**.
        """
        self.reset()
        self._enabled = False
        if self.component.active_tool == self:
            self.component.active_tool = None
        if event and event.window:
            event.window.set_pointer("arrow")
        return

    def reset(self, event=None):
        """ Resets the tool to normal state, with no start or end position.
        """
        self.event_state = "normal"
        self._screen_start = None
        self._screen_end = None

    def deactivate(self, component):
        """ Called when this is no longer the active tool.
        """
        # Required as part of the AbstractController interface.
        return self.disable()

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.
        
        Overrides AbstractOverlay.
        """
        if self.event_state == "selecting":
            if self.tool_mode == "range":
                self.overlay_range(component, gc)
            else:
                self.overlay_box(component, gc)
        return

    def overlay_box(self, component, gc):
        """ Draws the overlay as a box.
        """
        if self._screen_start and self._screen_end:
            gc.save_state()
            try:
                gc.set_antialias(0)
                gc.set_line_width(self.border_size)
                gc.set_stroke_color(self.border_color_)
                gc.clip_to_rect(component.x, component.y, component.width, component.height)
                x, y = self._screen_start
                x2, y2 = self._screen_end
                rect = (x, y, x2-x+1, y2-y+1)
                if self.color != "transparent":
                    if self.alpha:
                        color = list(self.color_)
                        if len(color) == 4:
                            color[3] = self.alpha
                        else:
                            color += [self.alpha]
                    else:
                        color = self.color_
                    gc.set_fill_color(color)
                    gc.rect(*rect)
                    gc.draw_path()
                else:
                    gc.rect(*rect)
                    gc.stroke_path()
            finally:
                gc.restore_state()
        return

    def overlay_range(self, component, gc):
        """ Draws the overlay as a range.
        """
        axis_ndx = self._determine_axis()
        lower_left = [0,0]
        upper_right = [0,0]
        lower_left[axis_ndx] = self._screen_start[axis_ndx]
        lower_left[1-axis_ndx] = self.component.position[1-axis_ndx]
        upper_right[axis_ndx] = self._screen_end[axis_ndx] - self._screen_start[axis_ndx]
        upper_right[1-axis_ndx] = self.component.bounds[1-axis_ndx]
       
        gc.save_state()
        try:
            gc.set_antialias(0)
            gc.set_alpha(self.alpha)
            gc.set_fill_color(self.color_)
            gc.set_stroke_color(self.border_color_)
            gc.clip_to_rect(component.x, component.y, component.width, component.height)
            gc.rect(lower_left[0], lower_left[1], upper_right[0], upper_right[1])
            gc.draw_path()
        finally:
            gc.restore_state()
        return

    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed while the tool is
        in the 'normal' state.
        
        If the tool is enabled or always on, it starts selecting.
        """
        if self.always_on or self._enabled:
            # we need to make sure that there isn't another active tool that we will
            # interfere with.
            if self.drag_button == "left":
                self._start_select(event)
        return

    def normal_right_down(self, event):
        """ Handles the right mouse button being pressed while the tool is
        in the 'normal' state.
        
        If the tool is enabled or always on, it starts selecting.
        """
        if self.always_on or self._enabled:
            if self.drag_button == "right":
                self._start_select(event)
        return

    def selecting_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'selecting' state.
        
        The selection is extended to the current mouse position.
        """
        self._screen_end = (event.x, event.y)
        self.component.request_redraw()
        event.handled = True
        return

    def selecting_left_up(self, event):
        """ Handles the left mouse button being released when the tool is in
        the 'selecting' state.
        
        Finishes selecting and does the zoom.
        """
        if self.drag_button == "left":
            self._end_select(event)
        return

    def selecting_right_up(self, event):
        """ Handles the right mouse button being released when the tool is in
        the 'selecting' state.
        
        Finishes selecting and does the zoom.
        """
        if self.drag_button == "right":
            self._end_select(event)
        return

    def selecting_mouse_leave(self, event):
        """ Handles the mouse leaving the plot when the tool is in the
        'selecting' state.
        
        Ends the selection operation without zooming.
        """
        self._end_selecting(event)
        return

    def selecting_key_pressed(self, event):
        """ Handles a key being pressed when the tool is in the 'selecting'
        state.
        
        If the key pressed is the **cancel_zoom_key**, then selecting is
        canceled.
        """
        if self.cancel_zoom_key.match(event):
            self._end_selecting(event)
            event.handled = True
        return

    def _start_select(self, event):
        """ Starts selecting the zoom region
        """
        if self.component.active_tool in (None, self):
            self.component.active_tool = self
        else:
            self._enabled = False
        self._screen_start = (event.x, event.y)
        self._screen_end = None
        self.event_state = "selecting"
        event.window.set_pointer(self.pointer)
        event.window.set_mouse_owner(self, event.net_transform())
        self.selecting_mouse_move(event)
        return

    def _end_select(self, event):
        """ Ends selection of the zoom region, adds the new zoom range to
        the zoom stack, and does the zoom.
        """
        self._screen_end = (event.x, event.y)
    
        start = array(self._screen_start)
        end = array(self._screen_end)
       
        if sum(abs(end - start)) < self.minimum_screen_delta:
            self._end_selecting(event)
            event.handled = True
            return
       
        if self.tool_mode == "range":
            mapper = self._get_mapper()
            axis = self._determine_axis()
            low = mapper.map_data(self._screen_start[axis])
            high = mapper.map_data(self._screen_end[axis])
           
            if low > high:
                low, high = high, low
        else:
            low, high = self._map_coordinate_box(self._screen_start, self._screen_end)
    
        new_zoom_range = (low, high)
        self._append_state(new_zoom_range)
        self._do_zoom()
        self._end_selecting(event)
        event.handled = True
        return

    def _end_selecting(self, event=None):
        """ Ends selection of zoom region, without zooming.
        """
        if self.disable_on_complete:
            self.disable(event)
        else:
            self.reset()
        self.component.request_redraw()
        if event and event.window.mouse_owner == self:
            event.window.set_mouse_owner(None)
        return

    def _do_zoom(self):
        """ Does the zoom operation.
        """
        # Sets the bounds on the component using _cur_stack_index
        low, high = self._current_state()
        orig_low, orig_high = self._history[0]
    
        if self._history_index == 0:
            if self.tool_mode == "range":
                mapper = self._get_mapper()
                mapper.range.low_setting = self._orig_low_setting
                mapper.range.high_setting = self._orig_high_setting
            else:
                x_range = self.component.x_mapper.range
                y_range = self.component.y_mapper.range
                x_range.low_setting, y_range.low_setting = \
                    self._orig_low_setting
                x_range.high_setting, y_range.high_setting = \
                    self._orig_high_setting

                # resetting the ranges will allow 'auto' to pick the values
                x_range.reset()
                y_range.reset()
               
        else:   
            if self.tool_mode == "range":
                mapper = self._get_mapper()
                if self._zoom_limit_reached(orig_low, orig_high, low, high, mapper):
                    self._pop_state()
                    return
                mapper.range.low = low
                mapper.range.high = high
            else:
                for ndx in (0, 1):
                    mapper = (self.component.x_mapper, self.component.y_mapper)[ndx]
                    if self._zoom_limit_reached(orig_low[ndx], orig_high[ndx],
                                                low[ndx], high[ndx], mapper):
                        # pop _current_state off the stack and leave the actual
                        # bounds unmodified.
                        self._pop_state()
                        return
                x_range = self.component.x_mapper.range
                y_range = self.component.y_mapper.range
                x_range.low, y_range.low = low
                x_range.high, y_range.high = high
                
        self.component.request_redraw()
        return

    def normal_key_pressed(self, event):
        """ Handles a key being pressed when the tool is in 'normal' state.
        
        If the tool is not always on, this method handles turning it on and
        off when the appropriate keys are pressed. Also handles keys to
        manipulate the tool history.
        """
        if not self.always_on:
            if not self._enabled and self.enter_zoom_key.match(event):
                if self.component.active_tool in (None, self):
                    self.component.active_tool = self
                    self._enabled = True
                    event.window.set_pointer(self.pointer)
                else:
                    self._enabled = False
                return
            elif self._enabled and self.exit_zoom_key.match(event):
                self._enabled = False
                event.window.set_pointer("arrow")
                return
           
        self._history_handle_key(event)
       
        if event.handled:
            self.component.request_redraw()
        return

    def normal_mouse_wheel(self, event):
        """ Handles the mouse wheel being used when the tool is in the 'normal'
        state.
        
        Scrolling the wheel "up" zooms in; scrolling it "down" zooms out.
        """
        if self.enable_wheel and event.mouse_wheel != 0:
            if event.mouse_wheel > 0:
                # zoom in
                zoom = 1.0 / (1.0 + 0.5 * self.wheel_zoom_step)
            elif event.mouse_wheel < 0:
                # zoom out
                zoom = 1.0 + 0.5 * self.wheel_zoom_step
           
            # We'll determine the current position of the cursor in screen coordinates,
            # and only afterwards map to dataspace.
            c = self.component
            screenlow_pt, screenhigh_pt = (c.x, c.y), (c.x2, c.y2)
            mouse_pos = (event.x, event.y)
    
            if self.tool_mode == "range":
                mapper_list = [(self._determine_axis(), self._get_mapper())]
            else:
                mapper_list = [(0, c.x_mapper), (1, c.y_mapper)]
           
            orig_low, orig_high = self._history[0]
           
            # If any of the axes reaches its zoom limit, we should cancel the zoom.
            # We should first calculate the new ranges and store them. If none of
            # the axes reach zoom limit, we can apply the new ranges.
            todo_list = []
            for ndx, mapper in mapper_list:
                screenrange = mapper.screen_bounds
                mouse_val = mouse_pos[ndx]
                newscreenlow = mouse_val + zoom * (screenlow_pt[ndx] - mouse_val)
                newscreenhigh = mouse_val + zoom * (screenhigh_pt[ndx] - mouse_val)
               
                newlow = mapper.map_data(newscreenlow)
                newhigh = mapper.map_data(newscreenhigh)
                               
                if type(orig_high) in (tuple,list):
                    ol, oh = orig_low[ndx], orig_high[ndx]
                else:
                    ol, oh = orig_low, orig_high
               
                if self._zoom_limit_reached(ol, oh, newlow, newhigh, mapper):
                    # Ignore other axes, we're done.
                    event.handled = True
                    return
                todo_list.append((mapper,newlow,newhigh))

            # Check the domain limits on each dimension, and rescale the zoom
            # amount if necessary. 
            for ndx, (mapper, newlow, newhigh) in enumerate(todo_list):
                domain_min, domain_max = getattr(mapper, "domain_limits", (None,None))
                if domain_min is not None and newlow < domain_min:
                    newlow = domain_min
                if domain_max is not None and newhigh > domain_max:
                    newhigh = domain_max
                todo_list[ndx] = (mapper, newlow, newhigh)

            # All axes can be rescaled, do it.
            for mapper, newlow, newhigh in todo_list:
                if newlow > newhigh:
                    newlow, newhigh = newhigh, newlow
                mapper.range.set_bounds(newlow, newhigh)
    
            event.handled = True
            c.request_redraw()
        return

    def _component_changed(self):
        if self._get_mapper() is not None:
            self._reset_state_to_current()
        return

    #------------------------------------------------------------------------
    # Implementation of PlotComponent interface
    #------------------------------------------------------------------------

    def _activate(self):
        """ Called by PlotComponent to set this as the active tool.
        """
        self.enable()
    
    #------------------------------------------------------------------------
    # implementations of abstract methods on ToolHistoryMixin
    #------------------------------------------------------------------------

    def _reset_state_to_current(self):
        """ Clears the tool history, and sets the current state to be the
        first state in the history.
        """
        if self.tool_mode == "range":
            mapper = self._get_mapper()
            if mapper is not None:
                self._reset_state((mapper.range.low,
                                   mapper.range.high))
        else:
            if self.component.x_mapper is not None:
                x_range = self.component.x_mapper.range
                xlow = x_range.low
                xhigh = x_range.high
            else:
                xlow = "auto"
                xhigh = "auto"

            if self.component.y_mapper is not None:
                y_range = self.component.y_mapper.range
                ylow = y_range.low
                yhigh = y_range.high
            else:
                ylow = "auto"
                yhigh = "auto"

            self._reset_state(((xlow, ylow),
                               (xhigh, yhigh)))

    def _reset_state_pressed(self):
        """ Called when the tool needs to reset its history. 
        
        The history index will have already been set to 0. Implements
        ToolHistoryMixin.
        """
        # First zoom to the set state (ZoomTool handles setting the index=0).
        self._do_zoom()
    
        # Now reset the state to the current bounds settings.
        self._reset_state_to_current()
        return

    def _prev_state_pressed(self):
        """ Called when the tool needs to advance to the previous state in the
        stack.
        
        The history index will have already been set to the index corresponding
        to the prev state. Implements ToolHistoryMixin.
        """
        self._do_zoom()
        return

    def _next_state_pressed(self):
        """ Called when the tool needs to advance to the next state in the stack.
        
        The history index will have already been set to the index corresponding
        to the next state. Implements ToolHistoryMixin.
        """
        self._do_zoom()
        return

    ### Persistence ###########################################################

    def __getstate__(self):
        dont_pickle = [
            'always_on',
            'enter_zoom_key',
            'exit_zoom_key',
            'minimum_screen_delta',
            'event_state',
            'reset_zoom_key',
            'prev_zoom_key',
            'next_zoom_key',
            'pointer',
            '_enabled',
            '_screen_start',
            '_screen_end']
        state = super(SimpleZoom,self).__getstate__()
        for key in dont_pickle:
            if state.has_key(key):
                del state[key]

        return state
    
