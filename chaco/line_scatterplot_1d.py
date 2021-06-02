# (C) Copyright 2006-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import warnings

from chaco.plots.line_scatterplot_1d import LineScatterPlot1D  # noqa: F401

warnings.warn(
    "Importing LineScatterPlot1D from this module is deprecated. Please use "
    "chaco.api or chaco.plots.api instead. This module will be removed in the "
    "next major release.",
    DeprecationWarning,
    stacklevel=2,
)
