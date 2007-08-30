""" Defines the BasePlotContainer class.
"""
from sets import Set
from numpy import array
import warnings

# Enthought library imports
from enthought.enable2.api import Container, Interactor, black_color_trait, \
                            white_color_trait, color_table, empty_rectangle, \
                            intersect_bounds
from enthought.traits.api import Bool, Enum, List, Property, Tuple

# Local, relative imports
from plot_component import PlotComponent


class BasePlotContainer(PlotComponent, Container):
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

    plot_components = Property
    
    # Redefine the container layers to name the main layer as "plot" instead
    # of the Enable default of "mainlayer"
    container_under_layers = Tuple("background", "image", "underlay", "plot")

    #------------------------------------------------------------------------
    # Properties
    #------------------------------------------------------------------------

    def _get_plot_components(self):
        warnings.warn("Use of plot_components attribute deprecated. Use components attribute instead.")
        return self._components

    def _set_plot_components(self, new):
        warnings.warn("Use of plot_components attribute deprecated. Use components attribute instead.")
        self._components = new

      

# EOF
