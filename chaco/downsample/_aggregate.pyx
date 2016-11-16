import numpy as np

cimport cython
cimport numpy as np
from libc.math cimport isnan

cdef double nan = float('nan')
cdef double infinity = float('inf')
cdef double negative_infinity = -float('inf')


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def reduce_slices_2d_float(np.ndarray[double, ndim=2] a,
                           np.ndarray[Py_ssize_t, ndim=2] i_slices,
                           np.ndarray[Py_ssize_t, ndim=2] j_slices,
                           object aggregator):
    """ Reduce specified slices with aggregation function """

    # extra sanity checks
    if i_slices.shape[1] != 2:
        msg = "Slices on axis 0 must have shape Nx2, got {}"
        raise ValueError(msg.format(i_slices.shape[1]))
    if j_slices.shape[1] != 2:
        msg = "Slices on axis 1 must have shape Nx2, got {}"
        raise ValueError(msg.format(j_slices.shape[1]))

    # set up
    cdef Py_ssize_t i, i_start, i_end, j, j_start, j_end, k, l
    cdef Py_ssize_t n = i_slices.shape[0]
    cdef Py_ssize_t m = j_slices.shape[0]
    cdef double x
    cdef double delta
    cdef np.ndarray[double, ndim=2] result, mean
    cdef np.ndarray[np.uint64_t, ndim=2] count

    if isinstance(aggregator, str):
        i_start = i_slices[0, 0]
        i_end = i_slices[n-1, 1]
        j_start = j_slices[0, 0]
        j_end = j_slices[m-1, 1]

        if aggregator == "count":
            count = np.zeros((n, m), dtype='uint64')
            with nogil:
                k = 0
                for i in range(i_start, i_end):
                    while i >= i_slices[k, 1]:
                        k += 1
                    l = 0
                    for j in range(j_start, j_end):
                        while j >= j_slices[l, 1]:
                            l += 1
                        x = a[i, j]
                        if not isnan(x):
                            count[k, l] += 1
            return count
        elif aggregator == "min":
            result = np.empty((n, m), dtype='float')
            with nogil:
                for k in range(n):
                    for l in range(m):
                        result[k, l] = infinity
                k = 0
                for i in range(i_start, i_end):
                    while i >= i_slices[k, 1]:
                        k += 1
                    l = 0
                    for j in range(j_start, j_end):
                        while j >= j_slices[l, 1]:
                            l += 1
                        x = a[i, j]
                        if x < result[k, l]:
                            result[k, l] = x
            return result
        elif aggregator == "max":
            result = np.empty((n, m), dtype='float')
            with nogil:
                for k in range(n):
                    for l in range(m):
                        result[k, l] = negative_infinity
                k = 0
                for i in range(i_start, i_end):
                    while i >= i_slices[k, 1]:
                        k += 1
                    l = 0
                    for j in range(j_start, j_end):
                        while j >= j_slices[l, 1]:
                            l += 1
                        x = a[i, j]
                        if x > result[k, l]:
                            result[k, l] = x
            return result
        elif aggregator == "sum":
            result = np.zeros((n, m), dtype='float')
            with nogil:
                k = 0
                for i in range(i_start, i_end):
                    while i >= i_slices[k, 1]:
                        k += 1
                    l = 0
                    for j in range(j_start, j_end):
                        while j >= j_slices[l, 1]:
                            l += 1
                        x = a[i, j]
                        if not isnan(x):
                            result[k, l] += x
            return result
        elif aggregator == "mean":
            result = np.zeros((n, m), dtype='float')
            count = np.zeros((n, m), dtype='uint64')
            with nogil:
                # this is slow because we are using numerically stable mean
                k = 0
                for i in range(i_start, i_end):
                    while i >= i_slices[k, 1]:
                        k += 1
                    l = 0
                    for j in range(j_start, j_end):
                        while j >= j_slices[l, 1]:
                            l += 1
                        x = a[i, j]
                        if not isnan(x):
                            count[k, l] += 1
                            result[k, l] += (x - result[k, l])/count[k, l]
                # anywhere count is 0, mean is undefined
                for k in range(n):
                    for l in range(m):
                        if count[k, l] == 0:
                            result[k, l] = nan
        elif aggregator == "fast_mean":
            result = np.zeros((n, m), dtype='float')
            count = np.zeros((n, m), dtype='uint64')
            with nogil:
                k = 0
                for i in range(i_start, i_end):
                    while i >= i_slices[k, 1]:
                        k += 1
                    l = 0
                    for j in range(j_start, j_end):
                        while j >= j_slices[l, 1]:
                            l += 1
                        x = a[i, j]
                        if not isnan(x):
                            count[k, l] += 1
                            result[k, l] += x
                # anywhere count is 0, mean is undefined
                for k in range(n):
                    for l in range(m):
                        if count[k, l] == 0:
                            result[k, l] = nan
                        else:
                            result[k, l] /= count[k, l]
        elif aggregator == "variance":
            result = np.zeros((n, m), dtype='float')
            mean = np.zeros((n, m), dtype='uint64')
            count = np.zeros((n, m), dtype='uint64')
            with nogil:
                k = 0
                for i in range(i_start, i_end):
                    while i >= i_slices[k, 1]:
                        k += 1
                    l = 0
                    for j in range(j_start, j_end):
                        while j >= j_slices[l, 1]:
                            l += 1
                        x = a[i, j]
                        if not isnan(x):
                            count[k, l] += 1
                            delta = x - mean[k, l]
                            mean[k, l] += delta/count[k, l]
                            result[k, l] += delta*(x - mean[k, l])
                # anywhere count is <=1, variance is undefined
                for k in range(n):
                    for l in range(m):
                        if count[k, l] <= 1:
                            result[k, l] = nan
                        else:
                            result[k, l] = result[k, l]/(count[k, l] - 1)
            return result
        elif aggregator == "fast_variance":
            result = np.zeros((n, m), dtype='float')
            mean = np.zeros((n, m), dtype='uint64')
            count = np.zeros((n, m), dtype='uint64')
            with nogil:
                k = 0
                for i in range(i_start, i_end):
                    while i >= i_slices[k, 1]:
                        k += 1
                    l = 0
                    for j in range(j_start, j_end):
                        while j >= j_slices[l, 1]:
                            l += 1
                        x = a[i, j]
                        if not isnan(x):
                            count[k, l] += 1
                            mean[k, l] += x
                            result[k, l] += x**2
                # anywhere count is <=1, variance is undefined
                for k in range(n):
                    for l in range(m):
                        if count[k, l] <= 1:
                            result[k, l] = nan
                        else:
                            result[k, l] = (result[k, l] -
                                            mean[k, l]/count[k, l])/(count[k, l] - 1)
            return result
        else:
            # TODO: can implement standard deviation in this way too
            msg = "Unknown aggregator: {}"
            raise ValueError(msg.format(repr(aggregator)))
    else:
        # Using a custom aggregator.  Slow.
        result = np.empty((n, m), dtype='float')
        for i in range(n):
            i_start = i_slices[i, 0]
            i_end = i_slices[i, 1]
            for j in range(m):
                j_start = j_slices[i, 0]
                j_end = j_slices[i, 1]
                result[i, j] = aggregator(a, i_start, i_end, j_start, j_end)

    return result
