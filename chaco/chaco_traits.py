# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines various traits that are used in many places in Chaco.
"""

# Enthought library imports
from traits.api import Enum

# ----------------------------------------------------------------------------
# Box positioning traits: used to specify positions of boxes relative to
# one another.  Generally used for layout.
# ----------------------------------------------------------------------------

box_edge_enum = Enum("left", "right", "top", "bottom")

#: Values correspond to: top, bottom, left, right, top left, top right, bottom
#: left, bottom right
box_position_enum = Enum("T", "B", "L", "R", "TL", "TR", "BL", "BR")
