#!/usr/bin/env python
"""
Demonstrates the LassoTool and overlay on a colormapped image
plot.  The underlying plot is similar to the one in cmap_image_plot.py.

Use Shift-drag to select multiple disjoint regions.
"""

# Major library imports
from numpy import linspace, meshgrid, pi, sin

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, jet, Plot, LassoOverlay
from enthought.chaco.tools.api import LassoSelection, LassoSelection

#===============================================================================
# # Create the Chaco plot.
#===============================================================================

def lasso_updated(lasso_tool, name, old, new_selections):
    # new_selections is a list of arrays of coordinates in dataspace.  It is a
    # list because the LassoSelection supports multiple, disjoint selection regions.
    for i, selection in enumerate(new_selections):
        print "Selection region", i

        # We first map to screen because the selection is stored as coordinates
        # in data space
        screen_pts = lasso_tool.plot.map_screen(selection)

        # Now map each point into the grid index
        for x, y in screen_pts:
            print "\t", lasso_tool.plot.map_index((x, y))
    return

def _create_plot_component():# Create a scalar field to colormap
    xbounds = (-2*pi, 2*pi, 600)
    ybounds = (-1.5*pi, 1.5*pi, 300)
    xs = linspace(*xbounds)
    ys = linspace(*ybounds)
    x, y = meshgrid(xs,ys)
    z = sin(x)*y

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("imagedata", z)

    # Create the plot
    plot = Plot(pd)
    img_plot = plot.img_plot("imagedata",
                             xbounds=xbounds[:2],
                             ybounds=ybounds[:2],
                             colormap=jet)[0]

    # Tweak some of the plot properties
    plot.title = "Image Plot with Lasso"
    plot.padding = 50

    lasso_selection = LassoSelection(component=img_plot)
    lasso_selection.on_trait_change(lasso_updated, "disjoint_selections")
    lasso_overlay = LassoOverlay(lasso_selection = lasso_selection, component=img_plot)
    img_plot.tools.append(lasso_selection)
    img_plot.overlays.append(lasso_overlay)
    return plot

#===============================================================================
# Attributes to use for the plot view.
size = (800, 600)
title="Image Plot with Lasso"

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

#===============================================================================
# Stand-alone frame to display the plot.
#===============================================================================
class PlotFrame(DemoFrame):

    def _create_window(self):
        # Return a window containing our plots
        return Window(self, -1, component=_create_plot_component())

if __name__ == "__main__":
    demo_main(PlotFrame, size=size, title=title)

