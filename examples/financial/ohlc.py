"""
Implementation of a standard financial plot visualization using Chaco
renderers and scales.
"""

# Major library imports
from numpy import abs, arange, cumprod, linspace, random, argmin, choose, vstack
import time

# Enthought library imports
from enthought.enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Enum
from traitsui.api import View, VGroup, Item, EnumEditor

# Chaco imports
from enthought.chaco.api import ArrayDataSource, DataRange1D, \
        LinearMapper, PlotAxis, add_default_grids, OverlayPlotContainer
from enthought.chaco.tools.api import PanTool, ZoomTool
from enthought.chaco.scales.api import CalendarScaleSystem
from enthought.chaco.scales_tick_generator import ScalesTickGenerator

try:
    from enthought.chaco.hloc_renderer import OHLCPlot, PriceDataSource, \
            CandleOHLCPlot, HeikinAshiPlot
except ImportError:
    try:
        from ohlc_renderer import OHLCPlot, PriceDataSource, \
                CandleOHLCPlot, HeikinAshiPlot
    except ImportError:
        raise ImportError, "Missing HLOC renderer module, unable to run this demo"

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

class MyApp(HasTraits):

    container = Instance(Component)
    plottype = Enum("OHLC", "Candlestick", "Heikin Ashi")
    view = View(VGroup(
                    Item("plottype", show_label=False, width=-250),
                    Item("container", editor=ComponentEditor(size=(800,600)),
                         show_label=False)
                    ),
                resizable = True,
                title = "OHLC Plot")

    _renderer_map = {"OHLC": OHLCPlot,
                     "Candlestick": CandleOHLCPlot,
                     "Heikin Ashi": HeikinAshiPlot}

    def _plottype_changed(self):
        oldplot = self.plot
        newplot = self._create_plot(oldplot.index, oldplot.prices)
        newplot.index_range.set_bounds(oldplot.index_range.low, oldplot.index_range.high)
        self.container.remove(oldplot)
        self.container.add(newplot)
        self.container.request_redraw()
        self.plot = newplot

    def _create_plot(self, times, prices):
        cls = self._renderer_map[self.plottype]
        if self.plot is None:
            index_mapper = LinearMapper(range=DataRange1D(times))
            value_mapper = LinearMapper(range=DataRange1D(prices))
        else:
            index_mapper = self.plot.index_mapper
            value_mapper = self.plot.value_mapper
        price_plot = cls(times = times, prices = prices,
                        index_mapper = index_mapper,
                        value_mapper = value_mapper,
                        bgcolor = "white",
                        border_visible = True)

        # Set the plot's bottom axis to use the Scales ticking system
        ticker = ScalesTickGenerator(scale=CalendarScaleSystem())
        bottom_axis = PlotAxis(price_plot, orientation="bottom",
                               tick_generator = ticker)
        price_plot.overlays.append(bottom_axis)
        price_plot.overlays.append(PlotAxis(price_plot, orientation="left"))
        hgrid, vgrid = add_default_grids(price_plot)
        vgrid.tick_generator = bottom_axis.tick_generator

        # Add pan and zoom
        price_plot.tools.append(PanTool(price_plot, constrain=True,
                                        constrain_direction="x"))
        price_plot.overlays.append(
                ZoomTool(price_plot, drag_button="right", always_on=True,
                         tool_mode="range", axis="index"))

        return price_plot

    def _container_default(self):
        self.plot = None

        # Create the data and datasource objects
        # In order for the date axis to work, the index data points need to
        # be in units of seconds since the epoch.  This is because we are using
        # the CalendarScaleSystem, whose formatters interpret the numerical values
        # as seconds since the epoch.
        numpoints = 500
        index = create_dates(numpoints)

        returns = random.lognormal(0.00, 0.04, size=numpoints)
        average = 100.0 * cumprod(returns)
        high = average + abs(random.normal(0, 20.0, size=numpoints))
        low = average - abs(random.normal(0, 20.0, size=numpoints))
        delta = high - low
        open = low + delta * random.uniform(0.05, 0.95, size=numpoints)
        close = low + delta * random.uniform(0.05, 0.95, size=numpoints)
        price = vstack((open, high, low, close, average))

        time_ds = ArrayDataSource(index)
        price_ds = PriceDataSource(price, sort_order="none")

        # Create the price plot
        price_plot = self._create_plot(time_ds, price_ds)
        self.plot = price_plot

        container = OverlayPlotContainer(padding=35)
        container.add(price_plot)
        return container

demo = MyApp()
if __name__ == "__main__":
    demo.configure_traits()
