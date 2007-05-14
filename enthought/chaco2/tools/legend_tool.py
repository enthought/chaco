
# Major library imports
from numpy import array

# Enthought library imports
from enthought.traits.api import Array, Enum, false, true

# Local relative imports
from drag_tool import DragTool


class LegendTool(DragTool):
    """
    Tool for interacting with legends.
    The legend should be this tool's .component.
    """
    
    # Which mouse button initiates the drag
    drag_button = Enum("left", "right")
    
    # Whether or not to change the legend's .align property in accord with
    # the quadrant into which it was dropped.
    auto_align = true
    
    
    def is_draggable(self, x, y):
        if self.component:
            legend = self.component
            return (x >= legend.x and x <= legend.x2 and \
                    y >= legend.y and y <= legend.y2)
        else:
            return False
    
    
    def drag_start(self, event):
        if self.component:
            self.original_padding = self.component.padding
            event.window.set_mouse_owner(self, event.net_transform())
            event.handled = True
        return
    
    
    def dragging(self, event):
        # To properly move a legend (which aligns itself to a corner of its overlay
        # component), we need to modify the padding amounts as opposed to modifying
        # the position directly.
        if self.component:
            legend = self.component
            valign, halign = legend.align
            left, right, top, bottom = self.original_padding
            
            dy = int(event.y - self.mouse_down_position[1])
            if valign == "u":
                # we subtract dy because if the mouse moves downwards, dy is
                # negative but the top padding has increased
                legend.padding_top = top - dy
            else:
                legend.padding_bottom = bottom + dy
            
            dx = int(event.x - self.mouse_down_position[0])
            if halign == "r":
                legend.padding_right = right - dx
            else:
                legend.padding_left = left + dx
            
            event.handled = True
            legend.request_redraw()
        return


    def drag_end(self, event):
        if self.auto_align and self.component:
            # Determine which boundaries of the legend's overlaid component are
            # closest to the center of the legend
            legend = self.component
            component = legend.component
            
            left = int(legend.x - component.x)
            right = int(component.x2 - legend.x2)
            if left < right:
                halign = "l"
                legend.padding_left = left
            else:
                halign = "r"
                legend.padding_right = right
                
            bottom = int(legend.y - component.y)
            top = int(component.y2 - legend.y2)
            if bottom < top:
                valign = "l"
                legend.padding_bottom = bottom
            else:
                valign = "u"
                legend.padding_top = top
            
            legend.align = valign + halign
            if event.window.mouse_owner == self:
                event.window.set_mouse_owner(None)
            event.handled = True
            legend.request_redraw()
        return

# EOF
