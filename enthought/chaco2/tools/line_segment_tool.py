""" Defines the LineSegmentTool class.
"""
# Major library imports
from numpy import array

# Enthought library imports
from enthought.traits.api import Any, Bool, Enum, Instance, Int, List, Trait, Tuple
from enthought.enable2.api import cursor_style_trait, Line

# Chaco imports
from enthought.chaco2.api import AbstractOverlay, PlotComponent



class LineSegmentTool(AbstractOverlay):
    """ The base class for tools that allow the user to draw a
    series of points connected by lines.
    """
    
    # The component that this tool overlays (overrides PlotComponent).
    component = Instance(PlotComponent)
    
    # The current line segment being drawn.
    line = Instance(Line, args=())
    
    # A list of the points in data space as (index,value)
    points = List
    
    # The event states are:
    #
    # normal: 
    #     The user may have selected points, and is moving the cursor around.
    # selecting: 
    #     The user has clicked down but hasn't let go of the button yet,
    #     and can still drag the point around.
    # dragging: 
    #     The user has clicked on an existing point and is dragging it
    #     around.  When the user releases the mouse button, the tool returns
    #     to the "normal" state
    event_state = Enum("normal", "selecting", "dragging")

    # The pixel distance from a vertex that is considered 'on' the vertex.
    proximity_distance = Int(4)

    # The data (index, value) position of the mouse cursor; this is used by various
    # draw() routines.
    mouse_position = Trait(None, None, Tuple)

    # The index of the vertex being dragged, if any.
    _dragged = Trait(None, None, Int)
    
    # Is the point being dragged is a newly placed point? This informs the 
    # "dragging" state about what to do if the user presses Escape while 
    # dragging.
    _drag_new_point = Bool(False)
    
    # The previous event state that the tool was in. This is used for states
    # that can be canceled (e.g., by pressing the Escape key), so that the
    # tool can revert to the correct state.
    _prev_event_state = Any

    # The cursor shapes to use for various modes
    
    # Cursor shape for non-tool use.
    original_cursor = cursor_style_trait("arrow")
    # Cursor shape for drawing.
    normal_cursor = cursor_style_trait("pencil")
    # Cursor shape for deleting points.
    delete_cursor = cursor_style_trait("bullseye")
    # Cursor shape for moving points.
    move_cursor = cursor_style_trait("sizing")



    #------------------------------------------------------------------------
    # Traits inherited from BaseTool
    #------------------------------------------------------------------------
    
    # How the tool draws on top of its component. Deprecated.
    draw_mode = "overlay"
    
    # The tool is initially invisible, because there is nothing to draw.
    visible = Bool(False)
    

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------
    
    def __init__(self, component=None, **kwtraits):
        if "component" in kwtraits:
            component = kwtraits["component"]
        super(LineSegmentTool, self).__init__(**kwtraits)
        self.component = component
        self.reset()
        self.line.line_dash = (4.0, 2.0)
        return
    
    #------------------------------------------------------------------------
    # Drawing tool methods
    #------------------------------------------------------------------------

    def reset(self):
        """ Resets the tool, throwing away any points, and making the tool
        invisible.
        """
        self.points = []
        self.event_state = "normal"
        self.visible = False
        self.request_redraw()
        return

    def _activate(self):
        """
        Called by a PlotComponent when this becomes the active tool.
        """
        pass

    def _deactivate(self, component=None):
        """
        Called by a PlotComponent when this is no longer the active tool.
        """
        self.reset()
        #self.component.window.set_pointer("arrow")
        return

    #------------------------------------------------------------------------
    # PointLine methods
    #------------------------------------------------------------------------
    
    def add_point(self, point):
        """ Given a screen-space *point* (x,y), adds the corresponding data
        space point to the list for this tool.
        """
        self.points.append(self._map_data(point))
        return
    
    def get_point(self, index):
        """ Retrieves the indexed point and returns its screen space value. 
        """
        return self._map_screen(self.points[index])
        
    def set_point(self, index, point):
        """ Sets the data-space *index* for a screen-space *point*.
        """
        self.points[index] = self._map_data(point)
        return
    
    def remove_point(self, index):
        """ Removes the point for a given *index* from this tool's list of 
        points.
        """
        del self.points[index]
        return

    #------------------------------------------------------------------------
    # "normal" state
    #------------------------------------------------------------------------

    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed while the tool is
        in the 'normal' state.
        
        For an existing point, if the user is pressing the Control key, the
        point is deleted. Otherwise, the user can drag the point.
        
        For a new point, the point is added, and the user can drag it.
        """
        # Determine if the user is dragging/deleting an existing point, or
        # creating a new one
        over = self._over_point(event, self.line.points)
        if over is not None:
            if event.control_down:
                # Delete the point
                self.points.pop(over)
                self.line.points = list(self.component.map_screen(array(self.points)))
                self.request_redraw()
            else:
                self.event_state = "dragging"
                self._dragged = over
                self._drag_new_point = False
                self.dragging_mouse_move(event)
        else:
            self.points.append(self._map_data((event.x, event.y)))
            self._dragged = -1
            self._drag_new_point = True
            self.visible = True
            self.event_state = "dragging"
            self.dragging_mouse_move(event)
        return

    def normal_mouse_move(self, event):
        """ Handles the user moving the mouse in the 'normal' state.
        
        When the user moves the cursor over an existing point, if the Control 
        key is pressed, the cursor changes to the **delete_cursor**, indicating
        that the point can be deleted. Otherwise, the cursor changes to the
        **move_cursor**, indicating that the point can be moved.
        
        When the user moves the cursor over any other point, the cursor
        changes to (or stays) the **normal_cursor**.
        """
        # If the user moves over an existing point, change the cursor to be the
        # move_cursor; otherwise, set it to the normal cursor
        over = self._over_point(event, self.line.points)
        if over is not None:
            if event.control_down:
                event.window.set_pointer(self.delete_cursor)
            else:
                event.window.set_pointer(self.move_cursor)
        else:
            event.handled = False
            event.window.set_pointer(self.normal_cursor)
        self.request_redraw()
        return
    
    def normal_draw(self, gc):
        """ Draws the line.
        """
        self.line.points = list(self.component.map_screen(array(self.points)))
        self.line._draw(gc)
        return
    
    def normal_key_pressed(self, event):
        """ Handles the user pressing a key in the 'normal' state.
        
        If the user presses the Enter key, the tool is reset.
        """
        if event.character == "Enter":
            self._finalize_selection()
            self.reset()
        return

    def normal_mouse_leave(self, event):
        """ Handles the user moving the cursor away from the tool area.
        """
        event.window.set_pointer("arrow")
        return
        
    #------------------------------------------------------------------------
    # "dragging" state
    #------------------------------------------------------------------------
    def dragging_mouse_move(self, event):
        """ Handles the user moving the mouse while in the 'dragging' state.
        
        The screen is updated to show the new mouse position as the end of the
        line segment being drawn.
        """
        mouse_position = self._map_data((event.x, event.y))
        self.points[self._dragged] = mouse_position
        self.line.points = list(self.component.map_screen(array(self.points)))
        self.request_redraw()
        return

    def dragging_draw(self, gc):
        """ Draws the polygon in the 'dragging' state. 
        """
        self.line._draw(gc)
        return

    def dragging_left_up(self, event):
        """ Handles the left mouse coming up in the 'dragging' state. 
        
        Switches to 'normal' state.
        """
        self.event_state = "normal"
        self._dragged = None
        self.updated = self
        return
    
    def dragging_key_pressed(self, event):
        """ Handles a key being pressed in the 'dragging' state.
        
        If the key is "Esc", the drag operation is canceled.
        """
        if event.character == "Esc":
            self._cancel_drag()
        return
    
    def dragging_mouse_leave(self, event):
        """ Handles the mouse leaving the tool area in the 'dragging' state.
        
        The drag is canceled and the cursor changes to an arrow.
        """
        self._cancel_drag()
        event.window.set_pointer("arrow")
        return

    def _cancel_drag(self):
        """ Cancels a drag operation.
        """
        if self._dragged != None:
            if self._drag_new_point:
                # Only remove the point if it was a newly-placed point
                self.points.pop(self._dragged)
            self._dragged = None
        self.mouse_position = None
        self.event_state = "normal"
        self.request_redraw()
        return

    #------------------------------------------------------------------------
    # override AbstractOverlay methods
    #------------------------------------------------------------------------

    def overlay(self, component, gc, view_bounds, mode="normal"):
        """ Draws this component overlaid on another component.
        
        Implements AbstractOverlay.
        """
        draw_func = getattr(self, self.event_state + "_draw", None)
        if draw_func:
            gc.save_state()
            gc.clip_to_rect(component.x, component.y, component.width-1, component.height-1)
            draw_func(gc)
            gc.restore_state()
        return
    
    def request_redraw(self):
        """ Requests that the component redraw itself. 
        
        Overrides Enable2 Component.
        """
        self.component.invalidate_draw()
        self.component.request_redraw()
        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _map_data(self, point):
        """ Maps values from screen space into data space.
        """
        index_mapper = self.component.index_mapper
        value_mapper = self.component.value_mapper
        if self.component.orientation == 'h':
            ndx = index_mapper.map_data(point[0])
            val = value_mapper.map_data(point[1])
        else:
            ndx = index_mapper.map_data(point[1])
            val = value_mapper.map_data(point[0])
        return (ndx, val)

    def _map_screen(self, point):
        """ Maps values from data space into screen space.
        """
        index_mapper = self.component.index_mapper
        value_mapper = self.component.value_mapper

        if self.component.orientation == 'h':
            x = index_mapper.map_screen(point[0])
            y = value_mapper.map_screen(point[1])
        else:
            y = index_mapper.map_screen(point[0])
            x = value_mapper.map_screen(point[1])
        return (x, y)

        
    def _is_near_point(self, point, event):
        """ Determines if the pointer is near a specified point. 
        """
        event_point = (event.x, event.y)
                
        return ((abs( point[0] - event_point[0] ) + \
                 abs( point[1] - event_point[1] )) <= self.proximity_distance)

    def _over_point(self, event, points):
        """ Return the index of a point in *points* that *event* is 'over'.

        Returns None if there is no such point.
        """
        for i, point in enumerate(points):
            if self._is_near_point(point, event):
                result = i
                break
        else:
            result = None
        return result

    def _finalize_selection(self):
        """
        Abstract method called to take action after the line selection is complete
        """
        pass

    #------------------------------------------------------------------------
    # Trait event handlers
    #------------------------------------------------------------------------
    
    def _component_changed(self, old, new):
        if new:
            self.container = new
        return


# EOF
