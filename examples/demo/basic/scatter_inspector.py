"""
Scattergram inspector tool

Allows the user to highlight and/or select individual points of a scattergram.

When the mouse hovers over a scatter point, it changes temporarily. If you click
on a point, you select and mark (or unselect and unmark) the point.
"""

# Major library imports
from numpy import random

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot, ScatterInspectorOverlay
from chaco.tools.api import PanTool, ZoomTool, ScatterInspector

# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================
def _create_plot_component():

    # Create a random scattering of XY pairs
    x = random.uniform(0.0, 10.0, 50)
    y = random.uniform(0.0, 5.0, 50)
    pd = ArrayPlotData(x=x, y=y)
    plot = Plot(pd, border_visible=True, overlay_border=True)

    scatter = plot.plot(("x", "y"), type="scatter", color="lightblue")[0]

    # Tweak some of the plot properties
    plot.title = "Scatter Inspector Demo"
    plot.padding = 50

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    plot.overlays.append(ZoomTool(plot))

    # Attach the inspector and its overlay
    inspector = ScatterInspector(scatter)
    scatter.tools.append(inspector)
    overlay = ScatterInspectorOverlay(
        scatter,
        hover_color="red",
        hover_marker_size=6,
        selection_marker_size=6,
        selection_color="yellow",
        selection_outline_color="purple",
        selection_line_width=3,
    )
    scatter.overlays.append(overlay)

    # Optional: add a listener on inspector events:
    def echo(event):
        new = event.new
        print("{} event on element {}".format(new.event_type, new.event_index))

    inspector.observe(echo, "inspector_event")

    return plot


# ===============================================================================
# Attributes to use for the plot view.
size = (900, 500)
title = "Tooltip demo"

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
