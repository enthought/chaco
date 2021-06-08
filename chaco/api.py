# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
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
- :class:`~.PolarMapper`

Visual Components / Overlays
----------------------------

- :class:`~.AbstractPlotRenderer`
- :class:`~.AbstractOverlay`
- :class:`~.BasePlotContainer`
- :class:`~.DataView`
- :class:`~.PlotComponent`
- :class:`~.PlotGraphicsContext`
- :class:`~.PlotGraphicsContextMixin`
- :class:`~.OverlayPlotContainer`
- :class:`~.HPlotContainer`
- :class:`~.VPlotContainer`
- :class:`~.GridPlotContainer`
- :class:`~.Label`
- :class:`~.ColorBar`
- :class:`~.AlignedContainerOverlay`
- :class:`~.ColormappedSelectionOverlay`
- :class:`~.ContainerOverlay`
- :class:`~.CoordinateLineOverlay`
- :class:`~.DataBox`
- :class:`~.DataLabel`
- :class:`~.LassoOverlay`
- :class:`~.AbstractCompositeIconRenderer`
- :class:`~.CompositeIconRenderer`
- :class:`~.PlotLabel`
- :class:`~.ScatterInspectorOverlay`
- :func:`~.basic_formatter`
- :func:`~.datetime_formatter`
- :func:`~.date_formatter`
- :class:`~.SimpleInspectorOverlay`
- :func:`~.time_formatter`
- :class:`~.TextBoxOverlay`
- :class:`~.TextGridOverlay`
- :class:`~.ToolTip`
- :class:`~.ImageInspectorOverlay`
- :class:`~.ErrorLayer`
- :class:`~.StatusLayer`
- :class:`~.WarningLayer`
- :class:`~.ColormappedScatterPlotView`
- :class:`~.ScatterPlotView`

Renderers
---------

- :class:`~.Base1DPlot`
- :class:`~.Base2DPlot`
- :class:`~.BaseXYPlot`
- :class:`~.BarPlot`
- :class:`~.CandlePlot`
- :class:`~.CMapImagePlot`
- :class:`~.ColormappedScatterPlot`
- :class:`~.ColormappedSegmentPlot`
- :class:`~.ContourLinePlot`
- :class:`~.ContourPolyPlot`
- :class:`~.ErrorBarPlot`
- :class:`~.FilledLinePlot`
- :class:`~.HorizonPlot`
- :class:`~.ImagePlot`
- :class:`~.JitterPlot`
- :class:`~.LineScatterPlot1D`
- :class:`~.LinePlot`
- :class:`~.MultiLinePlot`
- :class:`~.PolarLineRenderer`
- :class:`~.PolygonPlot`
- :class:`~.QuiverPlot`
- :func:`~.render_markers`
- :class:`~.ScatterPlot`
- :class:`~.ScatterPlot1D`
- :class:`~.SegmentPlot`
- :class:`~.TextPlot`
- :class:`~.TextPlot1D`
- :class:`~.ScalyPlot`

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
from .plots.horizon_plot import BandedMapper
from .polar_mapper import PolarMapper

# Visual components / Overlays
from .abstract_plot_renderer import AbstractPlotRenderer
from .abstract_overlay import AbstractOverlay
from .base_plot_container import BasePlotContainer
from .data_view import DataView
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

from chaco.overlays.api import (
    AlignedContainerOverlay,
    ColormappedSelectionOverlay,
    ContainerOverlay,
    CoordinateLineOverlay,
    DataBox,
    DataLabel,
    LassoOverlay,
    AbstractCompositeIconRenderer,
    CompositeIconRenderer,
    Legend,
    PlotLabel,
    ScatterInspectorOverlay,
    basic_formatter,
    datetime_formatter,
    date_formatter,
    SimpleInspectorOverlay,
    time_formatter,
    TextBoxOverlay,
    TextGridOverlay,
    ToolTip,
    ImageInspectorOverlay,
    ErrorLayer,
    StatusLayer,
    WarningLayer,
)

from .plots.color_bar import ColorBar

# Renderers
from .base_1d_plot import Base1DPlot
from .base_2d_plot import Base2DPlot
from .base_xy_plot import BaseXYPlot

from chaco.plots.api import (
    BarPlot,
    CandlePlot,
    CMapImagePlot,
    ColormappedScatterPlot,
    ColormappedScatterPlotView,
    ColormappedSegmentPlot,
    ContourLinePlot,
    ContourPolyPlot,
    ErrorBarPlot,
    FilledLinePlot,
    HorizonPlot,
    ImagePlot,
    JitterPlot,
    LineScatterPlot1D,
    LinePlot,
    MultiLinePlot,
    PolarLineRenderer,
    PolygonPlot,
    QuiverPlot,
    render_markers,
    ScatterPlot,
    ScatterPlotView,
    ScatterPlot1D,
    SegmentPlot,
    TextPlot,
    TextPlot1D,
)

from .scaly_plot import ScalyPlot


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
