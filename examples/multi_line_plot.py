import numpy

from enthought.chaco.api import LinearMapper, Plot, ArrayDataSource, DataRange1D
from enthought.chaco.multi_array_data_source import MultiArrayDataSource
from enthought.chaco.multi_line_plot import MultiLinePlot
from enthought.enable.api import ComponentEditor
from enthought.traits.api import Instance, HasTraits
from enthought.traits.ui.api import View, Item

class MyPlot(HasTraits):
    """ Displays a plot with a few buttons to control which overlay
        to display
    """
    plot = Instance(Plot)

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False),
                        resizable=True)

    def __init__(self, x_index, y_index, data, **kw):
        super(MyPlot, self).__init__(**kw)
        
        # Create the data source for the MultiLinePlot.
        ds = MultiArrayDataSource(data=data)
        
        xs = ArrayDataSource(x_index, sort_order='ascending')
        xrange = DataRange1D()
        xrange.add(xs)
        
        ys = ArrayDataSource(y_index, sort_order='ascending')
        yrange = DataRange1D()
        yrange.add(ys)
        
        mlp = MultiLinePlot(
                        index = xs,
                        yindex = ys,
                        index_mapper = LinearMapper(range=xrange),
                        value_mapper = LinearMapper(range=yrange),
                        value=ds,
                        global_max = data.max(),
                        global_min = data.min(),
                        **kw)
        
        self.plot = Plot()
        self.plot.add(mlp)
        
    
x_index = numpy.arange(0,100, 1)
y_index = numpy.arange(0,1000, 10)
data = numpy.sin(numpy.arange(0,x_index.size*y_index.size))
data = data.reshape(x_index.size, y_index.size)

my_plot = MyPlot(x_index, y_index, data)
my_plot.configure_traits()
