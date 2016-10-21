import logging

logger = logging.getLogger(__name__)


try:
    from chaco.downsample import _lttb
except ImportError:
    _lttb = None
    logger.warning(
        "Can't import _lttb extension module, lttb downsampling will not work."
    )


def largest_triangle_three_buckets(points, n_buckets):
    """ Apply the largest triangle three buckets algorithm to data points

    This function assumes that all values are finite and the index values are
    monotone increasing.

    Parameters
    ----------
    points : N, 2 array of float
        The points as a N by 2 array of floats.  The index values (column 0)
        must be monotone increasing.
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
    if n_buckets > points.shape[0] or n_buckets <= 2:
        return points

    if _lttb is not None:
        return _lttb.lttb(points, n_buckets)
    else:
        # can't downsample, do nothing, but better than crashing
        return points
