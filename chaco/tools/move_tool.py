""" Defines the MoveTool class.
"""
# Enthought library imports
from traits.api import Tuple
from enable.tools.api import DragTool


class MoveTool(DragTool):
    """A tool for moving a plot component."""

    # The (x,y) offset of the start of the drag relative to the component.
    _offset = Tuple((0, 0))

    def drag_start(self, event):
        """Called when the drag operation starts.

        Implements DragTool.
        """
        self._offset = (event.x - self.component.x, event.y - self.component.y)
        event.handled = True

    def dragging(self, event):
        """This method is called for every mouse_move event that the tool
        receives while the user is dragging the mouse.

        Implements DragTool. Moves the component.
        """
        c = self.component
        c.position = [event.x - self._offset[0], event.y - self._offset[1]]
        if getattr(c, "x_mapper", None):
            c.x_mapper.updated = True
        if getattr(c, "y_mapper", None):
            c.y_mapper.updated = True
        if getattr(c, "vgrid", None):
            c.vgrid.invalidate()
        if getattr(c, "hgrid", None):
            c.hgrid.invalidate()
        event.handled = True
        c.request_redraw()
