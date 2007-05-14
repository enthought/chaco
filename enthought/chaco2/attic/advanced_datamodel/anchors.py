#
#  This file is not used at the moment.  It just consists of the ramblings
#  of an insane man.   -- pzw 3/2/06
#

class Anchor(HasTraits):
    
    position = Property
    
    # The AlignmentGroup this anchor belongs to
    group = Instance("AnchorGroup")
    
    # Shadow trait for position
    _position = Float
    
    def align(self, anchor_or_element, A, B):
        """
        Pins this element's position to the position of the given anchor
        The relationship of this anchor's position relative to its
        group's position can be expressed as:
                self.position = A*group.position + B
        """
        if isinstance(anchor_or_element, AnchorGroup):
            self.group = anchor_or_element
            self.group.add(self)
        else:
            # Create a new anchor group
            self.group = AnchorGroup()
            self.position

    def unalign(self):
        """Removes this element from its anchor group"""
        pass

    def _get_position(self):
        pass
    
    def _set_position(self, pos):
        if self.group is not None:
            self.group.position = pos
        else:
            self._position = pos
        return


class AnchorGroup(Anchor):
    
    anchors = List(Anchor)

    def add(self, anchor):
        pass
    
    def remove(self, anchor):
        pass


class LayoutContext(HasTraits):

    anchors = List(Anchors)


class LayoutElement(HasTraits):
    
    frame = Instance(LayoutContext)
    

# EOF
