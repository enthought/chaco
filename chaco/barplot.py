# (C) Copyright 2006-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Defines the BarPlot class. this module has been moved to live in
chaco/plots and as a result, importing BarPlot from this module is deprecated.
"""
import warnings

from chaco.plots.barplot import BarPlot  # noqa: F401

warnings.warn(
    "This module has been moved to sit in chaco/plots and this stub module has"
    " been kept for backwards compatibility. Importing from this module is"
    " deprecated, please import needed objects from chaco.api instead",
    DeprecationWarning
)
