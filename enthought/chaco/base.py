"""
Defines basic traits and functions for the data model.
"""

# Standard library imports
from math import radians, sqrt

# Major library imports
from numpy import (array, argsort, concatenate, cos, dot, empty, nonzero,
    pi, sin, take, ndarray)

# Enthought library imports
from enthought.traits.api import CArray, Enum, Trait



# Dimensions

# A single array of numbers.
NumericalSequenceTrait = Trait(None, None, CArray(value=empty(0)))

# A sequence of pairs of numbers, i.e., an Nx2 array.
PointTrait = Trait(None, None, CArray(value=empty(0)))

# An NxM array of numbers.
ImageTrait = Trait(None, None, CArray(value=empty(0)))

# An 3D array of numbers of shape (Nx, Ny, Nz)
CubeTrait = Trait(None, None, CArray(value=empty(0)))


# This enumeration lists the fundamental mathematical coordinate types that
# Chaco supports.
DimensionTrait = Enum("scalar", "point", "image", "cube")

# Linear sort order.
SortOrderTrait = Enum("ascending", "descending", "none")


#----------------------------------------------------------------------------
# Utility functions
#----------------------------------------------------------------------------

def poly_point(center, r, degrees):
    x = r * cos(degrees) + center[0]
    y = r * sin(degrees) + center[1]
    return x,y

def n_gon(center, r, nsides, rot_degrees=0):
    """ Generates the points of a regular polygon with specified center,
    radius, and number of sides.

    By default the rightmost point of the polygon is (*r*,0) but a
    rotation about the center may be specified with *rot_degrees*.
    """
    if nsides < 3:
        raise ValueError, 'Must have at least 3 sides in a polygon'
    rotation = radians(rot_degrees)
    theta = (pi * 2) / nsides
    return [poly_point(center, r, i*theta+rotation) for i in range(nsides)]


# Ripped from Chaco 1.0's plot_base.py
def bin_search(values, value, ascending):
    """
    Performs a binary search of a sorted array looking for a specified value.

    Returns the lowest position where the value can be found or where the
    array value is the last value less (greater) than the desired value.
    Returns -1 if *value* is beyond the minimum or maximum of *values*.
    """
    if ascending > 0:
        if (value < values[0]) or (value > values[-1]):
            return -1
    else:
        if (value < values[-1]) or (value > values[0]):
            return -1
    lo = 0
    hi = len( values )
    while True:
        mid  = (hi + lo) / 2
        test = cmp( values[ mid ], value ) * ascending
        if test == 0:
            return mid
        if test > 0:
            hi = mid
        else:
            lo = mid
        if lo >= (hi - 1):
            return lo

def reverse_map_1d(data, pt, sort_order, floor_only=False):
    """Returns the index of *pt* in the array *data*.

    Parameters
    ----------
    data : 1-D array
        data to search
    pt : scalar value
        value to find, which must be within the value range of *data*
    sort_order : string
        "ascending" or "descending"
    floor_only : bool
        if true, don't find "nearest" point, instead find last point
        less (greater) than pt

    Raises IndexError if *pt* is outside the range of values in *data*.
    """
    if sort_order == "ascending":
        ndx = bin_search(data, pt, 1)
    elif sort_order == "descending":
        ndx = bin_search(data, pt, -1)
    else:
        raise NotImplementedError, "reverse_map_1d() requires a sorted array"

    if ndx == -1:
        raise IndexError, "value outside array data range"


    # Now round the index to the closest matching index.  Do this
    # by determining the width (in value space) of each cell and
    # figuring out which side of the midpoint pt falls into.  Since
    # bin_search rounds down (i.e. each cell index contains the point
    # and all points up to the next cell index), we only need to look
    # at ndx+1 and not ndx-1 as well.
    last = len(data) - 1
    if ndx < last:
        if floor_only:
            return ndx
        delta = 0.5 * (data[ndx+1] - data[ndx])
        if ((sort_order == "ascending") and (pt > data[ndx] + delta)) or \
           ((sort_order == "descending") and (pt < data[ndx] + delta)):
            return ndx + 1
        else:
            return ndx
    else:
        # NB: OK floor_only is typically used with image plots, which
        # will have one extra "fencepost" so the assumption here is that
        # if we hit the last point exactly we still really want the index
        # of the previous point
        if floor_only:
            return last-1
        # If pt happened to match the value of data[last] exactly,
        # we just return it here.
        return last

# These are taken from Chaco 1.0's datamapper and subdivision_cells modules.
# TODO: Write unit tests for these!
def right_shift(ary, newval):
    "Returns a right-shifted version of *ary* with *newval* inserted on the left."
    return concatenate([[newval], ary[:-1]])

def left_shift(ary, newval):
    "Returns a left-shifted version of *ary* with *newval* inserted on the right."
    return concatenate([ary[1:], [newval]])

def sort_points(points, index=0):
    """
    sort_points(array_of_points, index=<0|1>) -> sorted_array

    Takes a list of points as an Nx2 array and sorts them according
    to their x- or y-coordinate.  If *index* is zero, the points are sorted
    on their x-coordinate.
    """
    if len(points.shape) != 2 or (2 not in points.shape):
        raise RuntimeError, "sort_points(): Array of wrong shape."
    return take( points, argsort(points[:,index]) )

def find_runs(int_array, order='ascending'):
    """
    find_runs(int_array, order=<'ascending'|'flat'|'descending'>) -> list_of_int_arrays

    Given an integer array sorted in ascending/descending order or flat order,
    returns a list of continuous runs of integers inside the list.  for example::

        find_runs([1,2,3,6,7,8,9,10,11,15])

    returns [ [1,2,3], [6,7,8,9,10,11], [15] ]
    and::

        find_runs([0,0,0,1,1,1,1,0,0,0,0], "flat")

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
    end indices of runs in the input *int_array*.
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
    rshifted = right_shift(int_array, int_array[0]-increment).view(ndarray)
    start_indices = concatenate([[0], nonzero(int_array - (rshifted+increment))[0]])
    end_indices = left_shift(start_indices, len(int_array))
    return zip(start_indices, end_indices)


def point_line_distance(pt, p1, p2):
    """ Returns the perpendicular distance between *pt* and the line segment
    between the points *p1* and *p2*.
    """
    v1 = array((pt[0] - p1[0], pt[1] - p1[1]))
    v2 = array((p2[0] - p1[0], p2[1] - p1[1]))
    diff = v1 - dot(v1, v2) / dot(v2, v2) * v2

    return sqrt(dot(diff,diff))


#EOF
