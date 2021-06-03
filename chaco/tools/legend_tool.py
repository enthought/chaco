# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the LegendTool class.
"""

# Enthought library imports
from traits.api import Bool, Enum
from enable.tools.api import DragTool


class LegendTool(DragTool):
    """A tool for interacting with legends.

    Attach this tool to a legend by setting the tool's **component**
    to the legend.
    """

    #: The mouse button that initiates the drag.
    drag_button = Enum("left", "right")

    #: Whether to change the legend's **align** property in accord with
    #: the quadrant into which it is dropped.
    auto_align = Bool(True)

    def is_draggable(self, x, y):
        """Returns whether the (x,y) position is in a region that is OK to
        drag.

        Overrides DragTool.
        """
        if self.component:
            legend = self.component
            return (
                x >= legend.x
                and x <= legend.x2
                and y >= legend.y
                and y <= legend.y2
            )
        else:
            return False

    def drag_start(self, event):
        """Called when the drag operation starts.

        Implements DragTool.
        """
        if self.component:
            self.original_padding = self.component.padding
            event.window.set_mouse_owner(self, event.net_transform())
            event.handled = True

    def dragging(self, event):
        """This method is called for every mouse_move event that the tool
        receives while the user is dragging the mouse.

        Implements DragTool. Moves the legend by aligning it to a corner of its
        overlay component.
        """
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

    def drag_end(self, event):
        """Called when a mouse event causes the drag operation to end.

        Implements DragTool.
        """
        # Make sure we have both a legend and that the legend is overlaying
        # a component
        if self.auto_align and self.component and self.component.component:
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
