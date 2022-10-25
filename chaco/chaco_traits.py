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
from traits.api import Enum, Union, TraitError

# ----------------------------------------------------------------------------
# Box positioning traits: used to specify positions of boxes relative to
# one another.  Generally used for layout.
# ----------------------------------------------------------------------------

box_edge_enum = Enum("left", "right", "top", "bottom")

#: Values correspond to: top, bottom, left, right, top left, top right, bottom
#: left, bottom right
box_position_enum = Enum("T", "B", "L", "R", "TL", "TR", "BL", "BR")


class MappedUnion(Union):
    """Version of the Union trait that handles mapped traits correctly."""

    #: This is not mapped by default.
    is_mapped = False

    def __init__(self, *traits, **metadata):
        super().__init__(*traits, **metadata)

        # look for post_setattr and is_mapped on traits
        post_setattrs = []
        mapped_traits = []
        for trait in traits:
            if trait is None:
                continue
            post_setattr = getattr(trait, "post_setattr", None)
            if post_setattr is not None:
                post_setattrs.append(post_setattr)
            if trait.is_mapped:
                self.is_mapped = True
                mapped_traits.append(trait)

        if post_setattrs:
            self.post_setattrs = post_setattrs
            self.post_setattr = self._post_setattr
        if self.is_mapped:
            self.mapped_traits = mapped_traits

    def mapped_value(self, value):
        for trait in self.mapped_traits:
            try:
                return trait.mapped_value(value)
            except Exception:
                pass

        return value

    def _post_setattr(self, object, name, value):
        for post_setattr in self.post_setattrs:
            try:
                post_setattr(object, name, value)
                return
            except Exception:
                pass

        if self.is_mapped:
            setattr(object, name + "_", value)


class Optional(MappedUnion):
    """Convenience class"""

    def __init__(self, trait, **metadata):
        super().__init__(None, trait, **metadata)
