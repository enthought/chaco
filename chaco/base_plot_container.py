""" Defines the BasePlotContainer class.
"""
import warnings

# Enthought library imports
from enable.api import Container
from traits.api import Bool, Instance, Property, Str, Tuple

# Local, relative imports
from .plot_component import DEFAULT_DRAWING_ORDER, PlotComponent


class BasePlotContainer(Container):
    """
    A container for PlotComponents that conforms to being laid out by
    PlotFrames.  Serves as the base class for other PlotContainers.

    PlotContainers define a layout, i.e., a spatial relationship between
    their contained components.  (BasePlotContainer doesn't define one,
    but its various subclasses do.)

    BasePlotContainer is a subclass of Enable Container, so it is possible to
    insert Enable-level components into it.  However, because Enable
    components don't have the correct interfaces to participate in layout,
    the visual results will probably be incorrect.
    """

    # Redefine the container layers to name the main layer as "plot" instead
    # of the Enable default of "mainlayer"
    container_under_layers = Tuple("background", "image", "underlay", "plot")

    #------------------------------------------------------------------------
    # Duplicate trait declarations from PlotComponent.  We don't subclass
    # PlotComponent to avoid MRO complications with trait handlers and property
    # getters/setters.
    #------------------------------------------------------------------------

    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))
    draw_layer = Str("plot")

    #------------------------------------------------------------------------
    # Deprecated traits
    #------------------------------------------------------------------------

    # Deprecated flag to indicate that a component needed to do old-style
    # drawing.  Unused by any recent Chaco component.
    use_draw_order = Bool(True)

    # Deprecated property for accessing the components in the container.
    plot_components = Property

    def _get_plot_components(self):
        warnings.warn("Use of plot_components attribute deprecated." \
                      "Use components attribute instead.", DeprecationWarning)
        return self._components

    def _set_plot_components(self, new):
        warnings.warn("Use of plot_components attribute deprecated." \
                      "Use components attribute instead.", DeprecationWarning)
        self._components = new

    def _use_draw_order_changed(self, old, new):
        """ Handler to catch the case when someone is trying to use the
        old-style drawing mechanism, which is now unsupported.
        """
        if new == False:
            raise RuntimeError("The old-style drawing mechanism is no longer " \
                    "supported in Chaco.")

# EOF
