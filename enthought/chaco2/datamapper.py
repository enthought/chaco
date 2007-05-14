"""
WARNING!!!

This is an older file from chaco classic to support the spatial subdivision 
structures.  It will be refactored soon.

If you are looking for Chaco2's mappers (subclasses of AbstractMapper),
look in abstract_mapper.py, linear_mapper.py, and log_mapper.py.
"""


from sets import Set

from numpy import array, concatenate, take, argsort, argmin, \
                  argmax, transpose, newaxis, sort

from enthought.traits.api import HasStrictTraits, Bool, Enum, Tuple, \
                             Property, Any, Float


#-------------------------------------------------------------------
# Module-specific traits
#-------------------------------------------------------------------

# Expresses sorting order of 
ArraySortTrait = Enum('ascending', 'descending')


#-------------------------------------------------------------------
# Module-specific utility functions
#-------------------------------------------------------------------

def right_shift(ary, newval):
    "Returns a right-shifted version of ary with newval inserted on the left."
    return concatenate([[newval], ary[:-1]])

def left_shift(ary, newval):
    "Returns a left-shifted version of ary with newval inserted on the right."
    return concatenate([ary[1:], [newval]])

def sort_points(points, index=0):
    """
    sort_points(array_of_points, index=<0|1>) -> sorted_array
    
    Takes a list of points as an Nx2 array and sorts them according
    to their x or y coordinate.  (index=0 => x)
    """
    if len(points.shape) != 2 or (2 not in points.shape):
        raise RuntimeError, "sort_points(): Array of wrong shape."
    return take( points, argsort(points[:,index]) )

def concat_point_arrays(list_of_arrays):
    """
    concat_point_arrays(list_of_point_arrays) -> point_array (Nx2)
    list_of_point_arrays should be a standard python list-like object
    with Nx2 arrays inside it.
    
    Example::
        
        concat_point_arrays( [array([[0,0], [1,1]]), array([[2,2], [3,3]])] )
        
    Returns::
        
        array([ [0,0], [1,1], [2,2], [3,3] ])
    """
    # shortcut if list is length 1
    if len(list_of_arrays) == 1:
        return list_of_arrays[0]
    else:
        ravelled = [ravel(x) for x in list_of_arrays]
        return resize(concatenate(ravelled), (len(ravelled)/2, 2))

def array_zip(*arys):
    """
    Returns a Numeric array that is the concatenation of the input 1D
    arys along a newaxis.  Basically equivalent to ``array(zip(*arys))``,
    but should be more resource-efficient.
    """
    return transpose(array(arys))


class AbstractDataMapper(HasStrictTraits):
    """
    A data mapper maps from coordinate space to data elements.  In its most
    basic form, it loops over all the available data points to find the ones
    near a given coordinate or within an area.  More advanced functionality
    includes returning rect-aligned "affected regions" enclosing all the
    returned points, etc.
    """
    
    # How to sort the output list of intersected points that the
    # get_points_near_*() function return.  The points are always sorted
    # by their domain (first/X-value) coordinate.
    sort_order = ArraySortTrait

    # A read-only property that describes the origin and size of the data
    # set in data space as a 4-tuple (min_x, min_y, width, height)
    extents = Property()
    
    
    #-------------------------------------------------------------------
    # Private traits
    #-------------------------------------------------------------------
    
    _data = Any
    
    # Internally we expect Nx2 arrays; if the user hands in something
    # different, we stored a transposed version but always remember to
    # transpose once again whenever we return data.
    _is_transposed = Bool(False)

    # the max and min points in data space expressed as a 4-tuple (x,y,w,h)
    _extents = Tuple
    
    # a "fudge factor" to make the extents slightly larger than the actual
    # values in the data set
    _extents_delta = Float(0.1)
    
    def __init__(self, data=None, data_sorting='none', **kw):
        "See set_data() for description."
        self._data = array([])
        HasStrictTraits.__init__(self, **kw)
        if data is not None:
            self.set_data(data, data_sorting)
        return
    
    def get_points_near(self, pointlist, radius=0.0):
        """
        get_points_near([points], radius=0.0) -> Nx2 array of candidate points
        
        Returns a list of points near the input points (Nx2 array).
        
        For each point in the input set, the radius is used to create a
        conceptual circle; if any points in the DataMapper's values lie insie
        this circle, they will be returned.

        The returned list is not guaranteed to be a minimum or exact set,
        but it is guaranteed to contain all points that intersect the input
        pointlist.  The caller still needs to do fine-grained testing to see
        if the points in the pointlist are a match.
        """
        raise NotImplementedError

    def get_points_near_polyline(self, line):
        """
        get_points_near_polyline([v1, ... vN]) -> [ [points], [points], ... ]
        
        Like get_points_near(), except takes a polyline as input.  A polyline
        is a list of vertices, each connected to the next by a straight line.
        The polyline has infinitely thin width.  
        
        The input array can have shape 2xN or Nx2.
        """
        raise NotImplementedError
    
    def get_points_in_rect(self, rect):
        """
        get_points_in_rect( (x,y,w,h) ) -> [ [points], [points], ... ]
        
        Like get_points_near(), except takes a rectangle as input.  The
        rectangle has infinitely thin width.
        """
        raise NotImplementedError
    
    def get_points_in_poly(self, poly):
        """
        get_points_in_poly([v1, ... vN]) -> [ [points], [points], ... ]
        
        Like get_points_near(), except takes a polygon as input.  The 
        polygon has infinitely thin width and can be self-intersecting
        and concave.
        
        The input array can have shape 2xN or Nx2.
        """
        raise NotImplementedError

    def get_last_region(self):
        """
        Returns a region of screen space that contains all of the
        points/lines/rect/polys in the last get_points_in_* call.  The
        returned region is guaranteed to only contain the points that
        were returned.
        
        The region is returned as a list of (possibly disjoint) rectangles,
        where each rectangle is a 4-tuple (x,y,w,h).
        """
        raise NotImplementedError
    
    def set_data(self, new_data, new_data_sorting='none'):
        """
        set_data(new_data, new_data_sorting='none')
        
        Sets the data used by this DataMapper.  new_data_sorting indicates
        how the new data is sorted: 'none', 'ascending', or 'descending'.
        The default is 'none', which will cause the data mapper to perform
        a full sort of the input data.
        
        The input data can be shaped 2xN or Nx2.
        """
        if len(new_data) == 0:
            self.clear()
            return
        
        if new_data.shape[0] == 2:
            self._is_transposed = True
            self._data = transpose(new_data)
        else:
            self._is_transposed = False
            self._data = new_data
        
        if new_data_sorting == 'none':
            if self.sort_order == 'ascending':
                self._data = sort_points(self._data)
            else:
                self._data = sort_points(self._data)[::-1]
        elif new_data_sorting != self.sort_order:
            self._data = self._data[::-1]

        self._calc_data_extents()
        self._update_datamap()
        # a re-sorting is unnecessary because any internal data structures
        # will have been updated by the _data update process.
        return

    def clear(self):
        """
        clear()
        
        Resets internal state and any cached data to reflect an empty
        data set/data space.
        """
        self._data = None
        self._extents = (0,0,0,0)
        self._clear()
        return

    def get_data(self):
        "Returns the actual data used by the DataMapper."
        if self._is_transposed:
            return transpose(self._data)
        else:
            return self._data

    #-------------------------------------------------------------------
    # Concrete private methods and event handlers
    # Child classes shouldn't have to override these.
    #-------------------------------------------------------------------
    
    def _get_extents(self):
        return self._extents
    
    def _calc_data_extents(self):
        """
        Computes ((minX, minY), (width, height)) of self._data; sets self._extent and
        returns nothing.
        """
        if len(self._data) == 0:
            self._extents = ((0,0), (0,0))
        else:
            value = self._data
            min_indices = argmin(value, axis=0)
            max_indices = argmax(value, axis=0)
            x = value[min_indices[0], 0] - self._extents_delta
            y = value[min_indices[1], 1] - self._extents_delta
            maxX = value[max_indices[0], 0] + self._extents_delta
            maxY = value[max_indices[1], 1] + self._extents_delta
            self._extents = ((x, y), (maxX-x, maxY-y))
        return


    #-------------------------------------------------------------------
    # Abstract private methods and event handlers
    #-------------------------------------------------------------------
    
    def _update_datamap(self):
        """
        This function gets called after self._data has changed.  Child classes
        should implement this function if they need to recompute any cached
        data structures, etc.
        """
        return
    
    def _clear(self):
        "Performs subclass-specific clearing/cleanup."
        return

    def _sort_order_changed(self, old, new):
        return


class BruteForceDataMapper(AbstractDataMapper):
    """
    The BruteForceDataMapper just returns all the points, all the time.
    This is basically the same behavior as not having a data mapper in
    the pipeline at all.
    """
    
    def get_points_near(self, pointlist, radius=0):
        return self.get_data()
        
    def get_points_near_polyline(self, line):
        return self.get_data()
        
    def get_points_in_rect(self, rect):
        return self.get_data()
    
    def get_points_in_poly(self, poly):
        return self.get_data()

    def get_last_region(self):
        return self._extents

    def _sort_order_changed(self, old, new):
        if len(self._data) == 0:
            return
        else:
            if self.sort_order == 'ascending':
                self._data = sort_points(self._data)
            else:
                self._data = sort_points(self._data)[::-1]
        return

#EOF
