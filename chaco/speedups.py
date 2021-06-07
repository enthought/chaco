# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# This contains python implementations of all the speedups
from ._speedups_fallback import (  # noqa: F401
    apply_selection_fade,
    array_combine,
    map_colors,
    map_colors_uint8,
    scatterplot_gather_points,
)


# cython implementation of speedups. Import these if we can.
try:
    from ._cython_speedups import (  # noqa: F401
        apply_selection_fade, map_colors, map_colors_uint8,
    )
except ImportError:
    pass
