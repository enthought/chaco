
# imports
from numpy import *
from enthought.chaco2.shell import *
from enthought.chaco2.default_colormaps import *

# Create some data
x = linspace(1, 15, 200)

# Create some line plots
loglog(x, x**2, "b-.", name="y=x**2", bgcolor="white")
hold(True)
loglog(x, x**4+3*x+2, "r-", name="y=x**4+3x+2", bgcolor="white")
loglog(x, exp(x), "g-", name="y=exp(x)", bgcolor="white")
loglog(x, x, "m--", name="y=x", bgcolor="white")

# Add some titles
title("simple loglog plots")

#This command is only necessary if running from command line
show()
