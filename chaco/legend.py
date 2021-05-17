# (C) Copyright 2006-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Defines the Legend, AbstractCompositeIconRenderer, and
CompositeIconRenderer classes.
"""
import warnings

from chaco.overlays.legend import (  # noqa: F401
    AbstractCompositeIconRenderer, CompositeIconRenderer, Legend
)

warnings.warn(
    "This module has been moved to sit in chaco/overlays and this stub module"
    " has been kept for backwards compatibility. Importing from this module is"
    " deprecated, please import needed objects from chaco.api instead",
    DeprecationWarning,
    stacklevel=2,
)
