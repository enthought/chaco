""" Defines ArrayPlotData.
"""

# Enthought library imports
from enthought.traits.api import Dict


# Local, relative imports
from abstract_plot_data import AbstractPlotData


class ArrayPlotData(AbstractPlotData):
    """ A PlotData implementation class that handles a list of Numpy arrays
    (or a 2-D Numpy array).

    By default, it doesn't allow its input data to be modified by downstream
    Chaco components or interactors.
    """

    #-------------------------------------------------------------------------
    # Public traits
    #-------------------------------------------------------------------------

    # Map of names to arrays.  Although there is no restriction on the array
    # dimensions, each array must correspond to a single plot item; that
    # is, a single name must not map to a multi-dimensional array unless
    # the array is being used for an image plot or for something that can handle
    # multi-dimensional input data.
    arrays = Dict

    # Consumers can write data to this object (overrides AbstractPlotData).
    writable = True

    def __init__(self, *data, **kw):
        """ ArrayPlotData can be constructed by passing in arrays.  
        
        Keyword arguments can be used to give certain arrays specific names;
        unnamed arrays are given a generic name of the format 'seriesN', where
        N is its position in the argument list.

        For example::
        
            ArrayPlotData(array1, array2, index=array3, foo=array4)

        This call results in the creation of four entries in self.arrays::
            
            'series1' -> array1
            'series2' -> array2
            'index'   -> array3
            'foo'     -> array4

        If any names in the keyword parameter list collide with the 
        auto-generated positional names "series1", "series2", etc., then those
        arrays are replaced.

        Note that this factor means that keyword traits are *not* set using the
        keyword parameters in the constructor. This strategy defies some 
        conventions, but was it chosen for convenience, since the raison d'etre
        of this class is convenience.
        """
        super(AbstractPlotData, self).__init__()
        self.arrays.update(kw)
        for i in range(1, len(data)+1):
            self.arrays['series'+str(i)] = data[i-1]
        return

    #------------------------------------------------------------------------
    # Dictionary Interface
    #------------------------------------------------------------------------

    def __getitem__(self, name):
        return self.arrays.get(name, None)

    def __setitem__(self, name, value):
        return self.set_data(name, value)

    def __delitem__(self, name):
        return self.del_data(name)
    

    def list_data(self):
        """ Returns a list of the names of the arrays managed by this instance.
        """
        return self.arrays.keys()


    def get_data(self, name):
        """ Returns the array associated with *name*.
        
        Implements AbstractDataSource.
        """
        return self.arrays.get(name, None)

    def del_data(self, name):
        """ Deletes the array specified by *name*, or raises a KeyError if
        the named array does not exist.
        """
        if name in self.arrays:
            del self.arrays[name]
        else:
            raise KeyError("Data series '%s' does not exist." % name)


    def set_data(self, name, new_data, generate_name=False):
        """ Sets the specified array as the value for either the specified
        name or a generated name.
        
        Implements AbstractPlotData.
        
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
        if not self.writable:
            return None

        if generate_name:
            # Find all 'series*' and increment
            candidates = [n[6:] for n in self.arrays.keys() if n.startswith('series')]
            max_int = 0
            for c in candidates:
                try:
                    if int(c) > max_int:
                        max_int = int(c)
                except ValueError:
                    pass
            name = "series%d" % (max_int + 1)

        event = {}
        if name in self.arrays:
            event['changed'] = [name]
        else:
            event['added'] = [name]
        
        self.arrays[name] = new_data
        self.data_changed = event
        return name
    

    def set_selection(self, name, selection):
        """ Overrides AbstractPlotData to do nothing and not raise an error.
        """
        pass


