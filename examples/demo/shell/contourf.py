"""
This example demonstrates creating a filled contour plot using the chaco
shell subpackage.
"""

# Major library Imports
from numpy import linspace, meshgrid, tanh

# Enthought Library Imports
from chaco.shell import contourf, colormap, title, show
from chaco.default_colormaps import viridis


# Crate some scalar data
xs = linspace(-10,10,200)
ys = linspace(-10,10,400)
x, y = meshgrid(xs,ys)
z = x * tanh(y)

# Create a filled contour plot
contourf(x,y,z)
colormap(viridis)

# Add some titles
title("filled contour plot")

# This command is only necessary if running from command line
show()
