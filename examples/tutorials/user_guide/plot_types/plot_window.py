from chaco.api import PlotComponent
from chaco.data_view import DataView
from enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance
from traits.has_traits import on_trait_change
from traitsui.api import Item, View

class PlotWindow(HasTraits):

    plot = Instance(PlotComponent)

    @on_trait_change('plot')
    def _update_container(self):
        self.container = DataView(
            padding=(80,20,20,60),  # make some space for axis labels
            border_visible=False
        )
        self.container.add(self.plot)

    traits_view = View(Item('container',
                            editor=ComponentEditor(),
                            show_label=False),
                       width=600, height=400, resizable=True)
