""" The base ScatterPlot class now accepts variable sized markers.

This definition remains for backwards compatibility.
"""
import warnings

warnings.warn(
    "VariableSizeScatterPlot has been deprecated. Use the base ScatterPlot "
    "class which now accepts variable sized markers",
    DeprecationWarning
)

from .scatterplot import ScatterPlot


# TODO: This should be officially deprecated.
class VariableSizeScatterPlot(ScatterPlot):
    pass
