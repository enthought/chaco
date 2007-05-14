
from enthought.traits.api import Event, HasTraits, true


class AbstractPlotData(HasTraits):
    """
    Defines the interface for data providers to Plot.
    """

    #-------------------------------------------------------------------------
    # Events that consumers of this data should use
    #-------------------------------------------------------------------------

    # Indicates that some of the data has changed.  The event objects should
    # be a dict with keys "added", "removed", "changed" and values of lists of
    # strings.
    data_changed = Event
    

    #-------------------------------------------------------------------------
    # Flags - these determine how downstream consumers of the PlotData objet
    # interact with it.  (Typically "consumers" just refers to Plots.)
    #-------------------------------------------------------------------------

    # Can consumers write data back through this interface using set_data()?
    writable = true

    # Can consumers set selections?
    selectable = true


    def list_data(self):
        """ Returns a list of valid names to use for get_data().  These are
        generally strings but can also be integers or any other hashable type.
        """
        raise NotImplementedError


    def get_data(self, name):
        """ Returns the data or datasource associated with name.  If there is
        no data or datasource associated with the name, returns None.
        """
        raise NotImplementedError


    def set_data(self, name, new_data, generate_name=False):
        """ If writable is True, then this sets the data associated with the
        given name to the new value.  If writable if False, then this should
        do nothing.  If generate_name is True, then the datasource should
        create a new name to bind to the data, and return it.

        If the name does not exist, then attaches a new data entry to this
        PlotData.

        Returns the new data's name.
        """
        raise NotImplementedError


    def set_selection(self, name, selection):
        """ Sets the selection on the specified data.  This informs the class
        that Chaco has selected a portion of the data.  'Selection' is a binary
        array of the same length as the data named 'name'.
        """
        raise NotImplementedError
