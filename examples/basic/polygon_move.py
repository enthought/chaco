#!/usr/bin/env python
"""
Shares same basic interactions as polygon_plot.py, but adds a new one:
 - Right click and drag to move a polygon around.
"""

# Major library imports
import math
from numpy import array, transpose

from enthought.enable2.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable2.api import Window
from enthought.traits.api import Enum, CArray, Dict

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco2.base import n_gon
from enthought.chaco2.tools.api import PanTool, SimpleZoom, DragTool

class DataspaceMoveTool(DragTool):
    """
    Modifies the data values of a plot.  Only works on instances
    of BaseXYPlot or its subclasses 
    """

    event_state = Enum("normal", "dragging")
    _prev_pt = CArray

    def is_draggable(self, x, y):
        return self.component.hittest((x,y))

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
        


class PlotFrame(DemoFrame):

    def _create_window(self):

        # Use n_gon to compute center locations for our polygons
        points = n_gon(center=(0,0), r=4, nsides=8)
 
        # Choose some colors for our polygons
        colors = {3:0xaabbcc,   4:'orange', 5:'yellow',    6:'lightgreen',
                  7:'green', 8:'blue',   9:'lavender', 10:'purple'}
 
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
            plot = polyplot.plot(("x"+str(nsides), "y"+str(nsides)), 
                          type="polygon", 
                          face_color=colors[nsides],
                          hittest_type="poly")[0]
            plot.tools.append(DataspaceMoveTool(plot, drag_button="right"))
            nsides = nsides + 1

        # Tweak some of the plot properties
        polyplot.padding = 50
        polyplot.title = "Polygon Plot"

        # Attach some tools to the plot
        polyplot.tools.append(PanTool(polyplot))
        zoom = SimpleZoom(polyplot, tool_mode="box", always_on=False)
        polyplot.overlays.append(zoom)

        # Return a window containing our plots
        return Window(self, -1, component=polyplot)

if __name__ == '__main__':
    demo_main(PlotFrame, size=(800,800), title="Polygon Plot")

