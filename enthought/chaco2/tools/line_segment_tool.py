
# Major library imports
from numpy import array

# Enthought library imports
from enthought.traits.api import Any, Enum, false, Instance, Int, List, Trait, true, Tuple
from enthought.enable2.api import cursor_style_trait, Line

# Chaco imports
from enthought.chaco2.api import AbstractOverlay, PlotComponent



class LineSegmentTool(AbstractOverlay):
    """
    LineSegmentTool is the base class for tools that allow the user to draw a
    series of points connected by lines.
    """
    
    component = Instance(PlotComponent)
    
    line = Instance(Line, args=())
    
    # A list of the points in data space as (index,value)
    points = List
    
    # The event states are:
    #   normal: The user may have selected points, and is moving the cursor around
    #   selecting: The user has clicked down but hasn't let go of the button yet,
    #              and can still drag the point around.
    #   dragging: The user has clicked over an existing point and is dragging it
    #             around.  When the user releases the mouse button, we return
    #             to the "normal" state
    event_state = Enum("normal", "selecting", "dragging")

    # The pixel distance from a vertex that is considered 'on' the vertex.
    proximity_distance = Int(4)

    # The data (index, value) position of the mouse cursor; this is used by various
    # draw() routines.
    mouse_position = Trait(None, None, Tuple)

    # The index of the vertex being dragged, if any.
    _dragged = Trait(None, None, Int)
    
    # This indicates whether the point we are dragging is a newly placed point,
    # or an existing point.  This then informs the "dragging" state about what
    # to do when the user pressed Escape while dragging.
    _drag_new_point = false
    
    # Used by states that are "cancellable" (e.g. via the ESCape key) so that
    # we can revert to the correct previous state.
    _prev_event_state = Any

    # The cursor shapes to use for various modes
    original_cursor = cursor_style_trait("arrow")
    normal_cursor = cursor_style_trait("pencil")
    delete_cursor = cursor_style_trait("bullseye")
    move_cursor = cursor_style_trait("sizing")



    #------------------------------------------------------------------------
    # Traits inherited from BaseTool
    #------------------------------------------------------------------------
    
    # soon to be deprecated
    draw_mode = "overlay"
    
    # The tool is initially invisible, because there is nothing to draw
    visible = false
    

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
        self.points = []
        self.event_state = "normal"
        self.visible = False
        self.request_redraw()
        return

    def _activate(self):
        """
        Called by a PlotComponent when we become the active tool.
        """
        pass

    def _deactivate(self, component=None):
        """
        Called by a PlotComponent when we are no longer the active tool.
        """
        self.reset()
        #self.component.window.set_pointer("arrow")
        return

    #------------------------------------------------------------------------
    # PointLine methods
    #------------------------------------------------------------------------
    
    def add_point(self, point):
        """ Stores screen-space point (x,y) """
        self.points.append(self._map_data(point))
        return
    
    def get_point(self, index):
        """ Retrieves the indexed point and returns its screen space value """
        return self._map_screen(self.points[index])
        
    def set_point(self, index, point):
        self.points[index] = self._map_data(point)
        return
    
    def remove_point(self, index):
        del self.points[index]
        return

    #------------------------------------------------------------------------
    # "normal" state
    #------------------------------------------------------------------------

    def normal_left_down(self, event):
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
        self.line.points = list(self.component.map_screen(array(self.points)))
        self.line._draw(gc)
        return
    
    def normal_key_pressed(self, event):
        if event.character == "Enter":
            self._finalize_selection()
            self.reset()
        return

    def normal_mouse_leave(self, event):
        event.window.set_pointer("arrow")
        return
        
    #------------------------------------------------------------------------
    # "dragging" state
    #------------------------------------------------------------------------
    def dragging_mouse_move(self, event):
        mouse_position = self._map_data((event.x, event.y))
        self.points[self._dragged] = mouse_position
        self.line.points = list(self.component.map_screen(array(self.points)))
        self.request_redraw()
        return

    def dragging_draw(self, gc):
        """ Draw the polygon in the 'drag_point' state. """
        self.line._draw(gc)
        return

    def dragging_left_up(self, event):
        """ Handle the left mouse coming up in the 'drag_point' state. """
        self.event_state = "normal"
        self._dragged = None
        self.updated = self
        return
    
    def dragging_key_pressed(self, event):
        if event.character == "Esc":
            self._cancel_drag()
        return
    
    def dragging_mouse_leave(self, event):
        self._cancel_drag()
        event.window.set_pointer("arrow")
        return

    def _cancel_drag(self):
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
        draw_func = getattr(self, self.event_state + "_draw", None)
        if draw_func:
            gc.save_state()
            gc.clip_to_rect(component.x, component.y, component.width-1, component.height-1)
            draw_func(gc)
            gc.restore_state()
        return
    
    def request_redraw(self):
        self.component.invalidate_draw()
        self.component.request_redraw()
        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _map_data(self, point):
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
        """ Determine if the pointer is near a specified point. """
        event_point = (event.x, event.y)
                
        return ((abs( point[0] - event_point[0] ) + \
                 abs( point[1] - event_point[1] )) <= self.proximity_distance)

    def _over_point(self, event, points):
        """ Return the index of a point in points that event is 'over'.

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
