
from numpy import linspace, array, pi, cos

from traits.api import HasTraits, Instance
from traitsui.api import View, Item
from enable.api import ComponentEditor
from chaco.api import Plot, ArrayPlotData, GridMapper
from chaco.tools.api import PanTool, ZoomTool

from chaco.line_projection_plot import LineProjectionPlot
from chaco.base_projection import PolarProjection


class PolarPlotExample(HasTraits):

    plot_data = Instance(ArrayPlotData)
    
    plot = Instance(Plot)
    
    def _plot_data_default(self):
    
        # Create theta data
        numpoints = 5000
        low = 0
        high = 2*pi
        theta = linspace(low, high, numpoints)
    
        # Create the radius data
        radius = cos(3*theta)
        
        model = array([radius, theta]).T

        data = ArrayPlotData(
            model=model,
        )
    
        return data
    
    def _plot_default(self):
        print 'here 0'
        plot = Plot(self.plot_data)
        print 'here 1'
        
        model = plot._get_or_create_datasource('model')
        mapper = GridMapper(range=plot.range2d)
        print 'here'
        mapper.range.high = (1., 1.)
        mapper.range.low = (-1., -1.)
        print mapper._xmapper._null_data_range
        print mapper._xmapper.range.low, mapper._xmapper._scale, mapper._xmapper.low_pos
        projection = PolarProjection()
        
        print 'here 2'
        
        renderer = LineProjectionPlot(
            model=model,
            mapper=mapper,
            projection=projection,
        )
        plot.add(renderer)
        plot.plots['polar'] = [renderer]
        
        plot.tools = [PanTool(plot), ZoomTool(plot)]
        
        return plot
    
    
    traits_view = View(
        Item('plot', show_label=False, editor=ComponentEditor()),
        width=500, height=500,
        resizable=True
    )

if __name__ == '__main__':
    example = PolarPlotExample()
    example.configure_traits()