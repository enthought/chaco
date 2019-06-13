"""
Defines basic traits and functions for the data model.
"""

# Standard library imports
from math import radians, sqrt

# Major library imports
from numpy import (
    array, argsort, concatenate, cos, diff, dot, dtype, empty, float32,
    isfinite, nonzero, pi, searchsorted, seterr, sin, int8
)

# Enthought library imports
from traits.api import Enum, ArrayOrNone

delta = {'ascending': 1, 'descending': -1, 'flat': 0}

rgba_dtype = dtype([('r', float32), ('g', float32), ('b', float32), ('a', float32)])
point_dtype = dtype([('x', float), ('y', float)])

# Dimensions

# A single array of numbers.
NumericalSequenceTrait = ArrayOrNone()

# A sequence of pairs of numbers, i.e., an Nx2 array.
PointTrait = ArrayOrNone(shape=(None, 2))

# An NxM array of numbers or NxMxRGB(A) array of colors.
ImageTrait = ArrayOrNone()

# An 3D array of numbers of shape (Nx, Ny, Nz)
CubeTrait = ArrayOrNone(shape=(None, None, None))


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
        raise ValueError('Must have at least 3 sides in a polygon')
    rotation = radians(rot_degrees)
    theta = (pi * 2) / nsides
    return [poly_point(center, r, i*theta+rotation) for i in range(nsides)]


def bin_search(values, value, ascending):
    """ Performs a binary search of a sorted array for a specified value.

    Parameters
    ----------

    values : array
        The values being searched.

    value : float
        The value being searched for.

    ascending : -1 or 1
        This value should be 1 if the values array is ascending, or -1 if
        the values array is descending.

    Returns
    -------

    Returns the lowest position where the value can be found or where the
    array value is the last value less (greater) than the desired value.
    Returns -1 if `value` is beyond the minimum or maximum of `values`.

    """
    if ascending > 0:
        if (value < values[0]) or (value > values[-1]):
            return -1
        index = searchsorted(values, value, 'right') - 1
    else:
        if (value < values[-1]) or (value > values[0]):
            return -1
        ascending_values = values[::-1]
        index = len(values) - searchsorted(ascending_values, value, 'left') - 1
    return index


def reverse_map_1d(data, pt, sort_order, floor_only=False):
    """Returns the index of *pt* in the array *data*.

    Raises IndexError if *pt* is outside the range of values in *data*.

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
    """
    if sort_order == "ascending":
        ndx = bin_search(data, pt, 1)
    elif sort_order == "descending":
        ndx = bin_search(data, pt, -1)
    else:
        raise NotImplementedError("reverse_map_1d() requires a sorted array")

    if ndx == -1:
        raise IndexError("value outside array data range")


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
    if points.ndim != 2:
        raise RuntimeError("sort_points(): Array of wrong shape.")
    return points[argsort(points[:, index]), :]


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
    return [int_array[i:j] for (i,j) in ranges]


def arg_find_runs(int_array, order='ascending'):
    """
    Like find_runs(), but returns a list of tuples indicating the start and
    end indices of runs in the input *int_array*.
    """
    n_points = len(int_array)
    if n_points == 0:
        return []
    indices = nonzero(diff(int_array) - delta.get(order, 0))[0] + 1
    result = empty(shape=(len(indices) + 1, 2), dtype=indices.dtype)
    result[0, 0] = 0
    result[-1, 1] = n_points
    result[1:, 0] = indices
    result[:-1, 1] = indices
    return result


def arg_true_runs(bool_array):
    """ Find runs where array is True """
    if len(bool_array) == 0:
        return []
    runs = arg_find_runs(bool_array.view(int8), 'flat')
    # runs have to alternate true and false
    if bool_array[0]:
        # even runs are true
        return runs[::2]
    elif len(runs) >= 2:
        # odd runs are true
        return runs[1::2]
    else:
        # array is all False
        return []



def point_line_distance(pt, p1, p2):
    """ Returns the perpendicular distance between *pt* and the line segment
    between the points *p1* and *p2*.
    """
    v1 = array((pt[0] - p1[0], pt[1] - p1[1]))
    v2 = array((p2[0] - p1[0], p2[1] - p1[1]))
    diff = v1 - dot(v1, v2) / dot(v2, v2) * v2

    return sqrt(dot(diff,diff))


def intersect_range(x, low, high, mask=None):
    """ Discard 1D intervals outside of range, with optional mask

    This is an optimized routine for detecting which points are endpoints
    of visible segments in a 1D polyline.  An optional mask can be provided for
    points which should be excluded from consideration for other reasons
    (such as not being selected).  Returns a mask of points which are
    endpoints of intervals which potentially intersect the range.

    Parameters
    ----------
    x : 1d array
        The array of connected interval endpoints.  If the x is
        [x0, x1, x2, ...] then the intervals are
        [[x0, x1], [x1, x2], [x2, x3], ...].
    low : number
        The low end of the range.
    high : number
        The high end of the range.
    mask : 1d array of bools or None
        The mask of points to consider, or None.  If None then any non-finite
        points will be ignored.

    Returns
    -------
    mask : 1d array of bools
        A mask array of points which are endpoints of intervals which
        potentially intersect the range.
    """
    # TODO: write a fast Cython version
    # TODO: write an optimized version for ordered data
    if mask is None:
        mask = isfinite(x)

    # find relationships to range bounds
    old_err = seterr(invalid='ignore')
    try:
        not_low_x = (x >= low) & mask
        not_high_x = (x <= high) & mask
    finally:
        seterr(**old_err)

    # a point is in if it is not low and not high
    result = (not_low_x & not_high_x)

    if x.shape[0] >= 2:
        # interval intersects range if one end not low and other end not high
        interval_mask = ((not_low_x[:-1] & not_high_x[1:]) |
                         (not_high_x[:-1] & not_low_x[1:]))

        # point is also in if at least one of its interval is in
        result[1:-1] |= interval_mask[:-1] | interval_mask[1:]
        result[0] |= interval_mask[0]
        result[-1] |= interval_mask[-1]

    return result
