""" Abstract base class for plot decorators and overlays

Primarily used so that tools can easily distinguish between data-related
plot items and the decorators on them.
"""

from enthought.traits.api import Instance

from plot_component import PlotComponent


class AbstractOverlay(PlotComponent):
    """
    The base class for overlays and underlays of the plot area.  The only
    default additional feature of an overlay is that it should implement
    an overlay() drawing method that overlays this component on top of
    another, without their necessarily being an object containment/ownership
    relationship.
    """

    # The component that we overlay.  This can be None.  By default, if 
    # we are called to draw(), we will try to render onto this component.
    component = Instance(PlotComponent)
    
    # The default layer that this component draw into.
    draw_layer = "overlay"

    # Override the default background color, inherited from PlotComponent.
    # Typically, an overlay will not want to render a background.
    bgcolor = "transparent"

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        pass

    def _draw(self, gc, view_bounds=None, mode="normal"):
        if self.component is not None:
            self.overlay(self.component, gc, view_bounds, mode)
        return

    def _request_redraw(self):
        if self.component is not None:
            self.component.request_redraw()
        super(AbstractOverlay, self)._request_redraw()
        return

# EOF
