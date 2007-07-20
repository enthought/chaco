""" Defines the base class for controllers.
"""
# Enthought library imports
from enthought.enable2.api import Interactor
from enthought.traits.api import false, Instance, true

# Relative imports
from plot_component import PlotComponent


class AbstractController(Interactor):
    """
    Abstract class for tools that manipulate PlotComponents. By default, a 
    controller attaches to a single PlotComponent.
    """
    
    component = Instance(PlotComponent)
    
    def __init__(self, component, *args, **kw):
        self.component = component
        super(AbstractController, self).__init__(*args, **kw)
        return
    
    def deactivate(self, component):
        """ This method is called by the component when this controller is no
        longer the active tool.
        """
        pass


# EOF
