"""
Implementation of a standard financial plot visualization using Chaco
renderers and scales.  This differs from the financial_plot.py example
in that it uses a date-oriented axis.
"""

# Major library imports
from numpy import abs, cumprod, linspace, random
import time

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import (
    ArrayDataSource,
    BarPlot,
    DataRange1D,
    LinearMapper,
    VPlotContainer,
    PlotAxis,
    FilledLinePlot,
    add_default_grids,
    PlotLabel,
)
from chaco.tools.api import PanTool, ZoomTool


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
def _create_plot_component():

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

    xmapper = LinearMapper(range=DataRange1D(time_ds))
    vol_mapper = LinearMapper(range=DataRange1D(vol_ds))
    price_mapper = LinearMapper(range=DataRange1D(price_ds))

    price_plot = FilledLinePlot(
        index=time_ds,
        value=price_ds,
        index_mapper=xmapper,
        value_mapper=price_mapper,
        edge_color="blue",
        face_color="paleturquoise",
        bgcolor="white",
        border_visible=True,
    )
    price_plot.overlays.append(PlotAxis(price_plot, orientation="left")),

    # Set the plot's bottom axis to use the Scales ticking system
    bottom_axis = PlotAxis(
        price_plot,
        orientation="bottom",  # mapper=xmapper,
        tick_generator=ScalesTickGenerator(scale=CalendarScaleSystem()),
    )
    price_plot.overlays.append(bottom_axis)
    hgrid, vgrid = add_default_grids(price_plot)
    vgrid.tick_generator = bottom_axis.tick_generator

    price_plot.tools.append(
        PanTool(
            price_plot,
            constrain=True,
            constrain_direction="x",
            restrict_to_data=True,
        )
    )
    price_plot.overlays.append(
        ZoomTool(
            price_plot,
            drag_button="right",
            always_on=True,
            tool_mode="range",
            axis="index",
            max_zoom_out_factor=10.0,
            x_min_zoom_factor=float(1e-3),
        )
    )

    vol_plot = BarPlot(
        index=time_ds,
        value=vol_ds,
        index_mapper=xmapper,
        value_mapper=vol_mapper,
        line_color="transparent",
        fill_color="black",
        bar_width=1.0,
        bar_width_type="screen",
        antialias=False,
        height=100,
        resizable="h",
        bgcolor="white",
        border_visible=True,
    )

    hgrid, vgrid = add_default_grids(vol_plot)
    # Use the same tick generator as the x-axis on the price plot
    vgrid.tick_generator = bottom_axis.tick_generator
    vol_plot.underlays.append(PlotAxis(vol_plot, orientation="left"))
    vol_plot.tools.append(
        PanTool(vol_plot, constrain=True, constrain_direction="x")
    )

    container = VPlotContainer(
        bgcolor="lightblue", spacing=40, padding=50, fill_padding=False
    )
    container.add(vol_plot)
    container.add(price_plot)
    container.overlays.append(
        PlotLabel(
            "Financial Plot with Date Axis",
            component=container,
            # font="Times New Roman 24"))
            font="Arial 24",
        )
    )

    return container


# ===============================================================================
# Attributes to use for the plot view.
size = (800, 600)
title = "Financial plot example"

# ===============================================================================
# # Demo class that is used by the demo.py application.
# ===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
        Group(
            Item("plot", editor=ComponentEditor(size=size), show_label=False),
            orientation="vertical",
        ),
        resizable=True,
        title=title,
        width=size[0],
        height=size[1],
    )

    def _plot_default(self):
        return _create_plot_component()


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
