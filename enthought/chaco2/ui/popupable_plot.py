# Enthought library imports
from enthought.traits.api import Instance, HasTraits, List
from enthought.traits.ui.api import View, Item
from enthought.enable2.api import Container
from enthought.chaco2.api import VPlotContainer
from enthought.chaco2.plot import Plot
from enthought.chaco2.chaco2_plot_container_editor import PlotContainerEditor
from enthought.chaco2.tools.api import PanTool, SimpleZoom

from enthought.traits.ui.wx.constants import WindowColor

class PlotWindow(HasTraits):
    plot = Instance(Container)

    traits_view = View(Item('plot',
                            editor=PlotContainerEditor(),
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
        plot.overlays.append(SimpleZoom(plot))
        window = PlotWindow(plot=container)
        window.edit_traits(kind='live', parent=event.window.control)

    def plot(self, data, **kw):
        """Queue up the plot commands"""
        self.command_queue.append((data, kw))
        super(PopupablePlot, self).plot(data, **kw)
        return
                            
                            
