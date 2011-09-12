"""
Implementation of a standard financial plot visualization using Chaco
renderers and scales.
"""

# Major library imports
from numpy import abs, arange, cumprod, random

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayDataSource, BarPlot, DataRange1D, \
        LinearMapper, VPlotContainer, PlotAxis, FilledLinePlot, \
        add_default_grids, PlotLabel
from chaco.tools.api import PanTool, ZoomTool

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create the data and datasource objects
    numpoints = 500
    index = arange(numpoints)
    returns = random.lognormal(0.01, 0.1, size=numpoints)
    price = 100.0 * cumprod(returns)
    volume = abs(random.normal(1000.0, 1500.0, size=numpoints) + 2000.0)

    time_ds = ArrayDataSource(index)
    vol_ds = ArrayDataSource(volume, sort_order="none")
    price_ds = ArrayDataSource(price, sort_order="none")

    xmapper = LinearMapper(range=DataRange1D(time_ds))
    vol_mapper = LinearMapper(range=DataRange1D(vol_ds))
    price_mapper = LinearMapper(range=DataRange1D(price_ds))

    price_plot = FilledLinePlot(index = time_ds, value = price_ds,
                                index_mapper = xmapper,
                                value_mapper = price_mapper,
                                edge_color = "blue",
                                face_color = "paleturquoise",
                                alpha = 0.5,
                                bgcolor = "white",
                                border_visible = True)
    add_default_grids(price_plot)
    price_plot.overlays.append(PlotAxis(price_plot, orientation='left'))
    price_plot.overlays.append(PlotAxis(price_plot, orientation='bottom'))
    price_plot.tools.append(PanTool(price_plot, constrain=True,
                                    constrain_direction="x"))
    price_plot.overlays.append(ZoomTool(price_plot, drag_button="right",
                                          always_on=True,
                                          tool_mode="range",
                                          axis="index"))

    vol_plot = BarPlot(index = time_ds, value = vol_ds,
                       index_mapper = xmapper,
                       value_mapper = vol_mapper,
                       line_color = "transparent",
                       fill_color = "black",
                       bar_width = 1.0,
                       bar_width_type = "screen",
                       antialias = False,
                       height = 100,
                       resizable = "h",
                       bgcolor = "white",
                       border_visible = True)

    add_default_grids(vol_plot)
    vol_plot.underlays.append(PlotAxis(vol_plot, orientation='left'))
    vol_plot.tools.append(PanTool(vol_plot, constrain=True,
                                  constrain_direction="x"))

    container = VPlotContainer(bgcolor = "lightblue",
                               spacing = 20,
                               padding = 50,
                               fill_padding=False)
    container.add(vol_plot)
    container.add(price_plot)
    container.overlays.append(PlotLabel("Financial Plot",
                                        component=container,
                                        #font="Times New Roman 24"))
                                        font="Arial 24"))
    return container

#===============================================================================
# Attributes to use for the plot view.
size=(800,600)
title="Financial plot example"

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

if __name__ == "__main__":
    demo.configure_traits()

#--EOF---
