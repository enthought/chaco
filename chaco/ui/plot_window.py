# Enthought library imports
from enthought.traits.api import Instance, HasTraits
from enthought.traits.ui.api import View, Item
from enthought.enable.api import Container
from enthought.enable.component_editor import ComponentEditor

class PlotWindow(HasTraits):
    plot = Instance(Container)

    traits_view = View(Item('plot',
                            editor=ComponentEditor(),
                            height=300,
                            width=500,
                            show_label=False,
                            ),
                       title='Chaco Plot',
                       resizable=True
                       )