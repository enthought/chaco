""" Tornado plot example from Brennan Williams """

# Major library imports
from numpy import arange, cos, linspace, pi, sin, ones

from chaco.example_support import COLOR_PALETTE
from enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enable.api import Window, Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayDataSource, BarPlot, DataRange1D, LabelAxis, \
                                LinearMapper, OverlayPlotContainer, PlotAxis, PlotGrid, \
                                DataLabel


def get_points():
    index = linspace(pi/4, 3*pi/2, 9)
    data = sin(index) + 2
    return (range(1, 10), data)

def make_curves():
   (index_points, value_points) = get_points()
   size = len(index_points)

   middle_value=2500000.0
   mid_values=middle_value*ones(size)
   low_values=mid_values-10000.0*value_points
   high_values=mid_values+20000.0*value_points
   range_values=high_values-low_values

   idx = ArrayDataSource(index_points)
   vals = ArrayDataSource(low_values, sort_order="none")

   idx3 = ArrayDataSource(index_points)
   vals3 = ArrayDataSource(high_values, sort_order="none")

   starting_vals = ArrayDataSource(mid_values, sort_order="none")

   # Create the index range
   index_range = DataRange1D(idx, low=0.5, high=9.5)
   index_mapper = LinearMapper(range=index_range)

   # Create the value range
   lower_value=low_values.min()
   higher_value=high_values.max()
   value_range = DataRange1D(vals, vals3, low_setting='auto',
                             high_setting='auto', tight_bounds=False)
   value_mapper = LinearMapper(range=value_range,tight_bounds=False)

   # Create the plot
   plot1 = BarPlot(index=idx, value=vals,
                   value_mapper=value_mapper,
                   index_mapper=index_mapper,
                   starting_value=starting_vals,
                   line_color='black',
                   orientation='v',
                   fill_color=tuple(COLOR_PALETTE[6]),
                   bar_width=0.8, antialias=False)

   plot3 = BarPlot(index=idx3, value=vals3,
                   value_mapper=value_mapper,
                   index_mapper=index_mapper,
                   starting_value=starting_vals,
                   line_color='black',
                   orientation='v',
                   fill_color=tuple(COLOR_PALETTE[1]),
                   bar_width=0.8, antialias=False)

   return [plot1, plot3]

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    container = OverlayPlotContainer(bgcolor = "white")
    plots = make_curves()
    for plot in plots:
       plot.padding = 60
       container.add(plot)

    bottom_axis = PlotAxis(plot, orientation='bottom')

    label_list=['var a', 'var b', 'var c', 'var d', 'var e', 'var f',
                'var g', 'var h', 'var i']
    vertical_axis = LabelAxis(plot, orientation='left',
                            title='Categories',
                            positions = range(1, 10),
                            labels=label_list)
    vertical2_axis = LabelAxis(plot, orientation='right',
                               positions = range(1, 10),
                               labels=label_list)

    plot.underlays.append(vertical_axis)
    plot.underlays.append(vertical2_axis)
    plot.underlays.append(bottom_axis)

    return container

#===============================================================================
# Attributes to use for the plot view.
size=(800,600)
title="Tornado Plot"

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
                    resizable=True, title=title,
                    width=size[0], height=size[1]
                    )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

#===============================================================================
# Stand-alone frame to display the plot.
#===============================================================================
class PlotFrame(DemoFrame):

    def _create_window(self):

        component = _create_plot_component()
        # Return a window containing our plots
        return Window(self, -1, component=component)

if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

# EOF
