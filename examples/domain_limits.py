import numpy

from enthought.chaco.plot import Plot, ArrayPlotData
from enthought.chaco.api import ToolbarPlot
from enthought.chaco.tools.api import PanTool, ZoomTool
from enthought.enable.api import ComponentEditor
from traits.api import Instance, HasTraits
from traitsui.api import View, Item


class ExamplePlotApp(HasTraits):

    plot = Instance(Plot)

    traits_view = View(Item('plot', editor=ComponentEditor(),
                            width = 600, height = 600,
                            show_label=False),
                            resizable=True)

    def __init__(self, index, series1, series2, **kw):
        super(ExamplePlotApp, self).__init__(**kw)
        plot_data = ArrayPlotData(index=index)
        plot_data.set_data('series1', series1)
        plot_data.set_data('series2', series2)

        self.plot = ToolbarPlot(plot_data)
        line_plot = self.plot.plot(('index', 'series1'), color='auto')[0]

        # Add pan and zoom tools
        line_plot.tools.append(PanTool(line_plot))
        line_plot.tools.append(ZoomTool(line_plot))

        # Set the domain_limits
        line_plot.index_mapper.domain_limits = (3.3, 6.6)

index = numpy.arange(1.0, 10., 0.01)
series1 = (100.0 + index) / (100.0 - 20*index**2 + 5.0*index**4)
series2 = (100.0 + index) / (100.0 - 20*index**2 + 5.0*index**3)
demo = ExamplePlotApp(index, series1, series2)

if __name__== '__main__':
    demo.configure_traits()
