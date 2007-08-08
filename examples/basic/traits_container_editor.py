#!/usr/bin/env python
"""
Draws some x-y line and scatter plots. On the left hand plot:
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".

This example differs from line_plot1.py in that it uses the PlotContainerEditor
to embed the plot in traits.
"""


# Major library imports
from numpy import linspace
from scipy.special import jn

# Enthought library imports
from enthought.enable2.wx_backend.api import Window
from enthought.traits.api import Any, Array, HasTraits, Str
from enthought.traits.ui.api import Item, View
from enthought.traits.ui.menu import NoButtons

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, Plot, HPlotContainer
from enthought.chaco2.chaco2_plot_container_editor import PlotContainerEditor
from enthought.chaco2.tools.api import PanTool, SimpleZoom, LegendTool


class Basic(HasTraits):

    plot = Any

    traits_view = View(Item('plot', editor=PlotContainerEditor(),
                            show_label=False),
                       buttons=NoButtons,
                       width=800, height=600, resizable=True)

    def __init__(self, *args, **kw):
        HasTraits.__init__(self, *args, **kw)
        self.create_plot()

    def add_tools(self, plot):
        plot.tools.append(PanTool(plot))
        plot.overlays.append(SimpleZoom(plot))

    def create_plot(self):
        x = linspace(-5, 5, 100)
        y = jn(0, x)
        data = ArrayPlotData(index = x, y0 = y)
        p = Plot(data)
        p.plot(("index", "y0"), name="jn0", color="red")
        self.add_tools(p)

        self.plot = p


class TwoPlots(Basic):

    def create_plot(self):
        x = linspace(-2.0, 10.0, 100)
        data = ArrayPlotData(index = x)
        for i in range(5):
            data.set_data("y" + str(i), jn(i,x))

        plot1 = Plot(data)
        plot1.plot(("index", "y0"), color="red")
        plot1.plot(("index", "y1"), color="blue")
        plot1.title = "jn0 and jn1"
        self.add_tools(plot1)

        plot2 = Plot(data)
        plot2.plot(("index", "y2"), name="jn2")
        plot2.plot(("index", "y3", "y4"), name="jn3,jn4", color=(1.0, 0.4, 0.8))
        plot2.legend.visible = True
        self.add_tools(plot2)

        # To synchronize the axes between plot1 and plot2:
        #plot1.index_range = plot2.index_range
        #plot1.value_range = plot2.value_range

        # To make the legend movable using right-click-drag:
        #plot2.legend.tools.append(LegendTool(plot2.legend, drag_button="right"))

        # To make the legend transparent:
        #plot2.legend.bgcolor = "transparent"

        container = HPlotContainer()
        container.add(plot1)
        container.add(plot2)
        
        self.plot = container

        
if __name__ == "__main__":

    #basic = Basic()
    #basic.configure_traits()

    twoplots = TwoPlots()
    twoplots.configure_traits()


