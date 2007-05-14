
# Enthought library imports
from enthought.enable2.api import Interactor
from enthought.traits.api import false, Instance, true

# Relative imports
from plot_component import PlotComponent


class AbstractController(Interactor):
    """
    Base class for tools that manipulate PlotComponents.  By default, it attaches
    to a single PlotComponent.
    """
    
    component = Instance(PlotComponent)
    
    def __init__(self, component, *args, **kw):
        self.component = component
        super(AbstractController, self).__init__(*args, **kw)
        return
    
    def deactivate(self, component):
        """
        Called by component when we have beeb removed as the active tool.
        """
        pass


# EOF
