import numpy as np

from traits.api import Instance, HasTraits, Range, Array, Float
from traitsui.api import View, Item, HGroup, VGroup, Group

from enable.api import ComponentEditor

from chaco.api import LinearMapper, Plot, ArrayDataSource, DataRange1D, PlotAxis
from chaco.multi_array_data_source import MultiArrayDataSource
from chaco.multi_line_plot import MultiLinePlot
from iris import *
from chaco.tools.api import RangeSelection, RangeSelectionOverlay


    
class ParallelAxis(HasTraits):
    """This is the X axis for the Parallel Cordinate Plot """

    # Name of the axis
    name = Str

    # Minimum of the Data
    data_min = Float(0)
    
    # Maximum of the Data
    data_max = Float(1)
    
    # Minimum of the Filter for this Axis
    filter_min  = Float(0,default=data_min)
    
    # Maximum of hte Filter for this Axis
    filter_max  = Float(1,default=data_max)
    
    location = Float(0)
    
    def catagorize(self,data):
        """ This will save a sorted unqiue list of data string and return
            and array of numeric values between 0 and 1 """
        self.cat_str = np.unique(data.copy())

        # scale is the max index
        scale = 1.0 * (len(self.cat_str) - 1)

        ret = np.zeros(len(data))
        for i in xrange(1,len(self.cat_str)):
            ret += (data == self.cat_str[i]) * i / scale            
        return ret
        
class ParallelCordinatePlot(HasTraits):
    """Demonstrates the ParallelCordinatePlot.

    """
    
    data = Array(depends_on='dataset')
    dataset = Array()

    plot = Instance(Plot)

    multi_line_plot_renderer = Instance(MultiLinePlot)
    
    x_axises = List(dtype=ParallelAxis)
    x_index = Array()
    y_index = Array()

    traits_view = \
        View(
            Group(
                Item('plot', editor=ComponentEditor(), show_label=False),
            ),
            width=800,
            height=500,
            resizable=True,
        )

    def data_default(self): data_source_change(self)
    def data_source_change(self):
        """ This will convert the structured array to a Normalized 2D Array """
        normalized = []
        x_axises = []
        for key in self.dataset.dtype.names:
            data = self.dataset[key]
            
            if(len(data) and type(data[0]) == type('')):
                new_axis = ParallelAxis(name = key, data_max = 1, data_min = 0)
                new_data = new_axis.catagorize(data)                
            else:
                new_axis = ParallelAxis(name = key, data_max = data.max(), data_min = data.min())
                new_data = (data - new_axis.data_min) / (new_axis.data_max - new_axis.data_min)
                assert(new_data.max() == 1)
                assert(new_data.min() == 0)
            normalized.append(new_data)
            x_axises.append(new_axis)
        # end for
        
        self.data = zip(*normalized)
        self.x_index = np.arange(len(normalized))
        self.y_index = np.zeros(len(self.dataset)) #linspace(0,1,len(self.dataset))
        
        
    #-----------------------------------------------------------------------
    # Trait defaults
    #-----------------------------------------------------------------------

    def _multi_line_plot_renderer_default(self):
        """Create the default MultiLinePlot instance."""

        xs = ArrayDataSource(self.x_index, sort_order='ascending')
        xrange = DataRange1D()
        xrange.add(xs)

        ys = ArrayDataSource(self.y_index, sort_order='ascending')
        yrange = DataRange1D()
        yrange.add(ys)
        yrange.low = 0
        yrange.high = 1

        # The data source for the MultiLinePlot.
        ds = MultiArrayDataSource(data=self.data)

        multi_line_plot_renderer = \
            MultiLinePlot(
                index = xs,
                yindex = ys,
                index_mapper = LinearMapper(range=xrange),
                value_mapper = LinearMapper(range=yrange),
                value=ds,
                scale = 2,
                normalized_amplitude = 1,
                global_max = 0,
                global_min = 1)

        return multi_line_plot_renderer

    def _plot_default(self):
        """Create the Plot instance."""

        plot = Plot(title="Parallel Cordinate Demo")
        plot.add(self.multi_line_plot_renderer)


        xs = ArrayDataSource(self.x_index)
        ys = ArrayDataSource(self.x_index)
        vals = MultiArrayDataSource(np.array([[x for x in self.x_index] \
                for y in self.x_index]))

        grid = MultiLinePlot(
            orientation='v',
            index=xs,
            yindex=ys,
            index_mapper=LinearMapper(range=DataRange1D(xs)),
            value_mapper=LinearMapper(range=DataRange1D(ys)),
            value=vals,
            global_max = 1000, ## Need to find max of `vals`
            global_min = 0
        )
        
        grid.active_tool = RangeSelection(grid, left_button_selects = True)
        grid.overlays.append(RangeSelectionOverlay(component=grid))
        plot.add(grid)
        
        return plot

    #-----------------------------------------------------------------------
    # Trait change handlers
    #-----------------------------------------------------------------------

    def _amplitude_changed(self, amp):
        self.multi_line_plot_renderer.normalized_amplitude = amp

    def _offset_changed(self, off):
        self.multi_line_plot_renderer.offset = off
        # FIXME:  The change does not trigger a redraw.  Force a redraw by
        # faking an amplitude change.
        self.multi_line_plot_renderer._amplitude_changed()


if __name__ == "__main__":
    dataset = IrisDataset(filename='iris.csv')
    iris_plot = ParallelCordinatePlot(dataset=dataset.data)
    iris_plot.data_source_change()
    iris_plot.configure_traits()

