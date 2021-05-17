# (C) Copyright 2006-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Defines the ColormappedScatterPlot and ColormappedScatterPlotView classes.
"""
import warnings

from chaco.plots.colormapped_scatterplot import (  # noqa: F401
    ColormappedScatterPlot, ColormappedScatterPlotView
)

warnings.warn(
    "This module has been moved to sit in chaco/plots and this stub module has"
    " been kept for backwards compatibility. Importing from this module is"
    " deprecated, please import needed objects from chaco.api instead",
    DeprecationWarning
)
