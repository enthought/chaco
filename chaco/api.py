""" Defines the publicly accessible items of the Chaco API.
"""
# This just imports the key datamodel classes into the top-level package
# namespace for convenience.

from .base import NumericalSequenceTrait, PointTrait, ImageTrait, DimensionTrait, \
                 SortOrderTrait, bin_search, reverse_map_1d, right_shift, \
                 left_shift, sort_points, find_runs, arg_find_runs, \
                 point_line_distance

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

# Colormaps and color palettes
from .default_colormaps import *
from .default_colors import *

# Visual components
from .abstract_plot_renderer import AbstractPlotRenderer
from .abstract_overlay import AbstractOverlay
from .base_plot_container import BasePlotContainer
from .base_plot_frame import BasePlotFrame
from .cross_plot_frame import CrossPlotFrame
from .data_view import DataView
from .simple_plot_frame import SimplePlotFrame
from .plot_component import PlotComponent
from .plot_graphics_context import PlotGraphicsContext, PlotGraphicsContextMixin
from .plot_containers import OverlayPlotContainer, HPlotContainer, VPlotContainer, \
                            GridPlotContainer
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
from .colormapped_selection_overlay import ColormappedSelectionOverlay
from .polygon_plot import PolygonPlot
from .errorbar_plot import ErrorBarPlot
from .filled_line_plot import FilledLinePlot
from .quiverplot import QuiverPlot
from .candle_plot import CandlePlot
from .multi_line_plot import MultiLinePlot
from .jitterplot import JitterPlot
from .variable_size_scatterplot import VariableSizeScatterPlot
from .horizon_plot import BandedMapper, HorizonPlot
from .scatterplot_1d import ScatterPlot1D
from .line_scatterplot_1d import LineScatterPlot1D
from .text_plot_1d import TextPlot1D
from .segment_plot import SegmentPlot
from .text_plot import TextPlot

# Plot factories
from .plot_factory import create_bar_plot, create_line_plot, create_scatter_plot, \
                         create_polar_plot, add_default_axes, add_default_grids

from .abstract_plot_data import AbstractPlotData
from .array_plot_data import ArrayPlotData
from .data_frame_plot_data import DataFramePlotData
from .plot import Plot
from .toolbar_plot import ToolbarPlot

# Axis
from .axis import PlotAxis, MinorPlotAxis
from .label_axis import LabelAxis
from .ticks import AbstractTickGenerator, DefaultTickGenerator, auto_ticks, auto_interval, \
                  tick_intervals, log_auto_ticks, auto_bounds, calc_bound

# Grid
from .grid import PlotGrid

# Tools
from .abstract_controller import AbstractController

# Importing various symbols into the Chaco namespace for backwards
# compatibility.  New code should directly import from Enable.
from enable.base_tool import BaseTool, KeySpec
from enable.markers import marker_trait

#EOF
