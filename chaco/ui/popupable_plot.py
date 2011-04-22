# Enthought library imports
from traits.api import Instance, HasTraits, List
from traitsui.api import View, Item
from enable.api import Container
from enable.component_editor import ComponentEditor
from chaco.api import VPlotContainer
from chaco.plot import Plot
from chaco.tools.api import PanTool, ZoomTool

from traitsui.wx.constants import WindowColor

class PlotWindow(HasTraits):
    plot = Instance(Container)

    traits_view = View(Item('plot',
                            editor=ComponentEditor(),
                            height=300,
                            width=500,
                            show_label=False,
                            ),
                       title='Popup Chaco Plot',
                       resizable=True
                       )

class PopupablePlot(Plot):
    """A Plot class that pops up in a new window on double click"""
    # FIXME: It would be nice to queue up other types of commands and settings
    command_queue = List()

    def normal_left_dclick(self, event):
        plot = Plot(self.data)
        for data, kw in self.command_queue:
            plot.plot(data, **kw)
            plot.title = self.title

        plot.title = self.title
        container = VPlotContainer(bgcolor=WindowColor)
        container.add(plot)
        plot.tools.append(PanTool(plot))
        plot.overlays.append(ZoomTool(plot))
        window = PlotWindow(plot=container)
        window.edit_traits(kind='live', parent=event.window.control)

    def plot(self, data, **kw):
        """Queue up the plot commands"""
        self.command_queue.append((data, kw))
        super(PopupablePlot, self).plot(data, **kw)
        return


