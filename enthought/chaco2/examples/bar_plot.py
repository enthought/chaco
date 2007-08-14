
# Major library imports
from numpy import arange, cos, linspace, pi, sin

from enthought.chaco2.example_support import DemoFrame, demo_main, COLOR_PALETTE

# Enthought library imports
from enthought.traits.api import HasTraits, Float, Int, Instance, Range,\
                             true, false
from enthought.enable2.traits.rgba_color_trait import RGBAColor
from enthought.traits.ui.api import View, Group, Item
from enthought.enable2.api import Window

# Chaco imports
from enthought.chaco2.api import ArrayDataSource, BarPlot, DataRange1D, LabelAxis, \
                                 LinearMapper, OverlayPlotContainer, PlotAxis, PlotGrid

def make_curves(spec):
    (index_points, value_points) = spec.get_points()
    size = len(index_points)

    # Create our data sources
    spec.index_source = idx = ArrayDataSource(index_points[:(size/2)])
    spec.value_source = vals = ArrayDataSource(value_points[:(size/2)], sort_order="none")

    idx2 = ArrayDataSource(index_points[(size/2):])
    vals2 = ArrayDataSource(value_points[(size/2):], sort_order="none")

    idx3 = ArrayDataSource(index_points)
    starting_vals = ArrayDataSource(value_points, sort_order="none")
    vals3 = ArrayDataSource(2 * cos(value_points) + 2, sort_order="none")

    # Create the index range
    index_range = DataRange1D(low=0.5, high=9.5)
    index_range.add(idx)
    index_mapper = LinearMapper(range=index_range)

    # Create the value range
    value_range = DataRange1D(low=0, high=4.25)
    #value_range.add(vals)
    value_mapper = LinearMapper(range=value_range)

    # Create the plot
    plot1 = BarPlot(index=idx, value=vals,
                    value_mapper=value_mapper,
                    index_mapper=index_mapper,
                    line_color='black',
                    fill_color=tuple(COLOR_PALETTE[6]),
                    bar_width=0.8, antialias=False)
    
    plot2 = BarPlot(index=idx2, value=vals2,
                    value_mapper=value_mapper,
                    index_mapper=index_mapper,
                    line_color='blue',
                    fill_color=tuple(COLOR_PALETTE[3]),
                    bar_width=0.8, antialias=False)
    
    plot3 = BarPlot(index=idx3, value=vals3,
                    value_mapper=value_mapper,
                    index_mapper=index_mapper,
                    starting_value=starting_vals,
                    line_color='black',
                    fill_color=tuple(COLOR_PALETTE[1]),
                    bar_width=0.8, antialias=False)

    return [plot1, plot2, plot3]

class PlotFrame(DemoFrame, HasTraits):
    index_source = Instance(ArrayDataSource)
    value_source = Instance(ArrayDataSource)

    line_color = RGBAColor('black')
    bg_color = RGBAColor('white')

    def get_points(self):
        index = linspace(pi/4, 3*pi/2, 9)
        data = sin(index) + 2
        return (range(1, 10), data)

    def _create_window(self):
        container = OverlayPlotContainer(bgcolor = "white")  # use_draw_order=False,
        
        self.container = container
        
        plots = make_curves(self)
        for plot in plots:
            plot.padding = 50
            container.add(plot)

        left_axis = PlotAxis(component=plot, orientation='left',
                             mapper=plot.value_mapper)

        bottom_axis = LabelAxis(component=plot, orientation='bottom',
                               title='Categories',
                               positions = range(1, 10),
                               labels = ['a', 'b', 'c', 'd', 'e',
                                         'f', 'g', 'h', 'i'],
                               small_haxis_style=True,
                               mapper=plot.index_mapper)

        plot.underlays.append(left_axis)
        plot.underlays.append(bottom_axis)
        
        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,600), title="Bar plot")
