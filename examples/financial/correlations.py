
from numpy import linspace, random, zeros, arange, cumprod
import time

# ETS imports (non-chaco)
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance, Int, List, Str, Enum, \
        on_trait_change, Any
from enthought.traits.ui.api import Item, View, HSplit, VGroup, EnumEditor

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot, ScatterInspectorOverlay
from enthought.chaco.scales.api import CalendarScaleSystem
from enthought.chaco.scales_tick_generator import ScalesTickGenerator
from enthought.chaco.scales_axis import PlotAxis as ScalesPlotAxis
from enthought.chaco.example_support import COLOR_PALETTE
from enthought.chaco.tools.api import PanTool, ZoomTool, RangeSelection, \
        RangeSelectionOverlay, LegendTool


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

class PlotApp(HasTraits):

    plotdata = Instance(ArrayPlotData)
    numpoints = Int(300)
    symbols = List

    sym1 = Enum(values="symbols")
    sym2 = Enum(values="symbols")

    returns_plot = Instance(Plot)
    times_ds = Any()   # arraydatasource for the time axis data
    corr_plot = Instance(Plot)
    corr_renderer = Any()

    traits_view = View(
            HSplit(
                Item('returns_plot', editor=ComponentEditor(), 
                    show_label = False),
                VGroup(
                    VGroup(
                        Item('sym1', width=-225),
                        Item('sym2', width=-225),
                    ),
                    Item('corr_plot', editor=ComponentEditor(),
                        show_label = False, width=-275),
                ),
            ),
            width=1024, height=500,
            resizable=True,
            title = "Correlations of returns")

    def __init__(self, *symbols, **kwtraits):
        super(PlotApp, self).__init__(symbols=list(symbols), **kwtraits)
        self._create_data(*symbols)
        self._create_returns_plot()
        self._create_corr_plot()
        if len(self.symbols) > 1:
            self.sym2 = self.symbols[1]

        return

    def _create_returns_plot(self):
        plot = Plot(self.plotdata)
        plot.legend.visible = True
        #FIXME: The legend move tool doesn't seem to quite work right now
        #plot.legend.tools.append(LegendTool(plot.legend))
        plot.x_axis = None
        x_axis = ScalesPlotAxis(plot, orientation="bottom",
                        tick_generator=ScalesTickGenerator(scale=CalendarScaleSystem()))
        plot.overlays.append(x_axis)
        plot.x_grid.tick_generator = x_axis.tick_generator
        for i, name in enumerate(self.plotdata.list_data()):
            if name == "times":
                continue
            renderer = plot.plot(("times", name), type="line", name=name,
                                  color=tuple(COLOR_PALETTE[i]))[0]
        
        # Tricky: need to set auto_handle_event on the RangeSelection
        # so that it passes left-clicks to the PanTool
        # FIXME: The range selection is still getting the initial left down
        renderer.tools.append(RangeSelection(renderer, auto_handle_event = False))
        plot.tools.append(PanTool(plot, constrain=True, constrain_direction="x"))
        plot.overlays.append(ZoomTool(plot, tool_mode="range", max_zoom_out=1.0)) 
        # Attach the range selection to the last renderer; any one will do
        renderer.overlays.append(RangeSelectionOverlay(renderer,
                                    metadata_name="selections"))
        # Grab a reference to the Time axis datasource and add a listener to its
        # selections metadata
        self.times_ds = renderer.index
        self.times_ds.on_trait_change(self._selections_changed, 'metadata_changed')
        self.returns_plot = plot

    def _create_corr_plot(self):
        plot = Plot(self.plotdata, padding=0)
        plot.padding_left = 25
        plot.padding_bottom = 25
        plot.tools.append(PanTool(plot))
        plot.overlays.append(ZoomTool(plot))
        self.corr_plot = plot

    def _create_data(self, *names):
        numpoints = self.numpoints
        plotdata = ArrayPlotData(times = create_dates(numpoints))
        for name in names:
            plotdata.set_data(name, cumprod(random.lognormal(0.0, 0.04, size=numpoints)))
        self.plotdata = plotdata

    def _selections_changed(self, event):
        if self.corr_renderer is None:
            return
        if not isinstance(event, dict) or "selections" not in event:
            return
        corr_index = self.corr_renderer.index
        selections = event["selections"]
        if selections is None:
            corr_index.metadata.pop("selections", None)
            return
        else:
            low, high = selections
            data = self.times_ds.get_data()
            low_ndx = data.searchsorted(low)
            high_ndx = data.searchsorted(high)
            corr_index.metadata["selections"] = arange(low_ndx, high_ndx+1, 1, dtype=int)
            self.corr_plot.request_redraw()

    @on_trait_change("sym1,sym2")
    def _update_corr_symbols(self):
        plot = self.corr_plot
        if self.corr_renderer is not None:
            # Remove the old one
            plot.remove(self.corr_renderer)
            self.corr_renderer = None

        self.corr_renderer = plot.plot((self.sym1, self.sym2), 
                                type="scatter", color="blue")[0]
        self.corr_renderer.overlays.append(ScatterInspectorOverlay(self.corr_renderer,
                selection_color = "lightgreen"))
        plot.request_redraw()



if __name__ == "__main__":
    PlotApp("AAPL", "GOOG", "MSFT").configure_traits()

