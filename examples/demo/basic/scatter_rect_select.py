"""
Rectangular selection of data points

Draws a simple scatterplot of random data.  Drag the mouse to use the
selector, which allows you to select points via a bounding box.

Upon completion of the selection operation, the indices of the selected
points are printed to the console and highlighted visually.
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
from chaco.api import (
    ArrayPlotData,
    Plot,
    LassoOverlay,
    ScatterInspectorOverlay,
)
from chaco.tools.api import RectangularSelection, ScatterInspector


# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================
def _create_plot_component():
    # Create some data
    npts = 200
    x = sort(random(npts))
    y = random(npts)

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("index", x)
    pd.set_data("value", y)

    # Create the plot
    plot = Plot(pd)
    plot.plot(
        ("index", "value"),
        type="scatter",
        name="my_plot",
        marker="circle",
        index_sort="ascending",
        color="red",
        marker_size=4,
        bgcolor="white",
    )

    # Tweak some of the plot properties
    plot.title = "Scatter Plot With Rectangular Selection"
    plot.line_width = 1
    plot.padding = 50

    # Right now, some of the tools are a little invasive, and we need the
    # actual ScatterPlot object to give to them
    my_plot = plot.plots["my_plot"][0]

    # Attach some tools to the plot
    rect_selection = RectangularSelection(
        component=my_plot,
        selection_datasource=my_plot.index,
        drag_button="left",
        metadata_name="selections",
    )
    my_plot.tools.append(rect_selection)
    my_plot.tools.append(ScatterInspector(my_plot, selection_mode="toggle"))
    my_plot.active_tool = rect_selection

    lasso_overlay = LassoOverlay(
        lasso_selection=rect_selection, component=my_plot
    )
    my_plot.overlays.append(lasso_overlay)

    scatter_overlay = ScatterInspectorOverlay(
        component=my_plot,
        selection_color="cornflowerblue",
        selection_marker_size=int(my_plot.marker_size) + 3,
        selection_marker="circle",
    )
    my_plot.overlays.append(scatter_overlay)

    return plot


# ===============================================================================
# Attributes to use for the plot view.
size = (650, 650)
title = "Scatter plot with selection"
bgcolor = "lightgray"


# ===============================================================================
# # Demo class that is used by the demo.py application.
# ===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
        Group(
            Item(
                "plot",
                editor=ComponentEditor(size=size, bgcolor=bgcolor),
                show_label=False
            ),
            orientation="vertical",
        ),
        resizable=True,
        title=title,
    )

    def _selection_changed(self, event):
        mask = self.index_datasource.metadata["selections"]
        print("New selection: ")
        print(compress(mask, arange(len(mask))))
        # Ensure that the points are printed immediately:
        sys.stdout.flush()

    def _plot_default(self):
        plot = _create_plot_component()

        # Retrieve the plot hooked to the RectangularSelection tool.
        my_plot = plot.plots["my_plot"][0]
        rect_selection = my_plot.active_tool

        # Set up the trait handler for the selection
        self.index_datasource = my_plot.index
        rect_selection.observe(self._selection_changed, "selection_changed")

        return plot


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
