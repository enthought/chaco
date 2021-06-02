#!/usr/bin/env python
"""
Scatter plot with point selection

Draws a simple scatter plot of random data. The user can click on points to
select or unselect them.

    - Left-click on a point to select or unselect it.
    - Left-drag to pan.
    - Mouse wheel to zoom

"""


# FIXME: the 'z' zoom interaction is ill-behaved.

# Major library imports
from numpy import sort
from numpy.random import random

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, VGroup, View, Label, HGroup, spring

# Chaco imports
from chaco.api import (
    AbstractDataSource,
    ArrayPlotData,
    Plot,
    ScatterInspectorOverlay,
)
from chaco.tools.api import ScatterInspector, PanTool, ZoomTool

# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================
def _create_plot_component():

    # Create some data
    npts = 100
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
        color="slategray",
        marker_size=6,
        bgcolor="white",
    )

    # Tweak some of the plot properties
    plot.title = "Scatter Plot With Selection"
    plot.line_width = 1
    plot.padding = 50

    # Right now, some of the tools are a little invasive, and we need the
    # actual ScatterPlot object to give to them
    my_plot = plot.plots["my_plot"][0]

    # Attach some tools to the plot
    my_plot.tools.append(
        ScatterInspector(
            my_plot, selection_mode="toggle", persistent_hover=False
        )
    )
    my_plot.overlays.append(
        ScatterInspectorOverlay(
            my_plot,
            hover_color="transparent",
            hover_marker_size=10,
            hover_outline_color="purple",
            hover_line_width=2,
            selection_marker_size=8,
            selection_color="lawngreen",
        )
    )

    my_plot.tools.append(PanTool(my_plot))
    my_plot.overlays.append(ZoomTool(my_plot, drag_button="right"))

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
        VGroup(
            HGroup(spring, Label("Click point to select/unselect"), spring),
            Item(
                "plot",
                editor=ComponentEditor(size=size, bgcolor=bgcolor),
                show_label=False,
            ),
            orientation="vertical",
        ),
        resizable=True,
        title=title,
    )

    def _metadata_handler(self, event):
        sel_indices = self.index_datasource.metadata.get("selections", [])
        print("Selection indices:", sel_indices)

        hover_indices = self.index_datasource.metadata.get("hover", [])
        print("Hover indices:", hover_indices)

    def _plot_default(self):
        plot = _create_plot_component()

        # Retrieve the plot hooked to the tool.
        my_plot = plot.plots["my_plot"][0]

        # Set up the trait handler for the selection
        self.index_datasource = my_plot.index
        self.index_datasource.observe(
            self._metadata_handler, "metadata_changed"
        )

        return plot


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
