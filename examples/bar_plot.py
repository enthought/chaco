
# Major library imports
from numpy import cos, linspace, pi, sin

from enthought.chaco.example_support import COLOR_PALETTE
from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayDataSource, BarPlot, DataRange1D, LabelAxis, \
                                 LinearMapper, OverlayPlotContainer, PlotAxis


def get_points():
    index = linspace(pi/4, 3*pi/2, 9)
    data = sin(index) + 2
    return (range(1, 10), data)
    
def make_curves():
    (index_points, value_points) = get_points()
    size = len(index_points)

    # Create our data sources
    idx = ArrayDataSource(index_points[:(size/2)])
    vals = ArrayDataSource(value_points[:(size/2)], sort_order="none")

    idx2 = ArrayDataSource(index_points[(size/2):])
    vals2 = ArrayDataSource(value_points[(size/2):], sort_order="none")

    idx3 = ArrayDataSource(index_points)
    starting_vals = ArrayDataSource(value_points, sort_order="none")
    vals3 = ArrayDataSource(2 * cos(value_points) + 2, sort_order="none")

    # Create the index range
    index_range = DataRange1D(idx, low=0.5, high=9.5)
    index_mapper = LinearMapper(range=index_range)

    # Create the value range
    value_range = DataRange1D(low=0, high=4.25)
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

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    
    container = OverlayPlotContainer(bgcolor = "white")
    plots = make_curves()
    for plot in plots:
        plot.padding = 50
        container.add(plot)

    left_axis = PlotAxis(plot, orientation='left')

    bottom_axis = LabelAxis(plot, orientation='bottom',
                           title='Categories',
                           positions = range(1, 10),
                           labels = ['a', 'b', 'c', 'd', 'e',
                                     'f', 'g', 'h', 'i'],
                           small_haxis_style=True)

    plot.underlays.append(left_axis)
    plot.underlays.append(bottom_axis)
        
    return container

#===============================================================================
# Attributes to use for the plot view.
size = (800, 600)
title = "Bar Plot"
        
#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)
    
    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size), 
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title
                    )
    
    def _plot_default(self):
        return _create_plot_component()
    
demo = Demo()

#===============================================================================
# Stand-alone frame to display the plot.
#===============================================================================
class PlotFrame(DemoFrame):

    def _create_window(self):
        # Return a window containing our plots
        return Window(self, -1, component=_create_plot_component())
    
if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

#--EOF---