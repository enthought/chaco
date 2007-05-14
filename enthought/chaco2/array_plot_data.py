

# Enthought library imports
from enthought.traits.api import Dict


# Local, relative imports
from abstract_plot_data import AbstractPlotData


class ArrayPlotData(AbstractPlotData):
    """ Implementation of a PlotData class that handles a list of numpy arrays
    (or a 2D numpy array).

    By default, it doesn't allow its input data to be modified by downstream
    Chaco components/interactors.
    """

    #-------------------------------------------------------------------------
    # Public traits
    #-------------------------------------------------------------------------

    # Maps names to arrays.  Although there is no restriction on the array
    # dimensions, each array should correspond to a single plot item; that
    # is, a single name shouldn't map to a multi-dimensional array unless
    # the array is being used for an image plot or something that can handle
    # multi-dimensional input data.
    arrays = Dict

    # Override the inherited value.
    writable = True

    def __init__(self, *data, **kw):
        """ ArrayPlotData can be constructed by passing in arrays.  Keyword
        arguments can be used to give certain arrays specific names; unnamed
        arrays will be given a generic name of the format 'seriesN', where
        N is its position in the argument list.

        For example, the following call:
        
            ArrayPlotData(array1, array2, index=array3, foo=array4)

        results in the creation of four entries in self.arrays:
            'series1' -> array1
            'series2' -> array2
            'index'   -> array3
            'foo'     -> array4

        If any names in the keyword parameter list collide with the auto-
        generated positional names "series1", "series2", etc., then they will
        be replaced.

        Note that this means that keyword traits will NOT be set using the
        keyword parameters in the constructor.  This defies some convention
        but was chosen for convenience, since the raison d'etre of this class
        is convenience.
        """
        super(AbstractPlotData, self).__init__()
        self.arrays.update(kw)
        for i in range(1, len(data)+1):
            self.arrays['series'+str(i)] = data[i-1]
        return


    def list_data(self):
        return self.arrays.keys()


    def get_data(self, name):
        return self.arrays.get(name, None)

    def del_data(self, name):
        if name in self.arrays:
            del self.arrays[name]
        else:
            raise KeyError("Data series '%s' does not exist." % name)


    def set_data(self, name, new_data, generate_name=False):
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
        pass


