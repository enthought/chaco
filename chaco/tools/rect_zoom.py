# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the RectZoomTool class.
"""
from .zoom_tool import ZoomTool


class RectZoomTool(ZoomTool):
    """
    Allows the user to drag a zoom box around a region of the plot.

    This is a subclass of ZoomTool, with different default values for some
    traits.
    """

    #: Selects a box in two dimensions (overrides ZoomTool).
    tool_mode = "box"

    #: The tool is always on; left-clicking initiates a zoom (overrides
    #: ZoomTool).
    always_on = True
