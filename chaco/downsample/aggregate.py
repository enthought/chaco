from numpy import array


def reduceat1d(a, slices, agg):
    """ Slice values from a at indices and aggregate according to function

    Assume that i is monotone increasing.
    """
    return array([agg(a[i:j]) for i, j in slices])


def reduceat2d(a, slices, agg):
    """ Slice values from a at indices and aggregate according to function

    Assume that i is monotone increasing.
    """
    return array([[agg(a[i0:j0, i1:j1]) for i1, j1 in slices[1]]
                   for i0, j0 in slices[0]])
