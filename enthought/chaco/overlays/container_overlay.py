""" Abstract base class for plot decorators and overlays.

This class is primarily used so that tools can easily distinguish between 
data-related plot items and the decorators on them.
"""

from enthought.traits.api import Instance
from enthought.enable.api import Container, Component
from enthought.chaco.api import PlotComponent


class ContainerOverlay(Container, PlotComponent):
    """ This is an overlay which draws arbitrary Enable components
    inside it.
    """

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
        """ Overrides Enable Component.
        """
        if self.component is not None:
            #self.component.invalidate_draw([self.bounds])
            self.component.request_redraw()
        super(ContainerOverlay, self)._request_redraw()
