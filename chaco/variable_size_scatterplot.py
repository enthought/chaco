""" The base ScatterPlot class now accepts variable sized markers.

This definition remains for backwards compatibility.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from chaco.scatterplot import ScatterPlot


# TODO: This should be officially deprecated.
class VariableSizeScatterPlot(ScatterPlot):
    pass
