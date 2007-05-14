
# imports
from numpy import *
from scipy.special import jn
from enthought.chaco2.shell import *
from enthought.chaco2.default_colormaps import *

# Crate some scalar data
xs = linspace(-10,10,200); 
ys = linspace(-10,10,400); 
x,y=meshgrid(xs,ys); 
z = sin(x)*x*jn(0,y)

# Create a contour line plot
contour(x,y,z, bgcolor="black")

# Add some titles
title("contour line plot")

#This command is only necessary if running from command line
show()
