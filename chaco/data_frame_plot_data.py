""" Defines DataFramePlotData.
"""

# Enthought library imports
from traits.api import Bool, Instance, Property

# Local, relative imports
from .abstract_plot_data import AbstractPlotData


class DataFramePlotData(AbstractPlotData):
    """ A PlotData implementation class that handles a DataFrame.

    By default, it doesn't allow its input data to be modified by downstream
    Chaco components or interactors. The index is availble as data unless there
    is a column named 'index', in which case that column masks the DataFrame
    index. (Rename that column if the DataFrame index must be accessible.)

    """

    #-------------------------------------------------------------------------
    # Public traits
    #-------------------------------------------------------------------------

    # The DataFrame backing this object.
    data_frame = Instance('pandas.core.frame.DataFrame')

    # Consumers can write data to this object (overrides AbstractPlotData).
    writable = True

    #-------------------------------------------------------------------------
    # Private traits
    #-------------------------------------------------------------------------

    _has_index_column = Property(Bool)

    def _get__has_index_column(self):
        return 'index' in self.data_frame.columns

    #------------------------------------------------------------------------
    # AbstractPlotData Interface
    #------------------------------------------------------------------------

    def list_data(self):
        """ Returns a list of the names of the columns of the DataFrame. The
        name 'index' is added to this unless there is a column named 'index'.
        """
        names = self.data_frame.columns.tolist()
        if not self._has_index_column:
            names = ['index'] + names
        return names

    def get_data(self, name):
        """ Returns the array associated with *name*.

        Implements AbstractDataSource.
        """
        if name == 'index' and not self._has_index_column:
            return self.data_frame.index.values
        series = self.data_frame.get(name)
        return series if series is None else series.values

    def del_data(self, name):
        """ Deletes the column specified by *name*, or raises a KeyError if
        the named column does not exist.
        """
        if not self.writable:
            return None

        if name == 'index' and not self._has_index_column:
            raise KeyError("Cannot delete the index.")

        if name in self.data_frame.columns:
            del self.data_frame[name]
            self.data_changed = {'removed': [name]}
        else:
            raise KeyError("Column '{}' does not exist.".format(name))

    def set_data(self, name, new_data, generate_name=False):
        """ Sets the specified index or column as the value for either the
        specified
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
        """ Sets the specified column or index as the value for either the
        specified name or a generated name.

        Implements AbstractPlotData's update_data() method.  This method has
        the same signature as the dictionary update() method.

        """
        if not self.writable:
            return None

        data = dict(*args, **kwargs)
        event = {}
        for name in data:
            if name in self.data_frame.columns:
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
        names = [
            "series{0:d}".format(i)
            for i in range(max_index + 1, max_index + n + 1)
        ]
        return names

    def _generate_indices(self):
        """ Generator that yields all integers that match "series%d" in keys
        """
        yield 0  # default minimum
        for name in self.list_data():
            if name.startswith('series'):
                try:
                    v = int(name[6:])
                except ValueError:
                    continue
                yield v

    def _update_data(self, data):
        for name, value in data.items():
            if name == 'index' and self._has_index_column:
                self.data_frame.index = value
            else:
                self.data_frame[name] = value
