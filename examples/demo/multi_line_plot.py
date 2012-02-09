import numpy as np

from chaco.api import LinearMapper, Plot, ArrayDataSource, DataRange1D
from chaco.multi_array_data_source import MultiArrayDataSource
from chaco.multi_line_plot import MultiLinePlot
from enable.api import ComponentEditor
from traits.api import Instance, HasTraits
from traitsui.api import View, UItem

class MyPlot(HasTraits):
    """ Displays a plot with a few buttons to control which overlay
        to display
    """
    plot = Instance(Plot)

    traits_view = View(UItem('plot', editor=ComponentEditor()),
                       width=700, height=600, resizable=True
                       )

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
                        global_max = np.nanmax(data),
                        global_min = np.nanmin(data),
                        **kw)

        self.plot = Plot()
        self.plot.add(mlp)


x_index = np.arange(0,100, 1)
y_index = np.arange(0,1000, 10)
data = np.sin(np.arange(0,x_index.size*y_index.size))
# add a random chunk of nan values
data[1532:1588] = np.nan
data = data.reshape(x_index.size, y_index.size)

my_plot = MyPlot(x_index, y_index, data)
my_plot.configure_traits()
