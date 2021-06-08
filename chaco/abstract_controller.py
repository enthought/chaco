# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the base class for controllers.
"""
# Enthought library imports
from enable.api import Component, Interactor
from traits.api import Instance


class AbstractController(Interactor):
    """
    Abstract class for tools that manipulate PlotComponents. By default, a
    controller attaches to a single PlotComponent.
    """

    component = Instance(Component)

    def __init__(self, component, *args, **kw):
        self.component = component
        super().__init__(*args, **kw)

    def deactivate(self, component):
        """This method is called by the component when this controller is no
        longer the active tool.
        """
        pass
