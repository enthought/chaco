# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the base class for mappings.
"""
# Major library imports
from numpy import array

# Enthought library imports
from traits.api import Event, HasTraits, Tuple


class AbstractMapper(HasTraits):
    """Defines an abstract mapping from a region in input space to a
    region in output space.
    """

    #: A generic "update" event that generally means that anything that relies
    #: on this mapper for visual output should do a redraw or repaint.
    updated = Event

    # FIXME: domain_limits is never used

    #: A tuple representing the minimum and maximum values of the domain (data
    #: space).  The dimensionality of each value varies depending on the
    #: dimensions of the mapper, so for 1D mappers these will be scalars, for
    #: image and 2D mappers these will be tuples.
    domain_limits = Tuple(None, None)

    def map_screen(self, data_array):
        """map_screen(data_array) -> screen_array

        Maps values from data space into screen space.
        """

    def map_data(self, screen_val):
        """map_data(screen_val) -> data_val

        Maps values from screen space into data space.
        """

    def map_data_array(self, screen_vals):
        """map_data_array(screen_vals) -> data_vals

        Maps an array of values from screen space into data space.
        By default, this method just loops over the points, calling map_data()
        on each one.  For vectorizable mapping functions, override this
        implmentation with a faster one.
        """
        return array([self.map_data(v) for v in screen_vals])

    # ------------------------------------------------------------------------
    # Persistence-related methods
    # ------------------------------------------------------------------------

    def _post_load(self):
        self._cache_valid = False
        self._range_changed(None, self.range)
