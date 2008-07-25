
# Mayor Library Imports
from numpy import linspace, meshgrid, tanh

# Enthought Library Imports
from enthought.chaco.shell import contourf, colormap, title, show
from enthought.chaco.default_colormaps import jet


# Crate some scalar data
xs = linspace(-10,10,200)
ys = linspace(-10,10,400) 
x, y = meshgrid(xs,ys)
z = x * tanh(y)

# Create a filled contour plot
contourf(x,y,z)
colormap(jet)

# Add some titles
title("filled contour plot")

#This command is only necessary if running from command line
show()
