# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the BasePlotContainer class.
"""
import warnings

# Enthought library imports
from enable.api import Container
from traits.api import Bool, Instance, Property, Str, Tuple

# Local, relative imports
from .plot_component import DEFAULT_DRAWING_ORDER, PlotComponent


class BasePlotContainer(Container):
    """
    A container for PlotComponents.  Serves as the base class for other
    PlotContainers.

    PlotContainers define a layout, i.e., a spatial relationship between
    their contained components.  (BasePlotContainer doesn't define one,
    but its various subclasses do.)

    BasePlotContainer is a subclass of Enable Container, so it is possible to
    insert Enable-level components into it.  However, because Enable
    components don't have the correct interfaces to participate in layout,
    the visual results will probably be incorrect.
    """

    #: Redefine the container layers to name the main layer as "plot" instead
    #: of the Enable default of "mainlayer"
    container_under_layers = Tuple("background", "image", "underlay", "plot")

    #:------------------------------------------------------------------------
    #: Duplicate trait declarations from PlotComponent.  We don't subclass
    #: PlotComponent to avoid MRO complications with trait handlers and property
    #: getters/setters.
    #:------------------------------------------------------------------------

    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))
    draw_layer = Str("plot")
