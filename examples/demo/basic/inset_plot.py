#!/usr/bin/env python
""" Overlaid inset plots.

A modification of line_plot1.py that shows the second plot as a subwindow
of the first.  You can pan and zoom the second plot just like the first,
and you can move it around my right-click and dragging in the smaller plot.
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, OverlayPlotContainer, Plot
from chaco.tools.api import PanTool, ZoomTool, MoveTool

# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================
def _create_plot_component():
    # Create some x-y data series to plot
    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(index=x)
    for i in range(5):
        pd.set_data("y" + str(i), jn(i, x))

    # Create some line plots of some of the data
    plot1 = Plot(pd)
    plot1.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="red")
    plot1.plot(("index", "y3"), name="j_3", color="blue")

    # Tweak some of the plot properties
    plot1.title = "Inset Plot"
    plot1.padding = 50

    # Attach some tools to the plot
    plot1.tools.append(PanTool(plot1))
    zoom = ZoomTool(component=plot1, tool_mode="box", always_on=False)
    plot1.overlays.append(zoom)

    # Create a second scatter plot of one of the datasets, linking its
    # range to the first plot
    plot2 = Plot(pd, range2d=plot1.range2d, padding=50)
    plot2.plot(("index", "y3"), type="scatter", color="blue", marker="circle")
    plot2.resizable = ""
    plot2.bounds = [250, 250]
    plot2.position = [550, 150]
    plot2.bgcolor = "white"
    plot2.border_visible = True
    plot2.unified_draw = True

    plot2.tools.append(PanTool(plot2))
    plot2.tools.append(MoveTool(plot2, drag_button="right"))
    zoom = ZoomTool(component=plot2, tool_mode="box", always_on=False)
    plot2.overlays.append(zoom)

    # Create a container and add our plots
    container = OverlayPlotContainer()
    container.add(plot1)
    container.add(plot2)
    return container


# ===============================================================================
# Attributes to use for the plot view.
size = (900, 500)
title = "Inset plots"

# ===============================================================================
# # Demo class that is used by the demo.py application.
# ===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
        Group(
            Item("plot", editor=ComponentEditor(size=size), show_label=False),
            orientation="vertical",
        ),
        resizable=True,
        title=title,
    )

    def _plot_default(self):
        return _create_plot_component()


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
