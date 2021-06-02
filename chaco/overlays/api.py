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
Defines the publicly accessible overlays in Chaco.

- :class:`~.AlignedContainerOverlay`
- :class:`~.ColormappedSelectionOverlay`
- :class:`~.ContainerOverlay`
- :class:`~.CoordinateLineOverlay`
- :class:`~.DataBox`
- :classL`~.DataLabel`
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

"""
from .aligned_container_overlay import AlignedContainerOverlay
from .colormapped_selection_overlay import ColormappedSelectionOverlay
from .container_overlay import ContainerOverlay
from .coordinate_line_overlay import CoordinateLineOverlay
from .databox import DataBox
from .data_label import DataLabel
from .lasso_overlay import LassoOverlay
from .legend import (
    AbstractCompositeIconRenderer, CompositeIconRenderer, Legend
)
from .plot_label import PlotLabel
from .scatter_inspector_overlay import ScatterInspectorOverlay
from .simple_inspector_overlay import (
    basic_formatter,
    datetime_formatter,
    date_formatter,
    SimpleInspectorOverlay,
    time_formatter,
)
from .text_box_overlay import TextBoxOverlay
from .text_grid_overlay import TextGridOverlay
from .tooltip import ToolTip
from ..tools.image_inspector_tool import ImageInspectorOverlay

from chaco.overlays.layers.api import (
    ErrorLayer,
    StatusLayer,
    WarningLayer,
)
