import numpy
from enthought.chaco.api import Plot, ArrayPlotData
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, View

class MyPlot(HasTraits):
    plot = Instance(Plot)

    traits_view = View(Item('plot', editor=ComponentEditor()))

    def __init__(self, index, data_series, **kw):
        super(MyPlot, self).__init__(**kw)

        plot_data = ArrayPlotData(index=index)
        plot_data.set_data('data_series', data_series)
        self.plot = Plot(plot_data, origin='top left')
        self.plot.plot(('index', 'data_series'))
        
index = numpy.array([1,2,3,4,5])
data_series = index**2

my_plot = MyPlot(index, data_series)
my_plot.configure_traits()