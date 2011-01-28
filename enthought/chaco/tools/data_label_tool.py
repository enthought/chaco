""" Defines the DataLabelTool class.
"""
# Major library imports
from numpy import array, asarray, argmin, sqrt

# Enthought library imports
from enthought.traits.api import Any, Bool, Enum
from enthought.enable.tools.drag_tool import DragTool


class DataLabelTool(DragTool):
    """ A tool for dragging a data label.

    Attach this tool to a DataLabel object by setting the tool's **component**
    to the DataLabel.
    """

    # The mouse button that initiates the drag.
    drag_button = Enum("left", "right")

    # Use the root of the label's arrow (if any) as the closest corner of the
    # label?
    auto_arrow_root = Bool(True)

    # The original position of the label with respect to the data point.
    _original_offset = Any

    # This is used in the auto_arrow_root = 'corners' case.
    _corner_names = ("bottom left", "bottom right", "top right", "top left",
                     "center", "center", "center", "center")

    def is_draggable(self, x, y):
        """ Returns whether the (x,y) position is in a region that is OK to
        drag.

        Overrides DragTool.
        """
        if self.component:
            label = self.component
            return (x >= label.x and x <= label.x2 and \
                    y >= label.y and y <= label.y2)
        else:
            return False


    def drag_start(self, event):
        """ Called when the drag operation starts.

        Implements DragTool.
        """
        if self.component:
            label = self.component
            pointx, pointy = label.component.map_screen(label.data_point)
            self._original_offset = (label.x - pointx, label.y - pointy)
            event.window.set_mouse_owner(self, event.net_transform())
            event.handled = True
        return


    def dragging(self, event):
        """ This method is called for every mouse_move event that the tool
        receives while the user is dragging the mouse.

        Implements DragTool. Moves and redraws the label.
        """
        if self.component:
            label = self.component
            dx = int(event.x - self.mouse_down_position[0])
            dy = int(event.y - self.mouse_down_position[1])

            label.label_position = (self._original_offset[0] + dx,
                                    self._original_offset[1] + dy)

            if self.auto_arrow_root:
                # Determine which corner is closest to the point
                p = asarray(label.component.map_screen(label.data_point))
                x, y = label.position
                x2 = label.x2
                y2 = label.y2
                xmid = (x+x2)/2
                ymid = (y+y2)/2
                anchors = array(((x, y), (x2, y), (x2, y2), (x, y2),
                                (xmid, y), (xmid, y2), (x, ymid), (x2, ymid)))
                diff = anchors - p
                closest = argmin(sqrt(map(sum, diff * diff)))
                label.arrow_root = self._corner_names[closest]

            event.handled = True
            label.request_redraw()
        return


    def drag_end(self, event):
        """ Called when a mouse event causes the drag operation to end.

        Implements DragTool.
        """
        if self.component:
            if event.window.mouse_owner == self:
                event.window.set_mouse_owner(None)
            event.handled = True
            self.component.request_redraw()
        return
