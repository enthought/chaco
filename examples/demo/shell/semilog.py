"""
This example shows how to create a semi-log plot using the `shell` package.
"""

# Major library imports
from numpy import linspace, exp

# Enthought library imports
from chaco.shell import semilogy, hold, title, show


# Create some data
x = linspace(1, 10, 200)

# Create some line plots
semilogy(x, exp(x), "b-", name="y=exp(x)", bgcolor="white")
hold(True)
semilogy(x, x**x, "r--", name="y=x**x")
semilogy(x, x, "g-", name="y=x")

# Add some titles
title("simple semilog plots")

# This command is only necessary if running from command line
show()

