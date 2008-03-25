
from numpy import linspace, pi, sin, tan

from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Tabbed, View

from enthought.chaco2.chaco2_plot_container_editor import PlotContainerEditor
from enthought.chaco2.api import Plot, AbstractPlotData, ArrayPlotData
from enthought.chaco2.tools.api import PanTool, SimpleZoom


class TabbedPlots(HasTraits):

    data = Instance(AbstractPlotData)

    plot1 = Instance(Plot)
    plot2 = Instance(Plot)

    view = View(
        Tabbed(
            Item('plot1', editor=PlotContainerEditor(), dock='tab'),
            Item('plot2', editor=PlotContainerEditor(), dock='tab'),
            show_labels=False
        ),
        width=0.67,
        height=0.4,
        resizable=True
    )

    def create_plot(self, data, name, color):
        p = Plot(self.data)
        p.plot(data, name=name, color=color)
        p.tools.append(PanTool(p))
        p.overlays.append(SimpleZoom(p))
        return p

    def create_plots(self):
        self.plot1 = self.create_plot(("x", "y1"), "sin plot", "red")
        self.plot2 = self.create_plot(("x", "y2"), "tan plot", "blue")
        
        self.plot2.index_range = self.plot1.index_range

    def _data_changed(self):
        self.create_plots()


if __name__ == "__main__":
    x = linspace(-2*pi, 2*pi, 100)
    obj = TabbedPlots(data = ArrayPlotData(x=x, y1=sin(x), y2=tan(x)))
    obj.configure_traits()

