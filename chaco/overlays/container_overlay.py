# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""Plot overlay which is an Enable Container

This module provides an Enable Container subclass which renders itself
into the overlay of a plot.  This allows the easy use of standard Enable
components in plot overlays.
"""

from traits.api import Instance
from enable.api import Container, Component
from chaco.plot_component import PlotComponent


class ContainerOverlay(Container, PlotComponent):
    """Container which is also a Chaco plot overlay

    Since this is an Enable container, any Components that it contains will
    be rendered into the overlay layer of the plot.
    """

    # XXX this works, but I'm not sure that it's quite right.

    # The component that this object overlays. This can be None. By default, if
    # this object is called to draw(), it tries to render onto this component.
    component = Instance(Component)

    draw_layer = "overlay"

    # The background color (overrides PlotComponent).
    # Typically, an overlay does not render a background.
    bgcolor = "transparent"

    unified_draw = True

    auto_size = True

    def overlay(self, other, gc, view_bounds, mode):
        self.draw(gc, view_bounds, mode)

    def _request_redraw(self):
        if self.component is not None:
            self.component.request_redraw()
        super()._request_redraw()
