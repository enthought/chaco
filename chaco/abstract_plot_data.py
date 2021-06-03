# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the base class for plot data.
"""
from traits.api import Bool, Event, HasTraits


class AbstractPlotData(HasTraits):
    """
    Defines the interface for data providers to Plot.
    """

    # -------------------------------------------------------------------------
    # Events that consumers of this data should use
    # -------------------------------------------------------------------------

    #: Indicates that some of the data has changed.  The event object must
    #: be a dict with keys "added", "removed", "changed" and values that are
    #: lists of strings. This event is used by consumers of this data.
    data_changed = Event

    # -------------------------------------------------------------------------
    # Flags - these determine how downstream consumers of the PlotData objet
    # interact with it.  (Typically "consumers" just refers to Plots.)
    # -------------------------------------------------------------------------

    #: Can consumers (Plots) write data back through this interface using
    #: set_data()?
    writable = Bool(True)

    #: Can consumers (Plots) set selections?
    selectable = Bool(True)

    def list_data(self):
        """Returns a list of valid names to use for get_data().

        These names are generally strings but can also be integers or any other
        hashable type.
        """
        raise NotImplementedError

    def get_data(self, name):
        """Returns the data or data source associated with *name*.

        If there is no data or data source associated with the name, this method
        returns None.
        """
        raise NotImplementedError

    def del_data(self, name):
        """Deletes the array specified by *name*, or raises a KeyError if
        the named array does not exist.

        If the instance is not writable, then this must do nothing.

        """
        raise NotImplementedError

    def set_data(self, name, new_data, generate_name=False):
        """Sets the specified array as the value for either the specified
        name or a generated name.

        If the instance's `writable` attribute is True, then this method sets
        the data associated with the given name to the new value, otherwise it
        does nothing.

        Parameters
        ----------
        name : string
            The name of the array whose value is to be set.
        new_data : array
            The array to set as the value of *name*.
        generate_name : Boolean
            If True, a unique name of the form 'seriesN' is created for the
            array, and is used in place of *name*. The 'N' in 'seriesN' is
            one greater the largest N already used.

        Returns
        -------
        The name under which the array was set.

        """
        raise NotImplementedError

    def update_data(self, *args, **kwargs):
        """
        Update a set of data values, firing only one data_changed event.

        This function has the same signature as the dictionary update()
        method.

        """
        raise NotImplementedError

    def set_selection(self, name, selection):
        """Sets the selection on the specified data.

        This method informs the class that Chaco has selected a portion of the
        data.

        Parameters
        ----------
        name : string
            Name of an array
        selection : array of Booleans
            Indicates whether the data in the cooresponding position of the
            array named by *name* is selected.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------------
    # Dictionary Interface
    # ------------------------------------------------------------------------

    def __getitem__(self, name):
        return self.arrays.get(name, None)

    def __setitem__(self, name, value):
        return self.set_data(name, value)

    def __delitem__(self, name):
        return self.del_data(name)

    def update(self, *args, **kwargs):
        self.update_data(*args, **kwargs)
