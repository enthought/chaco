
# Enthought library imports
from enthought.traits.api import Enum, Tuple

# Chaco imports
from enthought.chaco2.api import AbstractController

# Local, relative imports
from drag_tool import DragTool

class MoveTool(DragTool):

    event_state = Enum("normal", "dragging")

    _offset = Tuple

    def drag_start(self, event):
        self._offset = (event.x - self.component.x, event.y - self.component.y)
        event.handled = True
    
    def dragging(self, event):
        c = self.component
        c.position = [event.x - self._offset[0], event.y - self._offset[1]]
        if hasattr(c, "x_mapper"):
            c.x_mapper.updated = True
        if hasattr(c, "y_mapper"):
            c.y_mapper.updated = True
        if getattr(c, "vgrid", None):
            c.vgrid.invalidate()
        if getattr(c, "hgrid", None):
            c.hgrid.invalidate()
        event.handled = True
        c.request_redraw()

