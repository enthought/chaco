#!/usr/bin/env python
"""
Demonstrates the LinearRegression tool
"""

# Major library imports
from numpy import arange, sort, compress, arange
from numpy.random import random

# Enthought library imports
from enthought.enable2.wx_backend.api import Window

# Chaco imports
from enthought.chaco2.example_support import DemoFrame, demo_main
from enthought.chaco2.api import AbstractDataSource, ArrayPlotData, Plot
from enthought.chaco2.tools.api import RegressionLasso, RegressionOverlay, \
     PanTool, SimpleZoom


class PlotFrame(DemoFrame):

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
        lasso_selection = RegressionLasso(component=my_plot,
                                          selection_datasource=my_plot.index)
        my_plot.tools.append(lasso_selection)
        lasso_overlay = RegressionOverlay(lasso_selection=lasso_selection,
                                     component=my_plot)
        my_plot.overlays.append(lasso_overlay)

        my_plot.tools.append(PanTool(my_plot, drag_button="right"))
        my_plot.overlays.append(SimpleZoom(my_plot))

        # Return a window containing our plot container
        return Window(self, -1, component=plot, bg_color="lightgray")


if __name__ == "__main__":
    demo_main(PlotFrame, size=(650,650), title="Scatter plot with selection")

# EOF
