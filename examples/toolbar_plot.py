"""An example of a ToolbarPlot."""

import numpy

from enthought.chaco.plot import Plot, ArrayPlotData
from enthought.chaco.api import ToolbarPlot
from enthought.enable.api import ComponentEditor
from enthought.traits.api import Instance, HasTraits
from enthought.traits.ui.api import View, Item


class ExamplePlotApp(HasTraits):

    plot = Instance(Plot)

    traits_view = View(Item('plot', editor=ComponentEditor(),
                            width = 600, height = 600,
                            show_label=False),
                            resizable=True)

    def __init__(self, index, series, **kw):
        super(ExamplePlotApp, self).__init__(**kw)
        plot_data = ArrayPlotData(index=index)
        plot_data.set_data('series', series)

        self.plot = ToolbarPlot(plot_data)
        self.plot.plot(('index', 'series'), color='auto')

index = numpy.arange(0.1, 10., 0.01)
demo = ExamplePlotApp(index, (100.0 + index) / (100.0 - 20*index**2 + 5.0*index**4))

if __name__== '__main__':
    demo.configure_traits()
