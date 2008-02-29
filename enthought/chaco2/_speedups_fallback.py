"""
Module that implements pure-python equivalents of the functions in the
_speedups extension module.
"""

from numpy import invert, isnan, array, transpose, zeros, compress
import operator

def array_combine(a, b, op=operator.and_, func=lambda x: x):
    """ Returns op(func(a), func(b)) if a and b are both not None;
    if one is None, then returns func() on the non-None array;
    if both are None, then returns None.
    """
    if a is not None and b is not None:
        return op(func(a), func(b))
    elif a is not None:
        return func(a)
    elif b is not None:
        return func(b)
    else:
        return None


def scatterplot_gather_points(index, index_low, index_high,
                              value, value_low, value_high,
                              index_mask=None, index_sel=None, index_sel_mask=None,
                              value_mask=None, value_sel=None, value_sel_mask=None):
    """
    Takes index and value arrays, masks, and optional selection arrays,  
    and returns the list of points and corresponding selection mask for  
    those points.   
     
    Parameters 
    ---------- 
    index : float array (1D)  
    index_low : float or None 
       The minimum acceptable value in the index array 
    index_high : float or None  
       The maximum acceptable value in the index array 
    value : float array (1D)  
    value_low : float or None 
       The minimum acceptable value in the value array 
    value_high : float or None  
       The maximum acceptable value in the value array 
     
    Optional Parameters 
    ------------------- 
    index_mask : bool or int array (1D)  
    index_sel : sequence of ints  
       A list/tuple/array of indices of selected positions in the index array  
    index_sel_mask : array of ints or bools 
       An mask array with True values indicating which points are selected 
    value_mask : bool or int array (1D)  
    value_sel : sequence of ints  
       A list/tuple/array of indices of selected positions in the value array  
    value_sel_mask : array of ints or bools 
       An mask array with True values indicating which points are selected 
     
    Returns 
    ------- 
    points : float array (Nx2)   
       The points that match all the masking criteria  
    sel_mask : bool array (1D)   
       Mask indicating which indices in **points** are selected  
    """

    index_range_mask = (index_low < index) & (index < index_high)
    value_range_mask = (value_low < value) & (value < value_high)
    
    nan_mask = array_combine(index_mask, value_mask,
                    func = lambda x: invert(isnan(x)) & x)

    if nan_mask is not None:
        point_mask = nan_mask & index_range_mask & value_range_mask
    else:
        point_mask = index_range_mask & value_range_mask
    points = transpose(array((index, value)))

    # Handle the selection mask
    selection_mask = array_combine(index_sel_mask, value_sel_mask)

    if index_sel is None and value_sel is None:
        pass
    else:
        if index_sel is not None and value_sel is not None:
            mask2 = zeros(len(index), int)
            mask2[index_sel] = 1
            mask2[value_sel] &= 1
        elif index_sel is not None:
            mask2 = zeros(len(index), int)
            mask2[index_sel] = 1
        elif value_sel is not None:
            mask2 = zeros(len(index), int)
            mask2[value_sel] = 1
        if selection_mask is None:
            selection_mask = mask2
        else:
            selection_mask &= mask2

    points = compress(point_mask, points, axis=0)
    if selection_mask is not None:
        selections = compress(point_mask, selection_mask)
    else:
        selections = None
    return points, selections

