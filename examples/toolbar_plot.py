"""An example of a ToolbarPlot."""

import numpy

from enthought.chaco.plot import Plot, ArrayPlotData
from enthought.chaco.api import ToolbarPlot
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
        self.plot.plot(('index', 'series1'), color='auto')
        self.plot.plot(('index', 'series2'), color='auto')

index = numpy.arange(1.0, 10., 0.01)
series1 = (100.0 + index) / (100.0 - 20*index**2 + 5.0*index**4)
series2 = (100.0 + index) / (100.0 - 20*index**2 + 5.0*index**3)
demo = ExamplePlotApp(index, series1, series2)

if __name__== '__main__':
    demo.configure_traits()
