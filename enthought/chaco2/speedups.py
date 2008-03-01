
try:
    from numpy import asarray
    import _speedups

    def scatterplot_gather_points(index, index_low, index_high,
                                  value, value_low, value_high,
                                  index_mask=None, index_sel=None, index_sel_mask=None,
                                  value_mask=None, value_sel=None, value_sel_mask=None):
        if index_low is None:
            index_low = -inf
        if index_high is None:
            index_high = inf
        if value_low is None:
            value_low = -inf
        if value_high is None:
            value_high = inf
        if index_mask is not None:
            index_mask = asarray(index_mask, dtype=bool)
        if value_mask is not None:
            value_mask = asarray(value_mask, dtype=bool)
        if index_sel_mask is not None:
            index_sel_mask = asarray(index_sel_mask, dtype=bool)
        if value_sel_mask is not None:
            value_sel_mask = asarray(value_sel_mask, dtype=bool)

        return _speedups.scatterplot_gather_points(index, index_low, index_high,
                      value, value_low, value_high,
                      index_mask=index_mask, index_sel=index_sel, 
                      index_sel_mask=index_sel_mask,
                      value_mask=value_mask, value_sel=value_sel,
                      value_sel_mask=value_sel_mask)


except ImportError:
    from _speedups_fallback import *


