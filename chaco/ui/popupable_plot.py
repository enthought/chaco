# Enthought library imports
from traits.api import List
from chaco.plot import Plot
from chaco.plot_containers import VPlotContainer
from chaco.tools.pan_tool import PanTool
from chaco.tools.zoom_tool import ZoomTool
from chaco.ui.plot_window import PlotWindow

from traitsui.wx.constants import WindowColor


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
        window.edit_traits(kind="live", parent=event.window.control)

    def plot(self, data, **kw):
        """Queue up the plot commands"""
        self.command_queue.append((data, kw))
        super(PopupablePlot, self).plot(data, **kw)
