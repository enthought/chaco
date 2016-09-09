""" Defines ArrayPlotData.
"""
import six
import six.moves as sm
from numpy import array, ndarray

# Enthought library imports
from traits.api import Dict

# Local, relative imports
from .abstract_plot_data import AbstractPlotData
from .abstract_data_source import AbstractDataSource


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
        self._update_data(kw)
        data = dict(sm.zip(self._generate_names(len(data)), data))
        self._update_data(data)


    #------------------------------------------------------------------------
    # AbstractPlotData Interface
    #------------------------------------------------------------------------

    def list_data(self):
        """ Returns a list of the names of the arrays managed by this instance.
        """
        return list(six.iterkeys(self.arrays))


    def get_data(self, name):
        """ Returns the array associated with *name*.

        Implements AbstractDataSource.
        """
        return self.arrays.get(name, None)


    def del_data(self, name):
        """ Deletes the array specified by *name*, or raises a KeyError if
        the named array does not exist.
        """
        if not self.writable:
            return None

        if name in self.arrays:
            del self.arrays[name]
            self.data_changed = {'removed': [name]}
        else:
            raise KeyError("Data series '%s' does not exist." % name)


    def set_data(self, name, new_data, generate_name=False):
        """ Sets the specified array as the value for either the specified
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
        if not self.writable:
            return None

        if generate_name:
            names = self._generate_names(1)
            name = names[0]
            
        self.update_data({name: new_data})
        return name


    def update_data(self, *args, **kwargs):
        """ Sets the specified array as the value for either the specified
        name or a generated name.

        Implements AbstractPlotData's update_data() method.  This method has
        the same signature as the dictionary update() method.

        """
        if not self.writable:
            return None
        
        data = dict(*args, **kwargs)
        event = {}
        for name in data:
            if name in self.arrays:
                event.setdefault('changed', []).append(name)
            else:
                event.setdefault('added', []).append(name)

        self._update_data(data)
        self.data_changed = event


    def set_selection(self, name, selection):
        """ Overrides AbstractPlotData to do nothing and not raise an error.
        """
        pass

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------    

    def _generate_names(self, n):
        """ Generate n new names
        """
        max_index = max(self._generate_indices())
        names = ["series{0:d}".format(n) for n in range(max_index+1, max_index+n+1)]
        return names

    def _generate_indices(self):
        """ Generator that yields all integers that match "series%d" in keys
        """
        yield 0 # default minimum
        for name in self.list_data():
            if name.startswith('series'):
                try:
                    v = int(name[6:])
                except ValueError:
                    continue
                yield v

    def _update_data(self, data):
        """ Update the array, ensuring that data is an array
        """
        # note that this call modifies data, but that's OK since the callers
        # all create the dictionary that they pass in
        for name, value in list(six.iteritems(data)):
            if not isinstance(value, (ndarray, AbstractDataSource)):
                data[name] = array(value)
            else:
                data[name] = value

        self.arrays.update(data)

