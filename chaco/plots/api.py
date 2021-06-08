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
Defines the publicly accessible PlotRenderers in Chaco.

- :class:`~.BarPlot`
- :class:`~.BandedMapper`
- :class:`~.CandlePlot`
- :class:`~.CMapImagePlot`
- :class:`~.ColorBar`
- :class:`~.ColormappedScatterPlot`
- :class:`~.ColormappedScatterPlotView`
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
- :class:`~.ScatterPlotView`
- :class:`~.ScatterPlot1D`
- :class:`~.SegmentPlot`
- :class:`~.TextPlot`
- :class:`~.TextPlot1D`

"""

from chaco.plots.barplot import BarPlot
from chaco.plots.candle_plot import CandlePlot
from chaco.plots.cmap_image_plot import CMapImagePlot
from chaco.plots.color_bar import ColorBar
from chaco.plots.colormapped_scatterplot import (
    ColormappedScatterPlot, ColormappedScatterPlotView
)
from chaco.plots.contour.contour_line_plot import ContourLinePlot
from chaco.plots.contour.contour_poly_plot import ContourPolyPlot
from chaco.plots.errorbar_plot import ErrorBarPlot
from chaco.plots.filled_line_plot import FilledLinePlot
from chaco.plots.horizon_plot import BandedMapper, HorizonPlot
from chaco.plots.image_plot import ImagePlot
from chaco.plots.jitterplot import JitterPlot
from chaco.plots.line_scatterplot_1d import LineScatterPlot1D
from chaco.plots.lineplot import LinePlot
from chaco.plots.multi_line_plot import MultiLinePlot
from chaco.plots.polar_line_renderer import PolarLineRenderer
from chaco.plots.polygon_plot import PolygonPlot
from chaco.plots.quiverplot import QuiverPlot
from chaco.plots.scatterplot import (
    render_markers, ScatterPlot, ScatterPlotView
)
from chaco.plots.scatterplot_1d import ScatterPlot1D
from chaco.plots.segment_plot import ColormappedSegmentPlot, SegmentPlot
from chaco.plots.text_plot import TextPlot
from chaco.plots.text_plot_1d import TextPlot1D
