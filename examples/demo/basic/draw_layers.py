#!/usr/bin/env python
"""
Demonstrates the use of drawing layers in Chaco.

Three classes of functions are plotted: bessels, sines,
and Struve functions.
"""

# Major library imports
from numpy import linspace, sin
from scipy.special import jn, struve

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool

# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================
def _create_plot_component():

    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(x=x)

    # Create some line plots of some of the data
    plot = Plot(pd, padding=50, border_visible=True, overlay_border=True)
    plot.legend.visible = True

    # Extend the plot's list of drawing layers
    ndx = plot.draw_order.index("plot")
    plot.draw_order[ndx:ndx] = ["bessel", "sine", "struve"]

    # Draw struve
    for i in range(3):
        y_name = "struve" + str(i)
        pd.set_data(y_name, struve(i, x))
        renderer = plot.plot(
            ("x", y_name), color="blue", name=y_name, line_width=2
        )[0]
        renderer.draw_layer = "struve"
        renderer.unified_draw = True

    # Draw bessels
    for i in range(3):
        y_name = "bessel" + str(i)
        pd.set_data(y_name, jn(i, x))
        renderer = plot.plot(
            ("x", y_name), color="green", name=y_name, line_width=2
        )[0]
        renderer.draw_layer = "bessel"
        renderer.unified_draw = True

    # Draw sines
    for i in range(3):
        y_name = "sine" + str(i)
        pd.set_data(y_name, sin(x * (i + 1) / 1.5))
        renderer = plot.plot(
            ("x", y_name), color="red", name=y_name, line_width=2
        )[0]
        renderer.draw_layer = "sine"
        renderer.unified_draw = True

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    return plot


# ===============================================================================
# Attributes to use for the plot view.
size = (900, 500)
title = "Draw order demonstration"

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
