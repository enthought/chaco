"""
Implementation of a sample horizon plot, showing both negative and positive
values in the same banded region.
"""

# Major library imports
from numpy import cumprod, linspace, random
import time

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    LinearMapper,
    DataRange1D,
    HPlotContainer,
    OverlayPlotContainer,
    PlotGrid,
    PlotAxis,
    FilledLinePlot,
    BandedMapper,
    HorizonPlot,
    ColorBar,
    RdBu as cmap,
)
from chaco.tools.api import PanTool

from chaco.scales.api import CalendarScaleSystem
from chaco.scales_tick_generator import ScalesTickGenerator


def create_dates(numpoints, units="days"):
    """Returns **numpoints** number of dates that evenly bracket the current
    date and time.  **units** should be one of "weeks", "days", "hours"
    "minutes", or "seconds".
    """
    units_map = {
        "weeks": 7 * 24 * 3600,
        "days": 24 * 3600,
        "hours": 3600,
        "minutes": 60,
        "seconds": 1,
    }
    now = time.time()
    dt = units_map[units]
    dates = linspace(now, now + numpoints * dt, numpoints)
    return dates


# ===============================================================================
# # Create the Chaco plot.
# ===============================================================================
def _create_plot_components():
    # Create the data and datasource objects
    # In order for the date axis to work, the index data points need to
    # be in units of seconds since the epoch.  This is because we are using
    # the CalendarScaleSystem, whose formatters interpret the numerical values
    # as seconds since the epoch.
    high = 1.0
    numpoints = 5000

    random.seed(1000)

    index = create_dates(numpoints)
    price = 100 * cumprod(random.lognormal(0.0, 0.04, size=numpoints))
    changes = price / price[0] - 1.0

    index_ds = ArrayDataSource(index)
    value_ds = ArrayDataSource(changes, sort_order="none")
    value_range = DataRange1D(value_ds, low=-high, high=high)

    index_mapper = LinearMapper(
        range=DataRange1D(index_ds), stretch_data=False
    )

    horizon = HorizonPlot(
        bands=4,
        index=index_ds,
        value=value_ds,
        index_mapper=index_mapper,
        value_mapper=BandedMapper(range=DataRange1D(low=0, high=high)),
        color_mapper=cmap(range=value_range),
    )
    horizon.tools.append(
        PanTool(horizon, constrain=True, constrain_direction="x")
    )
    axis = PlotAxis(
        mapper=horizon.value_mapper,
        component=horizon,
        orientation="left",
        tick_label_position="outside",
    )
    horizon.overlays.append(axis)

    bottom_axis = PlotAxis(
        horizon,
        orientation="bottom",
        tick_generator=ScalesTickGenerator(scale=CalendarScaleSystem()),
    )
    horizon.overlays.append(bottom_axis)

    filled = FilledLinePlot(
        index=index_ds,
        value=value_ds,
        index_mapper=index_mapper,
        value_mapper=LinearMapper(range=value_range, stretch_data=False),
        fill_color=(0.81960784, 0.89803922, 0.94117647),
        edge_color="transparent",
    )
    filled.tools.append(
        PanTool(filled, constrain=True, constrain_direction="x")
    )
    axis = PlotAxis(
        mapper=filled.value_mapper,
        component=filled,
        orientation="left",
        tick_label_position="outside",
    )
    filled.overlays.append(axis)

    grid = PlotGrid(
        mapper=filled.value_mapper,
        component=filled,
        orientation="horizontal",
        line_color="lightgray",
        line_style="dot",
    )
    filled.underlays.append(grid)

    colormap = horizon.color_mapper
    colorbar = ColorBar(
        index_mapper=LinearMapper(range=colormap.range),
        color_mapper=colormap,
        orientation="v",
        resizable="v",
        width=20,
        padding=20,
    )

    padding = (40, 20, 0, 0)
    over1 = HPlotContainer(
        use_backbuffer=True, padding=padding, padding_top=20
    )
    over1.add(filled)
    over1.add(colorbar)

    over2 = OverlayPlotContainer(padding=padding, padding_bottom=40)
    over2.add(horizon)

    return over1, over2


filled_size = (800, 220)
horizon_size = (800, 70)
title = "Horizon plot example"

# ===============================================================================
# # Demo class that is used by the demo.py application.
# ===============================================================================
class Demo(HasTraits):
    filled = Instance(Component)
    horizon = Instance(Component)

    traits_view = View(
        Group(
            Item(
                "filled",
                editor=ComponentEditor(size=filled_size),
                show_label=False,
            ),
            Item(
                "horizon",
                editor=ComponentEditor(size=horizon_size),
                show_label=False,
            ),
            orientation="vertical",
        ),
        resizable=False,
        title=title,
        width=filled_size[0],
        height=filled_size[1] + horizon_size[1],
    )


demo = Demo()

if __name__ == "__main__":

    filled, horizon = _create_plot_components()
    demo.horizon = horizon
    demo.filled = filled
    demo.configure_traits()
