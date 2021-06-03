# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Abstract base class for plot decorators and overlays.

This class is primarily used so that tools can easily distinguish between
data-related plot items and the decorators on them.
"""

from enable.api import Component
from traits.api import Instance

from .plot_component import PlotComponent


class AbstractOverlay(PlotComponent):
    """The base class for overlays and underlays of the plot area.

    The only default additional feature of an overlay is that it implements
    an overlay() drawing method that overlays this component on top of
    another, without the components necessarily having an object
    containment-ownership relationship.
    """

    #: The component that this object overlays. This can be None. By default, if
    #: this object is called to draw(), it tries to render onto this component.
    component = Instance(Component)

    #: The default layer that this component draws into.
    draw_layer = "overlay"

    #: The background color (overrides PlotComponent).
    #: Typically, an overlay does not render a background.
    bgcolor = "transparent"

    def __init__(self, component=None, *args, **kw):
        if component is not None:
            self.component = component
        super().__init__(*args, **kw)

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        """Draws this component overlaid on another component."""
        pass

    def _draw(self, gc, view_bounds=None, mode="normal"):
        """Draws the component, paying attention to **draw_order**.  If the
        overlay has a non-null .component, then renders as an overlay;
        otherwise, default to the standard PlotComponent behavior.

        Overrides PlotComponent.
        """
        if self.component is not None:
            self.overlay(self.component, gc, view_bounds, mode)
        else:
            super()._draw(gc, view_bounds, mode)

    def _request_redraw(self):
        """Overrides Enable Component."""
        if self.component is not None:
            self.component.request_redraw()
        super()._request_redraw()
