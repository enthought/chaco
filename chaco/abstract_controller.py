""" Defines the base class for controllers.
"""
# Enthought library imports
from enable.api import Component, Interactor
from traits.api import Instance


class AbstractController(Interactor):
    """
    Abstract class for tools that manipulate PlotComponents. By default, a
    controller attaches to a single PlotComponent.
    """

    component = Instance(Component)

    def __init__(self, component, *args, **kw):
        self.component = component
        super().__init__(*args, **kw)

    def deactivate(self, component):
        """This method is called by the component when this controller is no
        longer the active tool.
        """
        pass
