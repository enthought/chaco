#!/usr/bin/env python
""" Polygon plot with drag-move.

Shares same basic interactions as polygon_plot.py, but adds a new one:
 - Right click and drag to move a polygon around.
"""

# Major library imports
from numpy import transpose

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Enum, CArray
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot
from chaco.base import n_gon
from chaco.tools.api import PanTool, ZoomTool, DragTool


class DataspaceMoveTool(DragTool):
    """
    Modifies the data values of a plot.  Only works on instances
    of BaseXYPlot or its subclasses
    """

    event_state = Enum("normal", "dragging")
    _prev_pt = CArray

    def is_draggable(self, x, y):
        return self.component.hittest((x, y))

    def drag_start(self, event):
        data_pt = self.component.map_data((event.x, event.y), all_values=True)
        self._prev_pt = data_pt
        event.handled = True

    def dragging(self, event):
        plot = self.component
        cur_pt = plot.map_data((event.x, event.y), all_values=True)
        dx = cur_pt[0] - self._prev_pt[0]
        dy = cur_pt[1] - self._prev_pt[1]
        index = plot.index.get_data() + dx
        value = plot.value.get_data() + dy
        plot.index.set_data(index, sort_order=plot.index.sort_order)
        plot.value.set_data(value, sort_order=plot.value.sort_order)
        self._prev_pt = cur_pt
        event.handled = True
        plot.request_redraw()


# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================
def _create_plot_component():

    # Use n_gon to compute center locations for our polygons
    points = n_gon(center=(0, 0), r=4, nsides=8)

    # Choose some colors for our polygons
    colors = {
        3: 0xAABBCC,
        4: "orange",
        5: "yellow",
        6: "lightgreen",
        7: "green",
        8: "blue",
        9: "lavender",
        10: "purple",
    }

    # Create a PlotData object to store the polygon data
    pd = ArrayPlotData()

    # Create a Polygon Plot to draw the regular polygons
    polyplot = Plot(pd)

    # Store path data for each polygon, and plot
    nsides = 3
    for p in points:
        npoints = n_gon(center=p, r=2, nsides=nsides)
        nxarray, nyarray = transpose(npoints)
        pd.set_data("x" + str(nsides), nxarray)
        pd.set_data("y" + str(nsides), nyarray)
        plot = polyplot.plot(
            ("x" + str(nsides), "y" + str(nsides)),
            type="polygon",
            face_color=colors[nsides],
            hittest_type="poly",
        )[0]
        plot.tools.append(DataspaceMoveTool(plot, drag_button="right"))
        nsides = nsides + 1

    # Tweak some of the plot properties
    polyplot.padding = 50
    polyplot.title = "Polygon Plot"

    # Attach some tools to the plot
    polyplot.tools.append(PanTool(polyplot))
    zoom = ZoomTool(polyplot, tool_mode="box", always_on=False)
    polyplot.overlays.append(zoom)

    return polyplot


# ===============================================================================
# Attributes to use for the plot view.
size = (800, 800)
title = "Polygon Plot"

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
