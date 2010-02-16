
from enthought.enable.api import BaseTool, KeySpec
from enthought.traits.api import Str, Bool, Event, Tuple, Enum, Callable


class SimpleInspectorTool(BaseTool):
    """ This is a simple tool that reports the data-space coordinates of the
    current mouse cursor position in a plot.
    """

    # This event fires whenever the mouse moves over a new image point.
    # Its value is a dict with keys "index" and "value".
    new_value = Event

    # Indicates whether overlays listening to this tool should be visible.
    visible = Bool(True)

    # Stores the last mouse position.  This can be used by overlays to
    # position themselves around the mouse.
    last_mouse_position = Tuple

    # This key will show and hide any overlays listening to this tool.
    inspector_key = KeySpec('p')
    
    # A callable that computes other values for the new_value event
    # this takes a dictionary as an argument, and returns a dictionary
    value_generator = Callable
   
    # Stores the value of self.visible when the mouse leaves the tool,
    # so that it can be restored when the mouse enters again.
    _old_visible = Enum(None, True, False) #Trait(None, Bool(True))

    def normal_key_pressed(self, event):
        if self.inspector_key.match(event):
            self.visible = not self.visible

    def normal_mouse_leave(self, event):
        if self._old_visible is None:
            self._old_visible = self.visible
            self.visible = False

    def normal_mouse_enter(self, event):
        if self._old_visible is not None:
            self.visible = self._old_visible
            self._old_visible = None
    
    def normal_mouse_move(self, event):
        plot = self.component
        if plot is not None:
            self.gather_values(event)
            self.last_mouse_position = (event.x, event.y)

    def gather_values(self, event):
        x, y, index, value = self._map_to_data(event.x, event.y)
        d = {'index': index, 'value': value, 'x': x, 'y': y}
        if self.value_generator is not None:
            d = self.value_generator(d)
        self.new_value = d

    def _map_to_data(self, x, y):
        """ Returns the data space coordinates of the given x and y.  
        
        Takes into account orientation of the plot and the axis setting.
        """
        
        plot = self.component
        if plot.orientation == "h":
            index = x = plot.x_mapper.map_data(x)
            value = y = plot.y_mapper.map_data(y)
        else:
            index = y = plot.y_mapper.map_data(y)
            value = x = plot.x_mapper.map_data(x)
        return x, y, index, value
