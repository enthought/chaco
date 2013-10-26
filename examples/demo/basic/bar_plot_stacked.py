"""
Simple example of a stacked bar chart
"""

# Major library imports
import numpy

# Enthought library imports
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import UItem, View

# Chaco imports
from chaco.api import LabelAxis, Plot, ArrayPlotData

class PlotExample(HasTraits):
    plot = Instance(Plot)
    traits_view = View(UItem('plot', editor=ComponentEditor()),
                       width=400, height=400, resizable=True, 
                      )

    def __init__(self, index, series_a, series_b, series_c, **kw):
        super(PlotExample, self).__init__(**kw)

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
                               positions = list(range(1, 10)),
                               labels = ['jan', 'feb', 'march', 'april', 'may'],
                               small_haxis_style=True)

        self.plot.underlays.remove(self.plot.index_axis)
        self.plot.index_axis = label_axis
        self.plot.underlays.append(label_axis)


index = numpy.array([1,2,3,4,5])
demo = PlotExample(index, index*10, index*5, index*2)

if __name__ == "__main__":
    demo.configure_traits()
