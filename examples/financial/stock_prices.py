"""
Implementation of a standard financial plot visualization using Chaco 
renderers and scales.

In the main price plot area, mouse wheel zooms and mouse drag pans (if
the plot is not at the edge of the time series data).  In the bottom 
overview plot area, right-click-drag selects a range of times to display
on the top two plots.  Once a region is selected, it can be moved
around by left-dragging or resized by left-dragging one of its
edges.
"""

# Major library imports
from numpy import abs, arange, cumprod, linspace, random
import time

from enthought.chaco.example_support import COLOR_PALETTE
from enthought.enable.example_support import DemoFrame, demo_main

# Enthought library imports
from enthought.enable.api import Window

# Chaco imports
from enthought.chaco.api import ArrayDataSource, BarPlot, DataRange1D, \
        LinePlot, LinearMapper, VPlotContainer, PlotAxis, PlotLabel, \
        FilledLinePlot, add_default_grids
from enthought.chaco.tools.api import PanTool, ZoomTool, RangeSelection, \
        RangeSelectionOverlay

from enthought.chaco.scales.api import CalendarScaleSystem
from enthought.chaco.scales_tick_generator import ScalesTickGenerator


def create_dates(numpoints, units="days"):
    """ Returns **numpoints** number of dates that evenly bracket the current
    date and time.  **units** should be one of "weeks", "days", "hours"
    "minutes", or "seconds".
    """
    units_map = { "weeks" : 7*24*3600,
                  "days" : 24*3600,
                  "hours" : 3600,
                  "minutes" : 60,
                  "seconds" : 1 }
    now = time.time()
    dt = units_map[units]
    dates = linspace(now, now+numpoints*dt, numpoints)
    return dates


class PlotFrame(DemoFrame):

    def _create_price_plots(self, times, prices, mini_height=75):
        """ Creates the two plots of prices and returns them.  One of the
        plots can be zoomed and panned, and the other plot (smaller) always
        shows the full data.
        
        *dates* and *prices* are two data sources.
        """

        # Create the price plot
        price_plot = FilledLinePlot(index = times, value = prices,
                        index_mapper = LinearMapper(range=DataRange1D(times)),
                        value_mapper = LinearMapper(range=DataRange1D(prices)), 
                        edge_color = "blue",
                        face_color = "paleturquoise",
                        bgcolor = "white",
                        border_visible = True)

        # Add pan and zoom
        price_plot.tools.append(PanTool(price_plot, constrain=True,
                                        constrain_direction="x"))
        price_plot.overlays.append(ZoomTool(price_plot, drag_button="right",
                                              always_on=True,
                                              tool_mode="range",
                                              axis="index",
                                              max_zoom_out_factor=1.0,
                                             ))

        # Create the miniplot
        miniplot = LinePlot(index = times, value = prices,
                        index_mapper = LinearMapper(range=DataRange1D(times)),
                        value_mapper = LinearMapper(range=DataRange1D(prices)),  
                        color = "black",
                        border_visible = True,
                        bgcolor = "white",
                        height = mini_height,
                        resizable = "h")

        # Add a range overlay to the miniplot that is hooked up to the range
        # of the main price_plot
        range_tool = RangeSelection(miniplot)
        miniplot.tools.append(range_tool)
        range_overlay = RangeSelectionOverlay(miniplot, metadata_name="selections")
        miniplot.overlays.append(range_overlay)
        range_tool.on_trait_change(self._range_selection_handler, "selection")

        # Attach a handler that sets the tool when the plot's index range changes
        self.range_tool = range_tool
        price_plot.index_range.on_trait_change(self._plot_range_handler, "updated")

        return price_plot, miniplot
        

    def _range_selection_handler(self, event):
        # The event obj should be a tuple (low, high) in data space
        if event is not None:
            low, high = event
            self.price_plot.index_range.low = low
            self.price_plot.index_range.high = high
        else:
            self.price_plot.index_range.set_bounds("auto", "auto")

    def _plot_range_handler(self, event):
        if event is not None:
            low, high = event
            if "auto" not in (low, high):
                self.range_tool.selection = (low, high)

    def _create_vol_plot(self, times, volumes, height=100):
        "Creates and returns the volume plot"
        index_range = self.price_plot.index_range
        vol_plot = BarPlot(index = times, value = volumes,
                       index_mapper = LinearMapper(range=index_range),
                       value_mapper = LinearMapper(range=DataRange1D(volumes)),
                       line_color = "transparent",
                       fill_color = "black",
                       bar_width = 1.0,
                       bar_width_type = "screen",
                       antialias = False,
                       height = 100,
                       resizable = "h",
                       bgcolor = "white",
                       border_visible = True)
        vol_plot.tools.append(PanTool(vol_plot, constrain=True,
                                      constrain_direction="x"))
        return vol_plot

    def _create_window(self):
       
        # Create the data and datasource objects
        # In order for the date axis to work, the index data points need to 
        # be in units of seconds since the epoch.  This is because we are using
        # the CalendarScaleSystem, whose formatters interpret the numerical values
        # as seconds since the epoch.  
        numpoints = 500
        index = create_dates(numpoints)
        returns = random.lognormal(0.01, 0.1, size=numpoints)
        price = 100.0 * cumprod(returns)       
        volume = abs(random.normal(1000.0, 1500.0, size=numpoints) + 2000.0)

        time_ds = ArrayDataSource(index)
        vol_ds = ArrayDataSource(volume, sort_order="none")
        price_ds = ArrayDataSource(price, sort_order="none")

        # Create the price plots
        price_plot, mini_plot = self._create_price_plots(time_ds, price_ds)
        price_plot.index_mapper.domain_limits = (index[0], index[-1])
        self.price_plot = price_plot
        self.mini_plot = mini_plot

        # Create the volume plot
        vol_plot = self._create_vol_plot(time_ds, vol_ds)
        vol_plot.index_mapper.domain_limits = (index[0], index[-1])

        # Set the plot's bottom axis to use the Scales ticking system
        ticker = ScalesTickGenerator(scale=CalendarScaleSystem())
        for plot in price_plot, mini_plot, vol_plot:
            bottom_axis = PlotAxis(plot, orientation="bottom", 
                                   tick_generator = ticker)
            plot.overlays.append(bottom_axis)
            plot.overlays.append(PlotAxis(plot, orientation="left"))
            hgrid, vgrid = add_default_grids(plot)
            vgrid.tick_generator = bottom_axis.tick_generator

        container = VPlotContainer(bgcolor = "lightgray",
                                   spacing = 40, 
                                   padding = 50,
                                   fill_padding=False)
        container.add(mini_plot, vol_plot, price_plot)
        
        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,600), title="Stock price and volume")
