
from numpy import linspace, pi, sin, tan

from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

from enthought.chaco2.chaco2_plot_container_editor import PlotContainerEditor
from enthought.chaco2.api import Plot, AbstractPlotData, ArrayPlotData
from enthought.chaco2.tools.api import PanTool, SimpleZoom


class TabbedPlots(HasTraits):

    data = Instance(AbstractPlotData)

    plot1 = Instance(Plot)
    plot2 = Instance(Plot)

    view = View(Group(
                   Item('plot1', editor=PlotContainerEditor(), 
                        dock='tab', show_label=False),
                   Item('plot2', editor=PlotContainerEditor(), 
                        dock='tab', show_label=False),
                   layout="tabbed"),
                width=800,
                height=600,
                resizable=True)
                


    def create_plots(self):
        p1 = Plot(self.data)
        p1.plot(("x", "y1"), name="sin plot", color="red")
        p1.tools.append(PanTool(p1))
        p1.overlays.append(SimpleZoom(p1))

        p2 = Plot(self.data)
        p2.plot(("x", "y2"), name="tan plot", color="blue")
        p2.tools.append(PanTool(p2))
        p2.overlays.append(SimpleZoom(p2))

        p2.index_range = p1.index_range

        self.plot1 = p1
        self.plot2 = p2

    def _data_changed(self):
        self.create_plots()


if __name__ == "__main__":
    obj = TabbedPlots()
    x = linspace(-2*pi, 2*pi, 100)
    obj.data = ArrayPlotData(x=x, y1=sin(x), y2=tan(x))
    obj.configure_traits()

