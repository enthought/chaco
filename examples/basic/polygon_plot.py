#!/usr/bin/env python
"""
Draws some different polygons
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular 
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".
"""

# Major library imports
import math
from numpy import array, transpose

# Enthought library imports
from enthought.enable2.wx_backend.api import Window
from enthought.traits.api import Enum, Tuple, Dict

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco2.base import n_gon
from enthought.chaco2.example_support import DemoFrame, demo_main
from enthought.chaco2.tools.api import PanTool, SimpleZoom, DragTool


class SpinTool(DragTool):

    event_state = Enum("normal", "dragging")
    _start = Tuple
    _stop = Tuple

    def drag_start(self, event):
        self._start = (event.x - self.component.x, event.y - self.component.y)
        #print self._start
        event.handled = True

    def dragging(self, event):
        index_mid = (self.component.index_range.high + self.component.index_range.low)/2.0
        value_mid = (self.component.value_range.high + self.component.value_range.low)/2.0
        center = (self.component.x_mapper.map_screen(index_mid), \
                    self.component.x_mapper.map_screen(value_mid))
        self._stop = (event.x - self.component.x, event.y - self.component.y)

        newstart = (self._start[0] - center[0], self._start[1] - center[1])
        newstop = (self._stop[0] - center[0], self._stop[1] - center[1])
        lenstart = math.sqrt(math.pow(newstart[0], 2) + math.pow(newstart[1],2))
        lenstop = math.sqrt(math.pow(newstop[0], 2) + math.pow(newstop[1],2))
        numerator = newstart[0]*newstop[0] + newstart[1]*newstop[1]
        denominator = lenstart*lenstop
        angle = math.degrees(math.acos(numerator/(lenstart*lenstop)))
        #print angle
        self._start = self._stop
        
        x = self._start[0] - center[0]
        y = self._start[1] - center[1]


class PlotFrame(DemoFrame):

    def _create_window(self):

        # Use n_gon to compute center locations for our polygons
        points = n_gon(center=(0,0), r=4, nsides=8)
 
        # Choose some colors for our polygons
        colors = {3:'red',   4:'orange', 5:'yellow',    6:'lightgreen',
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
            polyplot.plot(("x"+str(nsides), "y"+str(nsides)), 
                          type="polygon", 
                          face_color=colors[nsides])
            nsides = nsides + 1

        # Tweak some of the plot properties
        polyplot.padding = 50
        polyplot.title = "My First Polygon Plot"

        # Attach some tools to the plot
        polyplot.tools.append(PanTool(polyplot))
        polyplot.tools.append(SpinTool(polyplot, drag_button="right"))
        zoom = SimpleZoom(polyplot, tool_mode="box", always_on=False)
        polyplot.overlays.append(zoom)

        # Return a window containing our plots
        return Window(self, -1, component=polyplot)

if __name__ == '__main__':
    demo_main(PlotFrame, size=(800,800), title="Basic Polygon Plot")

