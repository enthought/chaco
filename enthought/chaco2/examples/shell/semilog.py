
# imports
from numpy import *
from enthought.chaco2.shell import *
from enthought.chaco2.default_colormaps import *

# Create some data
x = linspace(1, 10, 200)

# Create some line plots
semilogy(x, exp(x), "b-", name="y=exp(x)", bgcolor="white")
hold(True)
semilogy(x, x**x, "r--", name="y=x**x")
semilogy(x, x, "g-", name="y=x")

# Add some titles
title("simple semilog plots")

#This command is only necessary if running from command line
show()

