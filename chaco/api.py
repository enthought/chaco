# (C) Copyright 2006-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
"""
Defines the publicly accessible items of the Chaco API.

Base
----

- :attr:`~.NumericalSequenceTrait`
- :attr:`~.PointTrait`
- :attr:`~.ImageTrait`
- :attr:`~.DimensionTrait`
- :attr:`~.SortOrderTrait`
- :func:`~.bin_search`
- :func:`~.reverse_map_1d`
- :func:`~.right_shift`
- :func:`~.left_shift`
- :func:`~.sort_points`
- :func:`~.find_runs`
- :func:`~.arg_find_runs`
- :func:`~.point_line_distance`

Data Model
----------

- :class:`~.AbstractDataSource`
- :class:`~.ArrayDataSource`
- :class:`~.GridDataSource`
- :class:`~.ImageData`
- :class:`~.MultiArrayDataSource`
- :class:`~.PointDataSource`
- :class:`~.AbstractDataRange`
- :class:`~.BaseDataRange`
- :class:`~.DataRange1D`
- :class:`~.DataRange2D`

Mappers
-------

- :class:`~.AbstractMapper`
- :class:`~.Base1DMapper`
- :class:`~.GridMapper`
- :class:`~.LogMapper`
- :class:`~.LinearMapper`
- :class:`~.ColorMapper`
- :class:`~.ColorMapTemplate`
- :class:`~.DiscreteColorMapper`
- :class:`~.TransformColorMapper`
- :class:`~.BandedMapper`

Visual Components
-----------------

- :class:`~.AbstractPlotRenderer`
- :class:`~.AbstractOverlay`
- :class:`~.BasePlotContainer`
- :class:`~.BasePlotFrame`
- :class:`~.CrossPlotFrame`
- :class:`~.DataView`
- :class:`~.SimplePlotFrame`
- :class:`~.PlotComponent`
- :class:`~.PlotGraphicsContext`
- :class:`~.PlotGraphicsContextMixin`
- :class:`~.OverlayPlotContainer`
- :class:`~.HPlotContainer`
- :class:`~.VPlotContainer`
- :class:`~.GridPlotContainer`
- :class:`~.Label`
- :class:`~.PlotLabel`
- :class:`~.Legend`
- :class:`~.ToolTip`
- :class:`~.DataLabel`
- :class:`~.LassoOverlay`
- :class:`~.ColorBar`
- :class:`~.TextBoxOverlay`
- :class:`~.ScatterInspectorOverlay`
- :class:`~.ColormappedSelectionOverlay`

Renderers
---------

- :class:`~.BarPlot`
- :class:`~.Base1DPlot`
- :class:`~.Base2DPlot`
- :class:`~.BaseXYPlot`
- :class:`~.ScatterPlot`
- :func:`~.render_markers`
- :class:`~.ImagePlot`
- :class:`~.CMapImagePlot`
- :class:`~.ContourLinePlot`
- :class:`~.ContourPolyPlot`
- :class:`~.LinePlot`
- :class:`~.ColormappedScatterPlot`
- :class:`~.PolygonPlot`
- :class:`~.ErrorBarPlot`
- :class:`~.FilledLinePlot`
- :class:`~.QuiverPlot`
- :class:`~.CandlePlot`
- :class:`~.MultiLinePlot`
- :class:`~.JitterPlot`
- :class:`~.VariableSizeScatterPlot`
- :class:`~.HorizonPlot`
- :class:`~.ScatterPlot1D`
- :class:`~.LineScatterPlot1D`
- :class:`~.TextPlot1D`
- :class:`~.SegmentPlot`
- :class:`~.TextPlot`

Plot Factories
--------------

- :func:`~.create_bar_plot`
- :func:`~.create_line_plot`
- :func:`~.create_scatter_plot`
- :func:`~.create_polar_plot`
- :func:`~.add_default_axes`
- :func:`~.add_default_grids`

- :class:`~.AbstractPlotData`
- :class:`~.ArrayPlotData`
- :class:`~.DataFramePlotData`
- :class:`~.Plot`
- :class:`~.ToolbarPlot`

Axis
----

- :class:`~.PlotAxis`
- :class:`~.MinorPlotAxis`
- :class:`~.LabelAxis`
- :class:`~.AbstractTickGenerator`
- :class:`~.DefaultTickGenerator`
- :func:`~.auto_ticks`
- :func:`~.auto_interval`
- :func:`~.tick_intervals`
- :func:`~.log_auto_ticks`
- :func:`~.auto_bounds`
- :func:`~.calc_bound`

Grid
----

- :class:`~.PlotGrid`

Tools
-----

- :class:`~.AbstractController`

Colormaps and Color Palettes
----------------------------

Utilities / Convenience Objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- :func:`~.center`
- :attr:`~.color_map_dict`
- :attr:`~.color_map_functions`
- :attr:`~.color_map_name_dict`
- :func:`~.reverse`

Colormaps
^^^^^^^^^

- :func:`~.autumn`
- :func:`~.binary`
- :func:`~.bone`
- :func:`~.cool`
- :func:`~.copper`
- :func:`~.flag`
- :func:`~.seismic`
- :func:`~.terrain`
- :func:`~.gray`
- :func:`~.yarg`
- :func:`~.hot`
- :func:`~.hsv`
- :func:`~.jet`
- :func:`~.pink`
- :func:`~.prism`
- :func:`~.spring`
- :func:`~.summer`
- :func:`~.winter`
- :func:`~.cw1_004`
- :func:`~.cw1_005`
- :func:`~.cw1_006`
- :func:`~.cw1_028`
- :func:`~.gmt_drywet`
- :func:`~.Blues`
- :func:`~.BrBG`
- :func:`~.BuGn`
- :func:`~.BuPu`
- :func:`~.GnBu`
- :func:`~.Greens`
- :func:`~.Greys`
- :func:`~.OrRd`
- :func:`~.Oranges`
- :func:`~.PRGn`
- :func:`~.PiYG`
- :func:`~.PuBu`
- :func:`~.PuBuGn`
- :func:`~.PuOr`
- :func:`~.PuRd`
- :func:`~.Purples`
- :func:`~.RdBu`
- :func:`~.RdGy`
- :func:`~.RdPu`
- :func:`~.RdYlBu`
- :func:`~.RdYlGn`
- :func:`~.Reds`
- :func:`~.Spectral`
- :func:`~.YlGn`
- :func:`~.YlGnBu`
- :func:`~.YlOrBr`
- :func:`~.YlOrRd`
- :func:`~.gist_earth`
- :func:`~.gist_gray`
- :func:`~.gist_heat`
- :func:`~.gist_ncar`
- :func:`~.gist_rainbow`
- :func:`~.gist_stern`
- :func:`~.gist_yarg`
- :func:`~.CubicYF`
- :func:`~.CubicL`
- :func:`~.LinearL`
- :func:`~.LinearLHot`
- :func:`~.CoolWarm`
- :func:`~.CubeHelix`
- :func:`~.wistia`
- :func:`~.magma`
- :func:`~.inferno`
- :func:`~.plasma`
- :func:`~.viridis`
- :func:`~.accent`
- :func:`~.Dark2`
- :func:`~.Paired`
- :func:`~.Pastel1`
- :func:`~.Pastel2`
- :func:`~.Set1`
- :func:`~.Set2`
- :func:`~.Set3`

Color Palettes
^^^^^^^^^^^^^^

- :attr:`~.cbrewer`
- :attr:`~.palette11`
- :attr:`~.palette14`
- :attr:`~.PALETTEES`

"""

from .base import (
    NumericalSequenceTrait,
    PointTrait,
    ImageTrait,
    DimensionTrait,
    SortOrderTrait,
    bin_search,
    reverse_map_1d,
    right_shift,
    left_shift,
    sort_points,
    find_runs,
    arg_find_runs,
    point_line_distance,
)

# Data model
from .abstract_data_source import AbstractDataSource
from .array_data_source import ArrayDataSource
from .grid_data_source import GridDataSource
from .image_data import ImageData
from .multi_array_data_source import MultiArrayDataSource
from .point_data_source import PointDataSource
from .abstract_data_range import AbstractDataRange
from .base_data_range import BaseDataRange
from .data_range_1d import DataRange1D
from .data_range_2d import DataRange2D

# Mappers
from .abstract_mapper import AbstractMapper
from .base_1d_mapper import Base1DMapper
from .grid_mapper import GridMapper
from .log_mapper import LogMapper
from .linear_mapper import LinearMapper
from .color_mapper import ColorMapper, ColorMapTemplate
from .discrete_color_mapper import DiscreteColorMapper
from .transform_color_mapper import TransformColorMapper
from .horizon_plot import BandedMapper

# Visual components
from .abstract_plot_renderer import AbstractPlotRenderer
from .abstract_overlay import AbstractOverlay
from .base_plot_container import BasePlotContainer
from .base_plot_frame import BasePlotFrame
from .cross_plot_frame import CrossPlotFrame
from .data_view import DataView
from .simple_plot_frame import SimplePlotFrame
from .plot_component import PlotComponent
from .plot_graphics_context import (
    PlotGraphicsContext,
    PlotGraphicsContextMixin,
)
from .plot_containers import (
    OverlayPlotContainer,
    HPlotContainer,
    VPlotContainer,
    GridPlotContainer,
)

GridContainer = GridPlotContainer

try:
    from .plot_containers import ConstraintsPlotContainer
except ImportError:
    pass

from .label import Label
from .plot_label import PlotLabel
from .legend import Legend
from .tooltip import ToolTip
from .data_label import DataLabel
from .lasso_overlay import LassoOverlay
from .color_bar import ColorBar
from .text_box_overlay import TextBoxOverlay
from .scatter_inspector_overlay import ScatterInspectorOverlay
from .colormapped_selection_overlay import ColormappedSelectionOverlay

# Renderers
from .barplot import BarPlot
from .base_1d_plot import Base1DPlot
from .base_2d_plot import Base2DPlot
from .base_xy_plot import BaseXYPlot
from .scatterplot import ScatterPlot, render_markers
from .image_plot import ImagePlot
from .cmap_image_plot import CMapImagePlot
from .contour_line_plot import ContourLinePlot
from .contour_poly_plot import ContourPolyPlot
from .lineplot import LinePlot
from .colormapped_scatterplot import ColormappedScatterPlot
from .polygon_plot import PolygonPlot
from .errorbar_plot import ErrorBarPlot
from .filled_line_plot import FilledLinePlot
from .quiverplot import QuiverPlot
from .candle_plot import CandlePlot
from .multi_line_plot import MultiLinePlot
from .jitterplot import JitterPlot
from .variable_size_scatterplot import VariableSizeScatterPlot
from .horizon_plot import HorizonPlot
from .scatterplot_1d import ScatterPlot1D
from .line_scatterplot_1d import LineScatterPlot1D
from .text_plot_1d import TextPlot1D
from .segment_plot import SegmentPlot
from .text_plot import TextPlot

# Plot factories
from .plot_factory import (
    create_bar_plot,
    create_line_plot,
    create_scatter_plot,
    create_polar_plot,
    add_default_axes,
    add_default_grids,
)

from .abstract_plot_data import AbstractPlotData
from .array_plot_data import ArrayPlotData
from .data_frame_plot_data import DataFramePlotData
from .plot import Plot
from .toolbar_plot import ToolbarPlot

# Axis
from .axis import PlotAxis, MinorPlotAxis
from .label_axis import LabelAxis
from .ticks import (
    AbstractTickGenerator,
    DefaultTickGenerator,
    auto_ticks,
    auto_interval,
    tick_intervals,
    log_auto_ticks,
    auto_bounds,
    calc_bound,
)

# Grid
from .grid import PlotGrid

# Tools
from .abstract_controller import AbstractController

# Colormaps and color palettes
from .default_colormaps import (
    center,
    color_map_dict,
    color_map_functions,
    color_map_name_dict,
    reverse,
    autumn,
    binary,
    bone,
    cool,
    copper,
    flag,
    seismic,
    terrain,
    gray,
    yarg,
    hot,
    hsv,
    jet,
    pink,
    prism,
    spring,
    summer,
    winter,
    cw1_004,
    cw1_005,
    cw1_006,
    cw1_028,
    gmt_drywet,
    Blues,
    BrBG,
    BuGn,
    BuPu,
    GnBu,
    Greens,
    Greys,
    OrRd,
    Oranges,
    PRGn,
    PiYG,
    PuBu,
    PuBuGn,
    PuOr,
    PuRd,
    Purples,
    RdBu,
    RdGy,
    RdPu,
    RdYlBu,
    RdYlGn,
    Reds,
    Spectral,
    YlGn,
    YlGnBu,
    YlOrBr,
    YlOrRd,  
    gist_earth,
    gist_gray,
    gist_heat,
    gist_ncar,
    gist_rainbow,
    gist_stern,
    gist_yarg,
    CubicYF,
    CubicL,
    LinearL,
    LinearLHot,
    CoolWarm,
    CubeHelix,
    wistia,
    magma,
    inferno,
    plasma,
    viridis,
    accent,
    Dark2,
    Paired,
    Pastel1,
    Pastel2,
    Set1,
    Set2,
    Set3,
)
from .default_colors import cbrewer, palette11, palette14, PALETTES
