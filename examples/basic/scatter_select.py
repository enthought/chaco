#!/usr/bin/env python
"""
Draws a simple scatterplot of random data.  The only interaction available is
the lasso selector, which allows you to circle a set of points.  Upon
completion of the lasso operation, the indices of the selected points are
printed to the console.

Uncomment 'lasso_selection.incremental_select' line to see the selection 
compute indices in realtime.
"""

# Major library imports
from numpy import arange, sort, compress, arange
from numpy.random import random

from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window
from enthought.traits.api import Instance

# Chaco imports
from enthought.chaco.api import AbstractDataSource, ArrayPlotData, Plot, \
                                 HPlotContainer, LassoOverlay 
from enthought.chaco.tools.api import LassoSelection, ScatterInspector


class PlotFrame(DemoFrame):

    index_datasource = Instance(AbstractDataSource)
    
    def _create_window(self):

        # Create some data
        npts = 2000
        x = sort(random(npts))
        y = random(npts)

        # Create a plot data obect and give it this data
        pd = ArrayPlotData()
        pd.set_data("index", x)
        pd.set_data("value", y)

        # Create the plot
        plot = Plot(pd)
        plot.plot(("index", "value"),
                  type="scatter",
                  name="my_plot",
                  marker="circle",
                  index_sort="ascending",
                  color="red",
                  marker_size=4,
                  bgcolor="white")

        # Tweak some of the plot properties
        plot.title = "Scatter Plot With Selection"
        plot.line_width = 1
        plot.padding = 50

        # Right now, some of the tools are a little invasive, and we need the 
        # actual ScatterPlot object to give to them
        my_plot = plot.plots["my_plot"][0]

        # Attach some tools to the plot
        lasso_selection = LassoSelection(component=my_plot,
                                         selection_datasource=my_plot.index)
        my_plot.active_tool = lasso_selection
        my_plot.tools.append(ScatterInspector(my_plot))
        lasso_overlay = LassoOverlay(lasso_selection=lasso_selection,
                                     component=my_plot)
        my_plot.overlays.append(lasso_overlay)

        # Uncomment this if you would like to see incremental updates:
        #lasso_selection.incremental_select = True

        # Set up the trait handler for the selection
        self.index_datasource = my_plot.index
        lasso_selection.on_trait_change(self._selection_changed, 
                                        'selection_changed')
        
        # Return a window containing our plot container
        return Window(self, -1, component=plot, bg_color="lightgray")

    def _selection_changed(self):
        mask = self.index_datasource.metadata['selection']
        print "New selection: "
        print compress(mask, arange(len(mask)))
        print

if __name__ == "__main__":
    demo_main(PlotFrame, size=(650,650), title="Scatter plot with selection")

# EOF
