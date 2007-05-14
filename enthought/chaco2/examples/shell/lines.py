
# imports
from numpy import *
from enthought.chaco2.shell import *
from enthought.chaco2.default_colormaps import *

# Create some data
x = linspace(-2*pi, 2*pi, 100)
y1 = sin(x)
y2 = cos(x)

# Create some line plots
plot(x, y1, "b-", bgcolor="white")
hold()
plot(x, y2, "g-.", marker_size=2)

# Add some titles
title("simple line plots")

#This command is only necessary if running from command line
show()

