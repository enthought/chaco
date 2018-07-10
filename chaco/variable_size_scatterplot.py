""" The base ScatterPlot class now accepts variable sized markers.

This definition remains for backwards compatibility.
"""
from .scatterplot import ScatterPlot


# TODO: This should be officially deprecated.
class VariableSizeScatterPlot(ScatterPlot):
    pass
