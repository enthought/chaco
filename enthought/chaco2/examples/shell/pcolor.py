
# imports
from numpy import *
from enthought.chaco2.shell import *
from enthought.chaco2.default_colormaps import *

# Crate some scalar data
xs = linspace(0,10,200); 
ys = linspace(0,20,400); 
x,y=meshgrid(xs,ys); 
z = sin(x)*y

# Create a pseudo-color-map
pcolor(x,y,z)

#change the color mapping
colormap(jet)

# Add some titles
title("pseudo colormap image plot")

#This command is only necessary if running from command line
show()
