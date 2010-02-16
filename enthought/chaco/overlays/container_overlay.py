"""Plot overlay which is an Enable Container

This module provides an Enable Container subclass which renders itself
into the overlay of a plot.  This allows the easy use of standard Enable
components in plot overlays.
"""

from enthought.traits.api import Instance
from enthought.enable.api import Container, Component
from enthought.chaco.api import PlotComponent


class ContainerOverlay(Container, PlotComponent):
    """ Container which is also a Chaco plot overlay

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
        super(ContainerOverlay, self)._request_redraw()
