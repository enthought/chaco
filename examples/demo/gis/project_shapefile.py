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
from pyproj import Proj, transform

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

    #set original projection
    proj4_string = '+proj=longlat +ellps=GRS80 +no_defs '
    p1 = Proj(proj4_string)

    #set desired projection
    #EPSG:2192, ED50 / France EuroLambert
    #p2 = Proj('+proj=lcc +lat_1=46.8 +lat_0=46.8 +lon_0=2.337229166666667 +k_0=0.99987742 +x_0=600000 +y_0=2200000 +ellps=intl +units=m +no_defs ')

    #EPSG:3031, WGS 84 / Antarctic Polar Stereographic
    p2 = Proj('+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ')

    #cycle through polygons in shapefile
    for i, shp in enumerate(basins.shapes()):
        points = array(shp.points)
        px, py  = transform(p1, p2, points[:,0], points[:,1])
        pd.set_data("x" + str(i), px)
        pd.set_data("y" + str(i), py)

        # Store path data for each polygon, and plot
        plot = polyplot.plot(("x" + str(i), "y" + str(i)),
                             type="polygon",
                             face_color='auto',
                             hittest_type="poly")[0]
        plot.edge_color = (0, 0, 0, 0.5)

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
