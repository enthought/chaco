from enthought.traits.api import Enum, Any

from container_overlay import ContainerOverlay

class AlignedContainerOverlay(ContainerOverlay):
    
    # Alignment of the text in the box:
    #
    # * "ur": upper right
    # * "ul": upper left
    # * "ll": lower left
    # * "lr": lower right
    align = Enum("ur", "ul", "ll", "lr")

    # This allows subclasses to specify an alternate position for the root
    # of the text box.  Must be a sequence of length 2.
    alternate_position = Any

    def overlay(self, other, gc, view_bounds, mode):
        self._compute_position(other)
        self.draw(gc, view_bounds, mode)

    def _compute_position(self, component):
        """ Given the alignment and size of the overlay, position it.
        """
        if self.layout_needed:
            self.do_layout()
        valign, halign = self.align

        if self.alternate_position:
            x, y = self.alternate_position
            if valign == "u":
                self.outer_y = component.y + y
            else:
                self.outer_y2 = component.y + y

            if halign == "r":
                self.outer_x = component.x + x
            else:
                self.outer_x2 = component.x + x
        else:
            if valign == "u":
                self.outer_y2 = component.y2
            else:
                self.outer_y = component.y

            if halign == "r":
                self.outer_x2 = component.x2
            else:
                self.outer_x = component.x

            # attempt to get the box entirely within the component
            # (prefer expanding to top-right if we cover entire component)
            if self.x2 > component.x2:
                self.x2 = component.x2
            if self.y2 > component.y2:
                self.y2 = component.y2
            if self.x < component.x:
                self.x = component.x
            if self.y < component.y:
                self.y = component.y
