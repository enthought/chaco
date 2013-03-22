""" Defines the ColormappedScatterPlot and ColormappedScatterPlotView classes.
"""

from __future__ import with_statement

# Standard library imports
import itertools

# Major library imports
from numpy import argsort, array, concatenate, nonzero, invert, take, \
                  isnan, transpose, newaxis, zeros, ndarray

# Enthought library imports
from kiva.constants import STROKE
from traits.api import Dict, Enum, Float, Instance
from traitsui.api import Item, RangeEditor

# Local, relative imports
from array_data_source import ArrayDataSource
from base import left_shift, right_shift
from color_mapper import ColorMapper
from scatterplot import ScatterPlot, ScatterPlotView


class ColormappedScatterPlotView(ScatterPlotView):
    """ Traits UI View for customizing a color-mapped scatter plot.
    """
    def __init__(self):
        super(ColormappedScatterPlotView, self).__init__()
        vgroup = self.content
        vgroup.content[0].content.append(Item("fill_alpha", label="Fill alpha",
                                   editor=RangeEditor(low=0.0, high=1.0)))
        return


class ColormappedScatterPlot(ScatterPlot):
    """
    Functionality moved to parent ScatterPlot class.

    This definition remains for backwards compatibility.
    """
    pass
