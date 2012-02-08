"""
Module that implements pure-python equivalents of the functions in the
_speedups extension module.
"""

from numpy import clip, invert, isnan, isinf, array, transpose, zeros, \
    compress, where, take, float32, ones_like
import numpy as np

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
       Array of indexes of the points
    index_low : float or None
       The minimum acceptable value in the index array
    index_high : float or None
       The maximum acceptable value in the index array
    value : float array (1D)
       Array of values of the points
    value_low : float or None
       The minimum acceptable value in the value array
    value_high : float or None
       The maximum acceptable value in the value array

    Optional Parameters
    -------------------
    index_mask : bool or int array (1D)
      Mask array for the indexes
    index_sel : sequence of ints
       A list/tuple/array of indices of selected positions in the index array
    index_sel_mask : array of ints or bools
       An mask array with True values indicating which points are selected
    value_mask : bool or int array (1D)
       Mask array for the values
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



def apply_selection_fade(mapped_image, mask, fade_alpha, fade_background):
    '''Apply a selection fade to a colormapped image.

    Parameters
    ----------
    mapped_image : ndarray of uint8, shape (N,M,4)
        The digitized rgba values
    mask : ndarray of bool, shape (N,M,4)
        The array of masked pixels
    fade_alpha : float
        The alpha value for the fade
    fade_background : rgb888 tuple
        The fade background

    '''
    imask = invert(mask)
    if fade_alpha == 0:
        mapped_image[imask,0:3] = fade_background
    else:
        ialpha = (1.0 - fade_alpha)
        background = tuple(ialpha * x for x in fade_background)
        image_region = mapped_image[imask,0:3]
        image_region *= fade_alpha
        image_region += background
        mapped_image[imask,0:3] = image_region


def map_colors(data_array, steps, low, high, red_lut, green_lut, blue_lut,
        alpha_lut):
    '''Map colors from color lookup tables to a data array.

    This is used in ColorMapper.map_screen

    Parameters
    ----------
    data_array : ndarray
        The data array
    steps: int
        The number of steps in the color map (depth)
    low : float
        The low end of the data range
    high : float
        The high end of the data range
    red_lut : ndarray of float32
        The red channel lookup table
    green_lut : ndarray of float32
        The green channel lookup table
    blue_lut : ndarray of float32
        The blue channel lookup table
    alpha_lut : ndarray of float32
        The alpha channel lookup table
    
    Returns
    -------
    rgba: ndarray of float32
        The rgba values of data_array according to the lookup tables. The shape
        of this array is equal to data_array.shape + (,4).

    '''
    range_diff = high - low

    if range_diff == 0.0 or isinf(range_diff):
        # Handle null range, or infinite range (which can happen during 
        # initialization before range is connected to a data source).
        norm_data = 0.5*ones_like(data_array)
    else:
        norm_data = clip((data_array - low) / range_diff, 0.0, 1.0)


    nanmask = isnan(norm_data)
    norm_data = where(nanmask, 0, (norm_data * (steps-1)).astype(int))
    rgba = zeros(norm_data.shape+(4,), float32)
    rgba[...,0] = where(nanmask, 0, take(red_lut, norm_data))
    rgba[...,1] = where(nanmask, 0, take(green_lut, norm_data))
    rgba[...,2] = where(nanmask, 0, take(blue_lut, norm_data))
    rgba[...,3] = where(nanmask, 0, take(alpha_lut, norm_data))

    return rgba

