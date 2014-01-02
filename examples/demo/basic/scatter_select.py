"""
Lasso selection of data points

Draws a simple scatterplot of random data.  Drag the mouse to use the lasso
selector, which allows you to circle all the points in a region.

Upon completion of the lasso operation, the indices of the selected points are
printed to the console.

Uncomment 'lasso_selection.incremental_select' line (line 74) to see the
indices of the selected points computed in real time.
"""

import sys

# Major library imports
from numpy import sort, compress, arange
from numpy.random import random

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot, LassoOverlay
from chaco.tools.api import LassoSelection, ScatterInspector

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

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
    plot.title = "Scatter Plot With Lasso Selection"
    plot.line_width = 1
    plot.padding = 50

    # Right now, some of the tools are a little invasive, and we need the
    # actual ScatterPlot object to give to them
    my_plot = plot.plots["my_plot"][0]

    # Attach some tools to the plot
    lasso_selection = LassoSelection(component=my_plot,
                                     selection_datasource=my_plot.index,
                                     drag_button="left")
                                     #drag_button="right")
    my_plot.active_tool = lasso_selection
    my_plot.tools.append(ScatterInspector(my_plot))
    lasso_overlay = LassoOverlay(lasso_selection=lasso_selection,
                                 component=my_plot)
    my_plot.overlays.append(lasso_overlay)

    # Uncomment this if you would like to see incremental updates:
    #lasso_selection.incremental_select = True

    return plot


#===============================================================================
# Attributes to use for the plot view.
size=(650,650)
title="Scatter plot with selection"
bg_color="lightgray"

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

    def _selection_changed(self):
        mask = self.index_datasource.metadata['selection']
        print "New selection: "
        print compress(mask, arange(len(mask)))
        # Ensure that the points are printed immediately:
        sys.stdout.flush()
        

    def _plot_default(self):
         plot = _create_plot_component()

         # Retrieve the plot hooked to the LassoSelection tool.
         my_plot = plot.plots["my_plot"][0]
         lasso_selection = my_plot.active_tool

         # Set up the trait handler for the selection
         self.index_datasource = my_plot.index
         lasso_selection.on_trait_change(self._selection_changed,
                                        'selection_changed')

         return plot

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
