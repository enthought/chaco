cimport cython

from libc.math cimport isnan, fabs, floor, INFINITY

from numpy import empty, inf



@cython.boundscheck(False)
def lttb(double[:, :] points not None, Py_ssize_t n_buckets):
    """ Apply the largest triangle three buckets algorithm to data points

    Parameters
    ----------
    points : N, 2 array of float
        The points as a N by 2 array of floats.  The index values (column 0)
        must be monotone.
    n_buckets : int
        The number of buckets.

    Returns
    -------
    index, values : array, array
        The downsampled index and values.

    References
    ----------

    Sveinn Steinarsson, "Down Sampling Time Series for Visual Representation,"
    Master's Thesis, University of Iceland, 2013.
    http://skemman.is/handle/1946/15343
    """
    cdef Py_ssize_t data_length = points.shape[0]
    cdef Py_ssize_t a = 0
    cdef Py_ssize_t sampled_index = 0
    cdef double max_area, area, avg_x, avg_y, a_x, a_y, baseline, height, bucket_size
    cdef Py_ssize_t max_area_index, next_a, i, j, k, count
    cdef double[:, :] sampled = empty(shape=(n_buckets, 2), dtype=float)

    cdef Py_ssize_t current_bucket_start, current_bucket_end, next_bucket_end

    with nogil:
        sampled[sampled_index, 0] = points[a, 0]
        sampled[sampled_index, 1] = points[a, 1]
        sampled_index += 1

        bucket_size = (data_length - 2.0)/(n_buckets - 2.0)
        current_bucket_start = 1
        current_bucket_end = <Py_ssize_t>bucket_size + 1

        for i in range(n_buckets-2):
            # find the average values of the next bucket
            avg_x = 0.0
            avg_y = 0.0
            count = 0
            next_bucket_end = <Py_ssize_t>((i+2)*bucket_size) + 1
            if next_bucket_end > data_length:
                next_bucket_end = data_length

            for j in range(current_bucket_end, next_bucket_end):
                count += 1
                avg_x += (points[j, 0] - avg_x)/count
                avg_y += (points[j, 1] - avg_y)/count
                j += 1

            # find maximum triangle area in current bucket
            max_area = -INFINITY
            area = -INFINITY
            a_x = points[a, 0]
            a_y = points[a, 1]
            baseline = (a_x - avg_x)
            height = (avg_y - a_y)

            for k in range(current_bucket_start, current_bucket_end):
                area = fabs(baseline * (points[k, 1] - a_y) -
                        (a_x - points[k, 0]) * height)/2
                if area > max_area:
                    max_area = area
                    next_a = k
                    sampled[sampled_index, 0] = points[k, 0]
                    sampled[sampled_index, 1] = points[k, 1]

            a = next_a
            current_bucket_start = current_bucket_end
            current_bucket_end = next_bucket_end

            sampled_index += 1

            skipped = 0

        sampled[-1, 0] = points[-1, 0]
        sampled[-1, 1] = points[-1, 1]

    return sampled
