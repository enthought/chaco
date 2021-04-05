# -*- coding: utf-8 -*-
"""
Minard's Map of Napoleon's Russian Campaign
===========================================

A Chaco version of Minard's visualization, as popularized by Edward Tufte.

This shows the use of segment plots, text plots and 1d line scatter plots.

Data is adapted from http://mbostock.github.io/protovis/ex/napoleon.html and
http://www.datavis.ca/gallery/minard/minard.txt
"""

import numpy as np

from chaco.api import ArrayPlotData, Plot, VPlotContainer, viridis
from chaco.tools.api import PanTool, ZoomTool
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View


# town locations
towns = np.array(
    [
        (24.0, 55.0, u"Kowno"),
        (25.3, 54.7, u"Wilna"),
        (26.4, 54.4, u"Smorgoni"),
        (26.8, 54.3, u"Molodexno"),
        (27.7, 55.2, u"Gloubokoe"),
        (27.6, 53.9, u"Minsk"),
        (28.5, 54.3, u"Studienska"),
        (28.7, 55.5, u"Polotzk"),
        (29.2, 54.4, u"Bobr"),
        (30.2, 55.3, u"Witebsk"),
        (30.4, 54.5, u"Orscha"),
        (30.4, 53.9, u"Mohilow"),
        (32.0, 54.8, u"Smolensk"),
        (33.2, 54.9, u"Dorogobouge"),
        (34.3, 55.2, u"Wixma"),
        (34.4, 55.5, u"Chjat"),
        (36.0, 55.5, u"Mojaisk"),
        (37.6, 55.8, u"Moscou"),
        (36.6, 55.3, u"Tarantino"),
        (36.5, 55.0, u"Malo-jarosewli"),
    ],
    dtype=[("lon", "f4"), ("lat", "f4"), ("town", "U12")],
)


# Temperature data for Napoleon's retreat.
temperatures = np.array(
    [
        ("Oct 18", 37.6, 0),
        ("Oct 24", 36.0, 0),
        ("Nov 09", 33.2, -9),
        ("Nov 14", 32.0, -21),
        ("Nov 24", 29.2, -11),
        ("Nov 28", 28.5, -20),
        ("Dec 01", 27.2, -24),
        ("Dec 06", 26.7, -30),
        ("Dec 07", 25.3, -26),
    ],
    dtype=[("date", "U6"), ("lon", float), ("temp", float)],
)


# Army sizes
army = np.array(
    [
        (24.5, 55.0, 24.6, 55.8, 22000, 1, 3),
        (25.5, 54.6, 26.6, 55.7, 60000, 1, 2),
        (26.6, 55.7, 27.4, 55.6, 40000, 1, 2),
        (27.4, 55.6, 28.7, 55.5, 33000, 1, 2),
        (24.0, 54.9, 24.5, 55.0, 422000, 1, 1),
        (24.5, 55.0, 25.5, 54.6, 400000, 1, 1),
        (25.5, 54.6, 26.0, 54.7, 340000, 1, 1),
        (26.0, 54.7, 27.0, 54.8, 320000, 1, 1),
        (27.0, 54.8, 28.0, 54.9, 300000, 1, 1),
        (28.0, 54.9, 28.5, 55.0, 280000, 1, 1),
        (28.5, 55.0, 29.0, 55.1, 240000, 1, 1),
        (29.0, 55.1, 30.0, 55.2, 210000, 1, 1),
        (30.0, 55.2, 30.3, 55.3, 180000, 1, 1),
        (30.3, 55.3, 32.0, 54.8, 175000, 1, 1),
        (32.0, 54.8, 33.2, 54.9, 145000, 1, 1),
        (33.2, 54.9, 34.4, 55.5, 140000, 1, 1),
        (34.4, 55.5, 35.5, 55.4, 127100, 1, 1),
        (35.5, 55.4, 36.0, 55.5, 100000, 1, 1),
        (36.0, 55.5, 37.6, 55.8, 100000, 1, 1),
        (37.6, 55.8, 37.0, 55.0, 98000, -1, 1),
        (37.0, 55.0, 36.8, 55.0, 97000, -1, 1),
        (36.8, 55.0, 35.4, 55.3, 96000, -1, 1),
        (35.4, 55.3, 34.3, 55.2, 87000, -1, 1),
        (34.3, 55.2, 33.2, 54.9, 55000, -1, 1),
        (33.2, 54.9, 32.0, 54.8, 37000, -1, 1),
        (32.0, 54.8, 30.4, 54.4, 24000, -1, 1),
        (30.4, 54.4, 29.2, 54.4, 20000, -1, 1),
        (29.2, 54.4, 28.5, 54.3, 50000, -1, 1),
        (28.5, 54.3, 28.3, 54.3, 50000, -1, 1),
        (28.3, 54.3, 27.5, 54.5, 48000, -1, 1),
        (27.5, 54.5, 26.8, 54.3, 40000, -1, 1),
        (26.8, 54.3, 26.4, 54.4, 12000, -1, 1),
        (26.4, 54.4, 24.6, 54.5, 14000, -1, 1),
        (24.6, 54.5, 24.4, 54.4, 8000, -1, 1),
        (24.4, 54.4, 24.2, 54.4, 4000, -1, 1),
        (24.2, 54.4, 24.1, 54.4, 10000, -1, 1),
        (28.7, 55.5, 29.2, 54.4, 30000, -1, 2),
        (24.6, 55.8, 24.2, 54.4, 6000, -1, 3),
    ],
    dtype=[
        ("start_lon", float),
        ("start_lat", float),
        ("end_lon", float),
        ("end_lat", float),
        ("size", float),
        ("direction", float),
        ("group", float),
    ],
)


def _create_plot_component():
    army_lat = np.column_stack([army["start_lat"], army["end_lat"]]).reshape(-1)
    army_lon = np.column_stack([army["start_lon"], army["end_lon"]]).reshape(-1)

    plot_data = ArrayPlotData(
        army_lon=army_lon,
        army_lat=army_lat,
        army_size=army["size"],
        army_color=army["direction"] * army["group"],
        towns_lat=towns["lat"],
        towns_lon=towns["lon"],
        towns=towns["town"],
        temp_lon=temperatures["lon"],
        temp=temperatures["temp"],
        temp_date=temperatures["date"],
    )

    map_plot = Plot(plot_data)
    map_plot.x_grid = None
    map_plot.y_grid = None
    map_plot.x_axis.orientation = "top"
    map_plot.x_axis.title = "Longitude"
    map_plot.y_axis.title = "Latitude"
    map_plot.title = "Minard's Map of Napoleon's Russian Campaign"
    map_plot._title.overlay_position = "inside top"
    map_plot._title.hjustify = "left"
    map_plot._title.vjustify = "bottom"
    map_plot.plot(
        ("army_lon", "army_lat", "army_color", "army_size"),
        type="cmap_segment",
        name="my_plot",
        color_mapper=viridis,
        border_visible=True,
        bgcolor="white",
        size_min=1.0,
        size_max=128.0,
    )
    map_plot.plot(
        ("towns_lon", "towns_lat"),
        type="scatter",
    )
    map_plot.plot(
        ("towns_lon", "towns_lat", "towns"),
        type="text",
        text_margin=4,
        h_position="right",
        text_offset=(4, 0),
    )
    map_plot.plot_1d(
        ("temp_lon"),
        type="line_scatter_1d",
        alpha=0.5,
        line_style="dot",
    )
    map_plot.index_range.high_setting = 38
    map_plot.index_range.low_setting = 23
    map_plot.value_range.high_setting = 56.0
    map_plot.value_range.low_setting = 53.5
    map_plot.tools.extend(
        [
            PanTool(map_plot),
            ZoomTool(map_plot),
        ]
    )

    temp_plot = Plot(plot_data, height=100)
    temp_plot.index_range = map_plot.index_range
    temp_plot.x_grid = None
    temp_plot.x_axis = None
    temp_plot.y_axis.orientation = "right"
    temp_plot.y_axis.title = u"Temp (°Re)"
    temp_plot.plot(
        ("temp_lon", "temp"),
        type="line",
    )
    temp_plot.plot_1d(
        ("temp_lon"),
        type="line_scatter_1d",
        alpha=0.5,
        line_style="dot",
    )
    temp_plot.plot_1d(
        ("temp_lon", "temp_date"),
        type="textplot_1d",
        alpha=0.5,
        line_style="dot",
        alignment="bottom",
    )
    temp_plot.value_range.high_setting = 5
    temp_plot.value_range.low_setting = -35

    container = VPlotContainer(temp_plot, map_plot)
    container.spacing = 0
    map_plot.padding_bottom = 0
    map_plot.padding_left = 70
    map_plot.padding_right = 70
    map_plot.padding_top = 50
    temp_plot.padding_top = 0
    temp_plot.padding_bottom = 15
    temp_plot.padding_right = 70
    temp_plot.padding_left = 70
    temp_plot.height = 100
    temp_plot.resizable = "h"

    return container


size = (1280, 720)
title = "Minard's Map of Napoleon's Russian Campaign"


class Demo(HasTraits):

    plot = Instance(Component)

    def _plot_default(self):
        return _create_plot_component()

    traits_view = View(
        Item(
            "plot",
            editor=ComponentEditor(size=size),
            show_label=False,
        ),
        title=title,
    )


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
