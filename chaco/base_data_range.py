# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Defines the BaseDataRange class.
"""

# Local relative imports
from .abstract_data_range import AbstractDataRange


class BaseDataRange(AbstractDataRange):
    """Ranges represent sub-regions of data space.

    They support "autoscaling" by querying their associated data sources.
    """

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def __init__(self, *datasources, **kwtraits):
        super().__init__(**kwtraits)
        if len(datasources) > 0:
            self.sources.extend(datasources)

    def add(self, *datasources):
        """ Convenience method to add a data source. """
        for datasource in datasources:
            if datasource not in self.sources:
                self.sources.append(datasource)

    def remove(self, *datasources):
        """ Convenience method to remove a data source. """
        for datasource in datasources:
            if datasource in self.sources:
                self.sources.remove(datasource)
