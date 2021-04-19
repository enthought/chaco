""" The base ScatterPlot class now accepts variable sized markers.

This definition remains for backwards compatibility.
"""
import warnings

from .scatterplot import ScatterPlot


class VariableSizeScatterPlot(ScatterPlot):

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "VariableSizeScatterPlot has been deprecated. Use the base "
            "ScatterPlot class which now accepts variable sized markers",
            DeprecationWarning
        )
        super(VariableSizeScatterPlot, self).__init__(*args, **kwargs)
