# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the HighlightTool class.
"""
# Major library imports
from numpy import ones

# Enthought library imports
from traits.api import Enum, Float, Str
from enable.api import BaseTool

# Chaco imports
from chaco.base_plot_container import BasePlotContainer


class HighlightTool(BaseTool):
    """A tool that enables the user to select a plot to be highlighted on the
    graph by clicking on it.
    """

    #: The name of the data source metadata which controls selections.
    metadata_name = Str("selections")

    #: The mouse button that initiates the selection.
    drag_button = Enum("left", "right")

    #: Threshold distance for hit-testing.
    threshold = Float(20.0)

    # ---------------------------------------------------------------------
    # Inherited BaseTool traits
    # ---------------------------------------------------------------------

    #: This tool is not drawn. Overrides BaseTool.
    draw_mode = "none"

    #: This tool is not visible. Overrides BaseTool.
    visible = False

    def normal_left_down(self, event):
        """Handles the left mouse button being pressed.

        If the left mouse button initiates the selection, this method does so.
        """
        if self.drag_button == "left":
            self._highlight(event)

    def normal_right_down(self, event):
        """Handles the right mouse button being pressed.

        If the right mouse button initiates the selection, this method does so.
        """
        if self.drag_button == "right":
            self._highlight(event)

    def _highlight(self, event):
        if isinstance(self.component, BasePlotContainer):
            event.offset_xy(self.component.x, self.component.y)
            closest_plot = self._find_curve(self.component.components, event)
            if closest_plot:
                index = closest_plot.index
                index.metadata[self.metadata_name] = ones(
                    len(index.get_data()), dtype=bool
                )
                closest_plot.request_redraw()
            else:
                # If we are attached to a plot container, then we can deselect
                # all of the plots in the container
                for p in self.component.components:
                    if self.metadata_name in p.index.metadata:
                        del p.index.metadata[self.metadata_name]
                        p.request_redraw()
            event.pop()

        elif hasattr(self.component, "hittest"):
            hit_point = self.component.hittest(
                (event.x, event.y), self.threshold
            )
            index = self.component.index
            if hit_point is not None:
                index.metadata[self.metadata_name] = ones(
                    len(index.get_data()), dtype=bool
                )
                self.component.request_redraw()
            elif self.metadata_name in index.metadata:
                del index.metadata[self.metadata_name]
                self.component.request_redraw()

        event.handled = True

    def _find_curve(self, plots, event):
        # need to change to use distance - not just return first plot within threshold
        for p in plots:
            if hasattr(p, "hittest"):
                cpoint = p.hittest((event.x, event.y), self.threshold)
                if cpoint is not None:
                    return p
        return None
