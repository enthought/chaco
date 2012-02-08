import numpy as np
cimport numpy as np

cimport cython

cdef extern from "math.h":
    int isnan(float)

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
        of this array is equal to data_array.shape + (,4).

    '''
    shape = data_array.shape + (4,)
    cdef int i, idx, N = data_array.size
    cdef float norm_value, range_diff = high - low
    cdef np.ndarray[np.float32_t, ndim=2] rgba = np.empty((N,4), np.float32)

    # Handle null range, or infinite range (which can happen during 
    # initialization before range is connected to a data source).
    if range_diff == 0.0 or np.isinf(range_diff):
        idx = (steps - 1) / 2
        for i in range(N):
            rgba[i,0] = red_lut[idx]
            rgba[i,1] = green_lut[idx]
            rgba[i,2] = blue_lut[idx]
            rgba[i,3] = alpha_lut[idx]
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
    cdef int N = mapped_image.shape[0]
    cdef int M = mapped_image.shape[1]
    cdef int i, j

    cdef float bg_r, bg_g, bg_b
    bg_r = ialpha * fade_background[0]
    bg_g = ialpha * fade_background[1]
    bg_b = ialpha * fade_background[2]

    cdef np.ndarray[np.uint8_t, ndim=2] i8mask = mask.view(np.uint8)

    for i in range(N):
        for j in range(M):
            if i8mask[i, j]:
                continue

            mapped_image[i, j, 0] = \
                    <unsigned int>  (fade_alpha * mapped_image[i, j, 0] + bg_r)
            mapped_image[i, j, 1] = \
                    <unsigned int>  (fade_alpha * mapped_image[i, j, 1] + bg_g)
            mapped_image[i, j, 2] = \
                    <unsigned int>  (fade_alpha * mapped_image[i, j, 2] + bg_b)
