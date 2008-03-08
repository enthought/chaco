""" Defines a the DragZoom tool class
"""

# Enthought library imports
from enthought.traits.api import Enum, Float, Tuple

# Chaco imports
from base_zoom_tool import BaseZoomTool
from drag_tool import DragTool


class DragZoom(DragTool, BaseZoomTool):
    """ A zoom tool that zooms continuously with a mouse drag movement, instead
    of using a zoom box or range.
    """

    # The mouse button that initiates the drag
    drag_button = Enum("left", "right")

    # Scaling factor on the zoom "speed".  A speed of 1.0 implies a zoom rate of
    # 5% for every 10 pixels.
    speed = Float(1.0)

    # The pointer to use when we're in the act of zooming
    drag_pointer = "magnifier"


    #------------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------------

    # (x,y) of the point where the mouse button was pressed.
    _original_xy = Tuple
    
    # Data coordinates of **_original_xy**.  This may be either (index,value)
    # or (value,index) depending on the component's orientation.
    _original_data = Tuple

    # A tuple of ((x,y), (x2,y2)) of the original, unzoomed screen bounds
    _orig_screen_bounds = Tuple

    # The y position of the previous mouse event.  The zoom rate is based on
    # the percentage change in position between the previous Y position and 
    # the current mouse position.
    _prev_y = Float

    def __init__(self, component=None, *args, **kw):
        super(DragZoom, self).__init__(component, *args, **kw)
        c = component
        if c is not None:
            self._orig_screen_bounds = ((c.x, c.y), (c.x2, c.y2))

    def dragging(self, event):

        # Compute the zoom amount based on the pixel difference between
        # the previous mouse event and the current one.
        clicked = event.y
        orig = self._prev_y
        zoom = 1.0 - self.speed * (clicked - orig) * (0.05/10)

        c = self.component
        low_pt, high_pt = self._map_coordinate_box((c.x, c.y), (c.x2, c.y2))

        # The original screen bounds are used to test if we've reached max_zoom
        orig_low, orig_high = self._orig_screen_bounds

        datarange_list = [(0, c.x_mapper.range), (1, c.y_mapper.range)]
        for ndx, datarange in datarange_list:
            mouse_val = self._original_data[ndx]
            newlow = mouse_val - zoom * (mouse_val - low_pt[ndx])
            newhigh = mouse_val + zoom * (high_pt[ndx] - mouse_val)
            
            ol, oh = orig_low[ndx], orig_high[ndx]
            if self._zoom_limit_reached(ol, oh, newlow, newhigh):
                event.handled = True
                return
            
            datarange.set_bounds(newlow, newhigh)
       
        self._prev_y = event.y
        event.handled = True
        self.component.request_redraw()
        return

    def drag_start(self, event, capture_mouse=True):
        self._original_xy = (event.x, event.y)
        c = self.component
        self._orig_screen_bounds = ((c.x,c.y), (c.x2,c.y2))
        self._original_data = (c.x_mapper.map_data(event.x), c.y_mapper.map_data(event.y))
        self._prev_y = event.y
        if capture_mouse:
            event.window.set_pointer(self.drag_pointer)
            event.window.set_mouse_owner(self, event.net_transform())
        event.handled = True
        return

    def drag_end(self, event):
        event.window.set_pointer("arrow")
        if event.window.mouse_owner == self:
            event.window.set_mouse_owner(None)
        event.handled = True
        return


