# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# Enthought library imports
from traits.api import Instance, HasTraits
from traitsui.api import View, Item
from enable.api import Container
from enable.api import ComponentEditor


class PlotWindow(HasTraits):
    plot = Instance(Container)

    traits_view = View(
        Item(
            "plot",
            editor=ComponentEditor(),
            height=300,
            width=500,
            show_label=False,
        ),
        title="Chaco Plot",
        resizable=True,
    )
