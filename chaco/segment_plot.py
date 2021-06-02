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

from chaco.plots.segment_plot import (  # noqa: F401
    ColormappedSegmentPlot, SegmentPlot
)

warnings.warn(
    "Importing ColormappedSegmentPlot or SegmentPlot from this module is "
    "deprecated. Please use chaco.api or chaco.plots.api instead. This module "
    "will be removed in the next major release.",
    DeprecationWarning,
    stacklevel=2,
)
