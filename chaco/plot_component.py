""" Defines the PlotComponent class.
"""
# Enthought library imports
from enable.api import Component
from enable.kiva_graphics_context import GraphicsContext
from traits.api import Bool, Instance, observe, Str


DEFAULT_DRAWING_ORDER = [
    "background",
    "image",
    "underlay",
    "plot",
    "selection",
    "border",
    "annotation",
    "overlay",
]


class PlotComponent(Component):
    """
    PlotComponent is the base class for all plot-related visual components.
    It defines the various methods related to layout and tool handling,
    which virtually every subclass uses or needs to be aware of.

    Several of these top-level layout and draw methods have implementations
    that must not be overridden; instead, subclasses implement various
    protected stub methods.

    Additionally, this class sets up the machinery for having changes to
    specific traits trigger a call to the invalidate_and_redraw method (defined
    on the Component base class).  To use this, simply set the metadata
    requires_redraw=True in the definition of the trait.
    """

    # ------------------------------------------------------------------------
    # Rendering control traits
    # ------------------------------------------------------------------------

    #: The order in which various rendering classes on this component are drawn.
    #: Note that if this component is placed in a container, in most cases
    #: the container's draw order is used, since the container calls
    #: each of its contained components for each rendering pass.
    #: Typically, the definitions of the layers are:
    #:
    #: 1. 'background': Background image, shading
    #: 2. 'image': A special layer for plots that render as images.  This is in
    #:     a separate layer since these plots must all render before non-image
    #:     plots.
    #: 3. 'underlay': Axes and grids
    #: 4. 'plot': The main plot area itself
    #: 5. 'selection': Selected content are rendered above normal plot elements
    #:                 to make them stand out
    #: 6. 'border': Plot borders
    #: 7. 'annotation': Lines and text that are conceptually part of the "plot"
    #:    but need to be rendered on top of everything else in the plot
    #: 8. 'overlay': Legends, selection regions, and other tool-drawn visual
    #:    elements
    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))

    #: The default draw layer for Chaco plot components is the "plot" layer
    draw_layer = Str("plot")

    #: Draw layers in **draw_order**? If False, use _do_draw() (for backwards
    #: compatibility).
    use_draw_order = Bool(True)

    def _use_draw_order_changed(self, old, new):
        """Handler to catch the case when someone is trying to use the
        old-style drawing mechanism, which is now unsupported.
        """
        if new == False:
            raise RuntimeError(
                "The old-style drawing mechanism is no longer "
                "supported in Chaco."
            )

    @observe("+requires_redraw")
    def _plot_component_invalidated(self, event):
        self.invalidate_and_redraw()
