from chaco.api import DataView, PlotComponent
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance, observe
from traitsui.api import Item, View


class PlotWindow(HasTraits):

    plot = Instance(PlotComponent)
    container = Instance(DataView)

    @observe("plot")
    def _update_container(self, event):
        self.container = DataView(
            padding=(80, 20, 20, 60),  # make some space for axis labels
            border_visible=False,
        )

        self.container.add(self.plot)
        self.container.aspect_ratio = self.plot.aspect_ratio

        # remove axes etc
        self.container.underlays = []

    traits_view = View(
        Item("container", editor=ComponentEditor(), show_label=False),
        width=600,
        height=400,
        resizable=True,
    )
