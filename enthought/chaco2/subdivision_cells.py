
from numpy import take, array, concatenate, nonzero

from enthought.traits.api import HasStrictTraits, Instance, Delegate, Array, List, \
                             Tuple, Property, Trait, Any, Disallow

from datamapper import AbstractDataMapper, right_shift, left_shift, sort_points


def find_runs(int_array, order='ascending'):
    """
    find_runs(int_array, order=<'ascending'|'flat'|'descending'>) -> list_of_int_arrays
    
    Given an integer array sorted in ascending/descending order or flat order,
    returns a list of continuous runs of integers inside the list.  for example,
        
        find_runs([1,2,3,6,7,8,9,10,11,15])
          
    returns [ [1,2,3], [6,7,8,9,10,11], [15] ]
    and 
        find_runs([0,0,0,1,1,1,1,0,0,0,0])
    return [ [0,0,0], [1,1,1,1], [0,0,0,0] ]
    """
    ranges = arg_find_runs(int_array, order)
    if ranges:
        return [int_array[i:j] for (i,j) in ranges]
    else:
        return []

def arg_find_runs(int_array, order='ascending'):
    """
    Like find_runs(), but returns a list of tuples indicating the start and
    end indices of runs in the input int_array.
    """
    if len(int_array) == 0:
        return []
    assert len(int_array.shape)==1, "find_runs() requires a 1D integer array."
    if order == 'ascending':
        increment = 1
    elif order == 'descending':
        increment = -1
    else:
        increment = 0
    rshifted = right_shift(int_array, int_array[0]-increment)
    start_indices = concatenate([[0], nonzero(int_array - (rshifted+increment))[0]])
    end_indices = left_shift(start_indices, len(int_array))
    return zip(start_indices, end_indices)


class AbstractCell(HasStrictTraits):
    """
    A grid cell in a uniform subdivision.  Individual subclasses store points
    in different, possibly optimized fashion, and performance may be drastically
    different between different Cell subclasses for a given set of data.
    """
    # The parent of this cell
    parent = Instance(AbstractDataMapper)
    
    # The sort traits characterizes the internal points list.
    _sort_order = Delegate('parent')
    
    # _data references the actual point array.  in general, _data should be the
    # parent's _data object.  for the sake of simplicity, Cells assume
    # that _data is sorted in fashion indicated by self.sort_order.  (if this
    # doesn't hold, then each Cell would need to have its own duplicate
    # copy of sorted data.)
    data = Delegate('parent', '_data')
    
    indices = Property
    
    # shadow trait for 'indices'
    _indices = Any
    
    def add_indices(self, indices):
        "Adds a list of integer indices to the existing list of indices."
        raise NotImplementedError
    
    def get_points(self):
        """
        Returns a list of points that was previously set by set_points.
        This might be large and expensive; in general, get_indices() should
        be used instead.
        """
        raise NotImplementedError
    
    def reverse_indices(self):
        """
        Tells the Cell to manipulate its indices so that they index to the same
        values in a reversed _data array.  Generally this handles when the
        parent's _data array has been flipped due to a sort_order change.
        
        The length of _data must not have changed, or else there is no way to
        know the proper way to manipulate indices.
        """
        raise NotImplementedError
    
    def _set_indices(self, indices):
        raise NotImplementedError
    
    def _get_indices(self):
        """
        Returns the list of indices into _data that reflect the points 
        inside this cell.
        """
        raise NotImplementedError


class Cell(AbstractCell):
    """
    A basic Cell that just stores its point indices as an array of integers.
    """
    # Redefine the property from the base class
    indices = Property(Array)
    
    # a 1-D array of indices into _data.
    _indices = Array
    
    def __init__(self, **kw):
        self._indices = array([])
        super(AbstractCell, self).__init__(**kw)
    
    def add_indices(self, indices):
        self._indices = concatenate([self._indices, indices])
        return
    
    def get_points(self):
        return take(self.data, self._indices)

    def reverse_indices(self):
        length = len(self.data)
        self._indices = [length-i-1 for i in self._indices]
        return

    def _set_indices(self, indices):
        self._indices = indices
        return
    
    def _get_indices(self):
        return self._indices



class RangedCell(AbstractCell):
    """
    A cell optimized for storing lists of continuous points.  Rather than storing
    each individual point index as an element in an array, RangedCell stores
    a list of index ranges (each a (start,end) tuple).
    """
    
    # Redefine the property from the base class
    indices = Property

    # Don't use the _indices shadow trait; rather, the getters and setters
    # for 'index' procedurally generate indices from the 'ranges'.
    _indices = Disallow
    
    # Ranges are an additional interface on RangedCells.
    ranges = Property(List(Tuple))
    
    # shadow trait
    _ranges = List(Tuple)
    
    #---------------------------------------------------------------------
    # AbstractCell methods
    #---------------------------------------------------------------------

    def add_indices(self, indices):
        self.add_ranges(find_runs(indices))
        return
    
    def get_points(self):
        return take(self.data, self.indices)
    
    def reverse_indices(self):
        length = len(self.data)
        self._ranges = [(length-end-1, length-start-1) for (start,end) in self._ranges]
        return
    
    def _set_indices(self, indices):
        self._ranges = find_runs(indices)
        return

    def _get_indices(self):
        list_of_indices = [range(i,j) for (i,j) in self._ranges]
        return sum(list_of_indices, [])


    #---------------------------------------------------------------------
    # additional RangedCell methods
    #---------------------------------------------------------------------
    
    def get_ranges(self):
        """
        Returns a list of tuples representing the (start,end) indices of
        continuous ranges of points in self._data.
        """
        return self._ranges()
    
    def add_ranges(self, ranges):
        """
        Adds a list of ranges ((start,end) tuples) to the current list
        
        This doesn't check for duplicate or overlapping ranges.
        """
        if self._ranges:
            self._ranges.extend(ranges)
        else:
            self._ranges = ranges
        return
#EOF
