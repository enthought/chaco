# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from chaco.tools.select_tool import SelectTool
from traits.api import List

from .legend import Legend


class SelectableLegend(Legend, SelectTool):

    # A list of indices into self._cached_labels that indicates which labels
    # should be rendered in the "selected" style
    selections = List

    # A cached list of tuples (x,y,w,h) of each label's geometry
    _cached_label_dims = List

    # ------------------------------------------------------------------------
    # Legend methods
    # ------------------------------------------------------------------------

    def _do_layout(self):
        Legend._do_layout(self)
        self._compute_label_dims()

    def _compute_label_dims(self):
        dims = []
        edge_space = self.border_width + self.border_padding
        icon_width, icon_height = self.icon_bounds

        icon_x = self.x + edge_space
        text_x = icon_x + icon_width + self.icon_spacing
        y = self.y2 - edge_space
        for i, label_name in enumerate(self._cached_label_names):
            label_width, label_height = self._cached_label_sizes[i]
            y -= label_height
            icon_y = y + (label_height - icon_height) / 2
            dims.append(
                (
                    icon_x,
                    icon_y,
                    icon_width + self.icon_spacing + label_width,
                    label_height,
                )
            )
            y -= self.line_spacing
        self._cached_label_dims = dims

    # ------------------------------------------------------------------------
    # SelectTool interface
    # ------------------------------------------------------------------------

    def _get_selection_state(self, event):
        for ndx, dims in enumerate(self._cached_label_dims):
            x, y, w, h = dims
            if (x <= event.x <= x + w) and (y <= event.y <= y + h):
                return (ndx in self.selections), True
        else:
            if len(self._cached_label_dims) > 0:
                return (ndx in self.selections), False
            else:
                return False, False

    def _get_selection_token(self, event):
        for ndx, dims in enumerate(self._cached_label_dims):
            x, y, w, h = dims
            if (x <= event.x <= x + w) and (y <= event.y <= y + h):
                return ndx
        else:
            return None

    def _select(self, index, append=True):
        if append:
            self.selections.append(index)
        else:
            self.selections = [index]

    def _deselect(self, index=None):
        if index in self.selections:
            self.selections.remove(index)
