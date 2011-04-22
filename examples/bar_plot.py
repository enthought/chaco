
# Major library imports
import numpy

# Enthought library imports
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View

# Chaco imports
from enthought.chaco.api import LabelAxis, Plot, ArrayPlotData

class DemoPlot(HasTraits):
    plot = Instance(Plot)
    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False))

    def __init__(self, index, series_a, series_b, series_c, **kw):
        super(DemoPlot, self).__init__(**kw)

        plot_data = ArrayPlotData(index=index)
        plot_data.set_data('series_a', series_a)
        plot_data.set_data('series_b', series_b)
        plot_data.set_data('series_c', series_c)
        self.plot = Plot(plot_data)
        self.plot.plot(('index', 'series_a'), type='bar', bar_width=0.8, color='auto')
        self.plot.plot(('index', 'series_b'), type='bar', bar_width=0.8, color='auto')
        self.plot.plot(('index', 'series_c'), type='bar', bar_width=0.8, color='auto')

        # set the plot's value range to 0, otherwise it may pad too much
        self.plot.value_range.low = 0

        # replace the index values with some nicer labels
        label_axis = LabelAxis(self.plot, orientation='bottom',
                               title='Months',
                               positions = range(1, 10),
                               labels = ['jan', 'feb', 'march', 'april', 'may'],
                               small_haxis_style=True)

        self.plot.underlays.remove(self.plot.index_axis)
        self.plot.index_axis = label_axis
        self.plot.underlays.append(label_axis)


index = numpy.array([1,2,3,4,5])

demo_plot = DemoPlot(index, index*10, index*5, index*2)
demo_plot.configure_traits()
