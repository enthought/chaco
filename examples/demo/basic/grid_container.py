"""
Grid containing plots with resize restrictions

The ability of Plots to resize, when their container resizes, can be explicitly
restricted in either direction. This can place *implicit* restrictions on
other plots in the grid.

In this example, the upper left plot is explicitly restricted from resizing 
horizontally. The bottom center plot is explicitly restricted from resizing 
at all.

The resulting implicit restrictions on the other 4 plots are generally
intuitive, except that when the window gets too small to respect all of the
restrictions, the results are OS and GUI-backend-dependent, not easily 
predictable.

"""

# Major library imports
from numpy import linspace
from scipy.special import jn

from chaco.example_support import COLOR_PALETTE

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, GridContainer, Plot, PlotLabel
from chaco.tools.api import PanTool, ZoomTool



#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    # Create a GridContainer to hold all of our plots: 2 rows, 3 columns:
    container = GridContainer(padding=40, fill_padding=True,
                              bgcolor="lightgray", use_backbuffer=True,
                              shape=(2,3), spacing=(20,20))

    # Create the initial series of data
    x = linspace(-5, 15.0, 100)
    pd = ArrayPlotData(index = x)

    # Plot some bessel functions and add the plots to our container
    for i in range(6):
        pd.set_data("y" + str(i), jn(i,x))
        plot = Plot(pd)
        plot.plot(("index", "y" + str(i)),
                  color=tuple(COLOR_PALETTE[i]), line_width=2.0,
                  bgcolor = "white", border_visible=True)

        # Tweak some of the plot properties
        plot.border_width = 1
        plot.padding = 0
        plot.padding_top = 30

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Add to the grid container (
        container.add(plot)

    # Set the upper-left plot to only be resizable vertically, and to have a
    # fixed horizontal width. This also constrains the width of the first column.
    ul_plot = container.components[0]
    ul_plot.resizable = "v"
    ul_plot.width = 200
    ul_plot.overlays.append(PlotLabel("Not horizontally resizable",
                                      component=ul_plot))

    # Set the bottom center plot to have a fixed width and height.
    # This also constrains the height of the bottom row and the width of
    # the middle column.
    cplot = container.components[4]
    cplot.resizable = ""
    cplot.bounds = [400,400]
    cplot.overlays.append(PlotLabel("Not resizable", component=cplot))

    container.padding_top = 50
    container.overlays.append(
        PlotLabel('Resize the window - some plots resize, others cannot '
                  '(see source code)',
                  component=container,
                  font = "swiss 16",
                  overlay_position = "top"))
        
    return container

#===============================================================================
# Attributes to use for the plot view.
size=(1000,800)
title="Resizable Grid Container"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = \
        View(
            Group(
                Item('plot', editor=ComponentEditor(size=size),
                        show_label=False),
                orientation = "vertical"
                ),
            resizable=True, title=title )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
