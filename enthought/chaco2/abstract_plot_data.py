""" Defines the base class for plot data.
"""
from enthought.traits.api import Bool, Event, HasTraits


class AbstractPlotData(HasTraits):
    """
    Defines the interface for data providers to Plot.
    """

    #-------------------------------------------------------------------------
    # Events that consumers of this data should use
    #-------------------------------------------------------------------------

    # Indicates that some of the data has changed.  The event object must
    # be a dict with keys "added", "removed", "changed" and values that are
    # lists of strings. This event is used by consumers of this data.
    data_changed = Event
    

    #-------------------------------------------------------------------------
    # Flags - these determine how downstream consumers of the PlotData objet
    # interact with it.  (Typically "consumers" just refers to Plots.)
    #-------------------------------------------------------------------------

    # Can consumers (Plots) write data back through this interface using 
    # set_data()?
    writable = Bool(True)

    # Can consumers (Plots) set selections?
    selectable = Bool(True)


    def list_data(self):
        """ Returns a list of valid names to use for get_data().  
        
        These names are generally strings but can also be integers or any other
        hashable type.
        """
        raise NotImplementedError


    def get_data(self, name):
        """ Returns the data or data source associated with *name*.  
        
        If there is no data or data source associated with the name, this method
        returns None.
        """
        raise NotImplementedError


    def set_data(self, name, new_data, generate_name=False):
        """ 
        Returns the new data's name.

        If **writable** is True, then this method sets the data associated
        with the given name to the new value.  
        
        If **writable** is False, then this method must do nothing.  
        
        If *generate_name* is True, then the data source must
        create a new name to bind to the data, and return it.

        If the name does not exist, then the method attaches a new data entry 
        to this PlotData.

        """
        raise NotImplementedError


    def set_selection(self, name, selection):
        """ Sets the selection on the specified data.  
        
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
