import sys
import numpy as np
cimport numpy as np

cimport cython

if sys.platform == 'win32':
    cdef extern from "float.h":
        int _isnan(float)
    isnan = _isnan
else:
    cdef extern from "math.h":
        int isnan(float)



# Inline max and min functions used below
cdef inline float float_max(float a, float b): 
    return a if a >= b else b

cdef inline float float_min(float a, float b): 
    return a if a <= b else b

@cython.wraparound(False)
@cython.boundscheck(False)
def map_colors(
        data_array not None,
        int steps,
        float low,
        float high,
        np.ndarray[np.float32_t] red_lut not None,
        np.ndarray[np.float32_t] green_lut not None,
        np.ndarray[np.float32_t] blue_lut not None,
        np.ndarray[np.float32_t] alpha_lut not None
        ):
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
        of this array is equal to data_array.shape + (4,).

    '''
    shape = data_array.shape + (4,)
    cdef int i, idx, N = data_array.size
    cdef float norm_value, range_diff, red, green, blue, alpha
    cdef np.ndarray[np.float32_t, ndim=2] rgba = np.empty((N,4), np.float32)

    range_diff = high - low

    # Handle null range, or infinite range (which can happen during 
    # initialization before range is connected to a data source).
    if range_diff == 0.0 or np.isinf(range_diff):
        idx = (steps - 1) / 2
        # Pull these out here to avoid N lookups
        red = red_lut[idx]
        green = green_lut[idx]
        blue = blue_lut[idx]
        alpha = alpha_lut[idx]
        for i in range(N):
            rgba[i,0] = red
            rgba[i,1] = green
            rgba[i,2] = blue
            rgba[i,3] = alpha
        return rgba.reshape(shape)

    # Copy the data into a float32 array so we can use fast iteration. We use
    # part of the rgba array for this to save memory.
    cdef np.ndarray[np.float32_t] norm_data = rgba[:,0]
    norm_data[:] = data_array.flat

    for i in range(N):
        if isnan(norm_data[i]):
            rgba[i,0] = 0
            rgba[i,1] = 0
            rgba[i,2] = 0
            rgba[i,3] = 0
        else:
            norm_value = (norm_data[i] - low) / range_diff
            if norm_value > 1:
                idx = steps - 1
            elif norm_value < 0:
                idx = 0
            else:
                idx = <int> ((steps - 1) * norm_value)

            rgba[i,0] = red_lut[idx]
            rgba[i,1] = green_lut[idx]
            rgba[i,2] = blue_lut[idx]
            rgba[i,3] = alpha_lut[idx]

    return rgba.reshape(shape)


@cython.wraparound(False)
@cython.boundscheck(False)
def apply_selection_fade(
        np.ndarray[np.uint8_t, ndim=3] mapped_image not None,
        mask, fade_alpha, fade_background):
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
    cdef float ialpha = (1.0 - fade_alpha)
    ialpha = max(0.0, min(1.0, ialpha))

    cdef float bg_r, bg_g, bg_b
    bg_r = ialpha * fade_background[0]
    bg_r = float_max(0.0, float_min(255.0, bg_r))
    bg_g = ialpha * fade_background[1]
    bg_g = float_max(0.0, float_min(255.0, bg_g))
    bg_b = ialpha * fade_background[2]
    bg_b = float_max(0.0, float_min(255.0, bg_b))

    cdef int N = mapped_image.shape[0]
    cdef int M = mapped_image.shape[1]
    cdef int i, j

    # Precompute new lookup tables. This is a win when the N*M >> 3*256,
    # which is usually the case.
    cdef np.ndarray[np.uint8_t] red_lut = np.empty(256, np.uint8)
    cdef np.ndarray[np.uint8_t] green_lut = np.empty(256, np.uint8)
    cdef np.ndarray[np.uint8_t] blue_lut = np.empty(256, np.uint8)
    cdef float red, green, blue, fade

    for i in range(256):
        fade = fade_alpha * i

        red = fade + bg_r
        red = float_max(0.0, float_min(255.0, red))
        red_lut[i] = <np.uint8_t> red

        green = fade + bg_g
        green = float_max(0.0, float_min(255.0, green))
        green_lut[i] = <np.uint8_t> green

        blue = fade + bg_b
        blue = float_max(0.0, float_min(255.0, blue))
        blue_lut[i] = <np.uint8_t> blue

    # View the mask as a uint8 so we can benefit from fast lookup. We
    # would use bools, but these are not well supported. We do this here
    # so that the caller doesn't have to deal with it.
    cdef np.ndarray[np.uint8_t, ndim=2] i8mask = mask.view(np.uint8)


    for i in range(N):
        for j in range(M):
            if i8mask[i, j]:
                continue

            mapped_image[i, j, 0] = red_lut[mapped_image[i, j, 0]]
            mapped_image[i, j, 1] = green_lut[mapped_image[i, j, 1]]
            mapped_image[i, j, 2] = blue_lut[mapped_image[i, j, 2]]
