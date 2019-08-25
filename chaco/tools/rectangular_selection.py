#
# Enthought product code
#
# (C) Copyright 2019 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
import numpy as np

from chaco.tools.api import LassoSelection
from traits.api import ArrayOrNone


class RectangularSelection(LassoSelection):
    """ A lasso selection tool whose selection shape is rectangular
    """

    #: The first click. This represents a corner of the rectangle.
    first_corner = ArrayOrNone(shape=(2,))

    def selecting_mouse_move(self, event):
        """ This function is the same as the super except that it injects
        `_make_rectangle` as the `_active_selection` assignment.
        """
        # Translate the event's location to be relative to this container
        xform = self.component.get_event_transform(event)
        event.push_transform(xform, caller=self)
        new_point = self._map_data(np.array((event.x, event.y)))
        if self.first_corner is None:
            self.first_corner = new_point
        self._active_selection = self._make_rectangle(
            self.first_corner, new_point)
        self.updated = True
        if self.incremental_select:
            self._update_selection()
        # Report None for the previous selections
        self.trait_property_changed("disjoint_selections", None)

    def selecting_mouse_up(self, event):
        super().selecting_mouse_up(event)
        # Clear the first click
        self.first_corner = None

    def _make_rectangle(self, p1, p2):
        """ Makes an array that represents that path that follows the
        corner points of the rectangle with two corners p1 and p2:
            *-----p2
            |     |
            p1----*
        """
        return np.array([
            p1,
            [p1[0], p2[1]],
            p2,
            [p2[0], p1[1]]
        ])
