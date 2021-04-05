# Enthought library imports
from traits.api import Instance, HasTraits
from traitsui.api import View, Item
from enable.api import Container
from enable.component_editor import ComponentEditor


class PlotWindow(HasTraits):
    plot = Instance(Container)

    traits_view = View(
        Item(
            "plot",
            editor=ComponentEditor(),
            height=300,
            width=500,
            show_label=False,
        ),
        title="Chaco Plot",
        resizable=True,
    )
