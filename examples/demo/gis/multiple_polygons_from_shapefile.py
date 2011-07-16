#!/usr/bin/env python
"""
Reads river basin polygons from tx_major_river_basins shapefile and
plots each river basin in a different color. Plots Lat/Lon directly
without conducting coordinate conversions
"""
import itertools

# Major library imports
from numpy import array

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Enum, CArray
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool

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
    basins = shapefile.Reader('tx_major_river_basins/basins_dd')
    #cycle through polygons in shapefile
    for i, shp in enumerate(basins.shapes()):
        points = array(shp.points)
        pd.set_data("x" + str(i), points[:,0])
        pd.set_data("y" + str(i), points[:,1])

        # Store path data for each polygon, and plot
        plot = polyplot.plot(("x" + str(i), "y" + str(i)),
                             type="polygon",
                             face_color='oldlace',
                             hittest_type="poly")[0]
        plot.edge_color = (0, 0, 0, 0.5)

    #get polygons from shapefile
    rivers = shapefile.Reader('tx_major_rivers/MajorRivers_dd83')
    #cycle through polygons in shapefile
    for i, shape_record in enumerate(rivers.shapeRecords()):
        if i > 400:
            break
        points = array(shape_record.shape.points)
        pd.set_data("river_x" + str(i), points[:,0])
        pd.set_data("river_y" + str(i), points[:,1])

        # Store path data for each polygon, and plot
        plot = polyplot.plot(("river_x" + str(i), "river_y" + str(i)),
                             type="line",
                             hittest_type="line")[0]
        plot.color = (0.392, 0.584, 0.929, 0.75)

    # Tweak some of the plot properties
    polyplot.padding = 50
    polyplot.title = "Major River Basins of Texas"
    polyplot.x_axis.title = "Longitude"
    polyplot.y_axis.title = "Latitude"

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
                    width=size[0], height=size[1],
                    title=title
                    )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

#--EOF---
