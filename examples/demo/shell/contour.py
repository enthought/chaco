"""
This example demonstrates creating a contour plot using the chaco
shell subpackage.
"""

# Major library imports
from numpy import linspace, meshgrid, sin
from scipy.special import jn

# Enthought library imports
from chaco.shell import show, title, contour


# Crate some scalar data
xs = linspace(-10,10,200)
ys = linspace(-10,10,400)
x,y = meshgrid(xs,ys)
z = sin(x)*x*jn(0,y)

# Create a contour line plot
contour(x,y,z, bgcolor="black")

# Add some titles
title("contour line plot")

# This command is only necessary if running from command line
show()
