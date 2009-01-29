#!/usr/bin/env python
#what i am
# doing to test
# everything
"""
Demonstrates the Regression Selection tool.

Hold down the left mouse button to use the mouse to draw a selection region
around some points, and a line fit is drawn through the center of the points.
The parameters of the line are displayed at the bottom of the plot region.  You
can do this repeatedly to draw different regions.1

Hold the right mouse button down and drag to pan.

Use the mousewheel to zoom in and out.
"""

# Major library imports
from numpy import linspace
from numpy.random import random

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.enable.example_support import DemoFrame, demo_main
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, Group, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, HPlotContainer, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool, RegressionLasso, \
        RegressionOverlay

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():
    pd = ArrayPlotData(x=random(100), y=random(100))
    
    # Create some line plots of some of the data
    plot = Plot(pd)
    
    # Create a scatter plot and get a reference to it (separate from the
    # Plot object) because we'll need it for the regression tool below.
    scatterplot = plot.plot(("x", "y"), color="blue", type="scatter")[0]
    
    # Tweak some of the plot properties
    plot.padding = 50
    
    # Attach some tools to the plot
    plot.tools.append(PanTool(plot, drag_button="right"))
    plot.overlays.append(ZoomTool(plot))
    
    # Add the regression tool and overlay.  These need to be added
    # directly to the scatterplot instance (and not the Plot instance).
    regression = RegressionLasso(scatterplot,
    	selection_datasource=scatterplot.index)
    scatterplot.tools.append(regression)
    scatterplot.overlays.append(RegressionOverlay(scatterplot, 
                                                  lasso_selection=regression))
    return plot

#===============================================================================
# Attributes to use for the plot view.
size = (600, 600)
title = "Regression Selection"
        
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

#--EOF---