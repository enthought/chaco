#!/usr/bin/env python
"""
Shares same basic interactions as polygon_plot.py, but adds a new one:
 - Right click and drag to move a polygon around.
"""

# Major library imports
from numpy import array

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Enum, CArray
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool

#shapefile.py in in the pwd
import shapefile

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # list of points that define the vertices of the polygon
    # points = n_gon(center=(0,0), r=4, nsides=8)

    # Choose some colors for our polygons
    #colors = {3:0xaabbcc,   4:'orange', 5:'yellow',    6:'lightgreen',
    #          7:'green', 8:'blue',   9:'lavender', 10:'purple'}

    # Create a PlotData object to store the polygon data
    pd = ArrayPlotData()
    # Create a Polygon Plot to draw the regular polygons
    polyplot = Plot(pd)
    
    #get polygons from shapefile
    sf = shapefile.Reader('tx_major_river_basins/basins_dd')
    #cycle through polygons in shapefile
    i = 0
    for shp in sf.shapes():
        points = array(shp.points)
        pd.set_data("x" + str(i), points[:,0])
        pd.set_data("y" + str(i), points[:,1])

        # Store path data for each polygon, and plot
        plot = polyplot.plot(("x" + str(i), "y" + str(i)),
                             type="polygon",
                             face_color='auto',
                             hittest_type="poly")[0]

    # Tweak some of the plot properties
    polyplot.padding = 50
    polyplot.title = "Polygon Plot"

    # Attach some tools to the plot
    polyplot.tools.append(PanTool(polyplot))
    zoom = ZoomTool(polyplot, tool_mode="box", always_on=False)
    polyplot.overlays.append(zoom)

    return polyplot

#===============================================================================
# Attributes to use for the plot view.
size=(800,800)
title="Polygon Plot"

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
                    resizable=True, title=title
                    )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

#--EOF---
